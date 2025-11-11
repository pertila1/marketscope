from __future__ import annotations

from typing import Any, Dict, List

from ..config import AppConfig, load_config
from ..domain.models import Establishment, ReviewSummary
from ..llm.client import LlmSettings, get_llm_client, LlmError


REVIEWS_SYSTEM_PROMPT = (
    "Ты — эксперт по анализу отзывов и ресторанному бизнесу. "
    "Найди информацию о заведении в Яндекс.Картах и 2ГИС, проанализируй отзывы и выдели все особенности и нюансы заведения. "
    "Обрати особое внимание на уникальные детали, атмосферу, концепцию, особенности кухни и сервиса. "
    "Верни СТРОГО валидный JSON без пояснений, текста до/после и без markdown."
)


def _build_reviews_user_prompt(est: Establishment) -> str:
    return f"""Найди информацию о заведении в Яндекс.Картах и 2ГИС и проанализируй отзывы.

Заведение:
- Название: {est.name}
- Город: {est.city or 'не указан'}
- Категория: {est.category or 'не указана'}
- URL: {est.url or 'не указан'}

Верни JSON со следующей структурой:
{{
  "establishment_id": "{est.id}",
  "avg_rating": число от 1 до 5 (средний рейтинг из отзывов),
  "overall_opinion": "развёрнутое описание заведения (8-12 предложений)",
  "pros": ["первый плюс", "второй плюс"],
  "cons": ["первый минус", "второй минус"]
}}

КРИТИЧЕСКИ ВАЖНО для поля overall_opinion:
Опиши РАЗВЁРНУТО (8-12 предложений) все особенности и нюансы заведения:
- Атмосфера и интерьер: стиль оформления, обстановка, детали дизайна, освещение, музыка
- Кухня: специализация, фирменные блюда, особенности приготовления, авторские решения, подача
- Сервис: уровень обслуживания, скорость, профессионализм персонала, особенности работы
- Концепция: формат заведения, целевая аудитория, ценовой сегмент, уникальные особенности
- Детали и нюансы: что делает это заведение особенным, изюминки, запоминающиеся моменты
- Расположение и окружение: где находится, что рядом, удобство расположения

Важно:
- avg_rating должен быть числом (например, 4.5)
- overall_opinion - РАЗВЁРНУТОЕ описание (8-12 предложений) с акцентом на особенности и нюансы
- pros - ровно 2 положительных пункта
- cons - ровно 2 отрицательных пункта
- Верни только JSON, без дополнительного текста"""


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
    
    def _arr2(xs: Any) -> List[str]:
        if isinstance(xs, list):
            return [str(v) for v in xs[:2]]
        return []
    
    return ReviewSummary(
        establishment_id=establishment_id,
        avg_rating=_num(data.get("avg_rating")),
        reviews_count=int(data.get("reviews_count")) if isinstance(data.get("reviews_count"), (int, float)) else 0,
        sentiment_score=None,
        overall_opinion=str(data.get("overall_opinion") or "").strip() or None,
        pros=_arr2(data.get("pros")),
        cons=_arr2(data.get("cons")),
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
                user=f"""Преобразуй текст ниже в валидный JSON:
{{
  "establishment_id": "{est.id}",
  "avg_rating": число,
  "overall_opinion": "развёрнутое описание (8-12 предложений) с особенностями и нюансами",
  "pros": ["строка", "строка"],
  "cons": ["строка", "строка"]
}}

ВАЖНО: overall_opinion должен быть развёрнутым (8-12 предложений) с описанием всех особенностей и нюансов заведения.

Текст для преобразования:
{str(payload.get("_raw", ""))[:7000]}""",
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
