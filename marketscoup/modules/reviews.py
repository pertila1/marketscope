from __future__ import annotations

from typing import Any, Dict, List
import json

from ..config import AppConfig, load_config
from ..domain.models import Establishment, ReviewItem, ReviewSummary
from ..llm.client import LlmSettings, get_llm_client, LlmError


REVIEWS_SYSTEM_PROMPT = (
    "Ты — эксперт по анализу отзывов. Используя Яндекс.Карты и 2ГИС как основные источники, "
    "найди и проанализируй отзывы о заведении. Обязательно попытайся найти и хорошее, и плохое: "
    "минимум по одному пункту каждого, в идеале по три. "
    "КРИТИЧЕСКИ ВАЖНО: в поле overall_opinion опиши РАЗВЁРНУТО (5–8 предложений) все особенности заведения: "
    "атмосфера и интерьер, характер кухни и фирменные блюда, уровень сервиса, особенности меню и концепции, "
    "целевая аудитория, время работы и формат (ресторан/кафе/бар), уникальные особенности и изюминки заведения. "
    "Верни СТРОГО валидный JSON без пояснений, текста до/после и без markdown."
)


def _build_reviews_user_prompt(est: Establishment) -> str:
    schema = (
        '{'
        '"establishment_id":"string",'
        '"avg_rating": number | null,'
        '"reviews_count": number | null,'
        '"overall_opinion": string | null,'
        '"pros": [string, string, string],'
        '"cons": [string, string, string],'
        '"sources": [string]'
        '}'
    )
    lines = [
        "Задача:",
        "Собери отзывы и рейтинги по заведению из Яндекс.Карт и 2ГИС (если доступно).",
        "",
        "В поле overall_opinion ОБЯЗАТЕЛЬНО опиши РАЗВЁРНУТО (5–8 предложений) все особенности заведения:",
        "- Атмосфера и интерьер (стиль, оформление, обстановка)",
        "- Характер кухни и фирменные блюда (специализация, популярные позиции)",
        "- Уровень и характер сервиса (скорость, вежливость, профессионализм)",
        "- Особенности меню и концепции (формат, ценовой сегмент, уникальность)",
        "- Целевая аудитория (для кого заведение)",
        "- Время работы и формат (ресторан/кафе/бар, режим)",
        "- Уникальные особенности и изюминки заведения",
        "",
        "Выдели до 3 плюсов и до 3 минусов. Если данные противоречивы или скудные — всё равно постарайся выделить хотя бы по одному положительному и отрицательному пункту.",
        "",
        "Верни только JSON по схеме ниже. Никаких пояснений, текста до/после и markdown.",
        schema,
        "",
        "Детали заведения:",
        f"id: {est.id}",
        f"name: {est.name}",
        f"city: {est.city or ''}",
        f"country: {est.country or ''}",
        f"category: {est.category or ''}",
        f"url: {est.url or ''}",
    ]
    return "\n".join(lines)


def _parse_reviews_payload(establishment_id: str, payload: Any) -> ReviewSummary:
    data = payload if isinstance(payload, dict) else {}
    # Allow nested {"data": {...}}
    for key in ("data", "result", "reviews"):
        if isinstance(data.get(key), dict):
            data = data[key]
            break
    def _num(x: Any) -> Any:
        try:
            return float(x) if x is not None else None
        except (TypeError, ValueError):
            return None
    def _arr3(xs: Any) -> List[str]:
        if isinstance(xs, list):
            return [str(v) for v in xs[:3]]
        return []
    return ReviewSummary(
        establishment_id=establishment_id,
        avg_rating=_num(data.get("avg_rating")),
        reviews_count=int(data.get("reviews_count")) if isinstance(data.get("reviews_count"), (int, float)) else 0,
        sentiment_score=None,
        overall_opinion=str(data.get("overall_opinion") or "").strip() or None,
        pros=_arr3(data.get("pros")),
        cons=_arr3(data.get("cons")),
    )


async def _fetch_reviews_one_llm(est: Establishment, config: AppConfig) -> ReviewSummary:
    if not config.llm_api_key:
        return ReviewSummary(
            establishment_id=est.id,
            avg_rating=None,
            reviews_count=0,
            sentiment_score=None,
            overall_opinion=None,
            pros=[],
            cons=[],
        )
    settings = LlmSettings(
        provider=config.llm_provider or "perplexity",
        api_key=config.llm_api_key,
        model=config.llm_model or "sonar-reasoning-pro",
    )
    client = get_llm_client(settings)
    try:
        payload = await client.complete_json(
            system=REVIEWS_SYSTEM_PROMPT,
            user=_build_reviews_user_prompt(est),
            max_tokens=6000
        )
        # If client returned raw, try one coercion pass
        if isinstance(payload, dict) and "_raw" in payload:
            payload = await client.complete_json(
                system="Ты — конвертор данных в строгий JSON.",
                user="\n".join([
                    "Преобразуй текст ниже в валидный JSON по схеме:",
                    '{"establishment_id":"string","avg_rating":number|null,"reviews_count":number|null,"overall_opinion":string|null,"pros":[string,string,string],"cons":[string,string,string],"sources":[string]}',
                    "",
                    "ВАЖНО: overall_opinion должен быть развёрнутым (5–8 предложений) с описанием всех особенностей заведения: атмосфера, кухня, сервис, концепция, целевая аудитория, формат, уникальные особенности.",
                    "",
                    str(payload.get("_raw", ""))[:8000]
                ]),
                max_tokens=6000,
            )
        return _parse_reviews_payload(est.id, payload)
    except LlmError:
        return ReviewSummary(
            establishment_id=est.id,
            avg_rating=None,
            reviews_count=0,
            sentiment_score=None,
            overall_opinion=None,
            pros=[],
            cons=[],
        )


async def fetch_reviews_batch(establishments: List[Establishment], config: AppConfig | None = None) -> Dict[str, ReviewSummary]:
    cfg = config or load_config()
    summaries: Dict[str, ReviewSummary] = {}
    for est in establishments:
        summaries[est.id] = await _fetch_reviews_one_llm(est, cfg)
    return summaries


