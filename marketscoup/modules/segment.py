from __future__ import annotations

from typing import Any, List

from ..config import load_config
from ..domain.models import Establishment, SegmentResult
from ..llm.client import LlmSettings, get_llm_client, LlmError


SYSTEM_PROMPT = (
    "Ты — ассистент-исследователь. Используй доступ к интернету, чтобы найти актуальные заведения в РФ. "
    "СТРАТЕГИЯ ПОИСКА: "
    "1) Сначала старайся найти указанное количество заведений, которые попадают И по тематике (тип кухни, специализация, концепция) И по ценовому сегменту (бюджет до 1500 руб, средний до 3000 руб, премиум выше 3000 руб); "
    "2) Если таких не хватает — дополни список заведениями, которые попадают хотя бы по тематике. "
    "Для каждого заведения рассчитай similarity_score (0.0-1.0): 1.0 = идеальное соответствие тематике и сегменту, 0.8-0.9 = только тематика, ниже = частичное соответствие. "
    "Верни НЕ МЕНЕЕ указанного количества заведений, отсортированных по similarity_score (убывание). "
    "Верни СТРОГО валидный JSON без какого-либо дополнительного текста, комментариев или markdown."
)


def _build_user_prompt(query: str, top_n: int) -> str:
    return "\n".join(
        [
            "Запрос пользователя:",
            query,
            "",
            "СТРАТЕГИЯ ПОИСКА:",
            f"1) Сначала старайся найти {top_n} заведений, которые попадают И по тематике (тип кухни, специализация, концепция) И по ценовому сегменту",
            f"2) Если таких не хватает — дополни список до {top_n} заведениями, которые попадают хотя бы по тематике",
            "",
            "Для каждого заведения рассчитай similarity_score (число от 0.0 до 1.0):",
            "- 1.0 = идеальное соответствие тематике И ценовому сегменту",
            "- 0.8-0.9 = попадание только по тематике (без сегмента)",
            "- 0.5-0.7 = частичное соответствие",
            "- ниже 0.5 = слабое соответствие",
            "",
            f"ОБЯЗАТЕЛЬНО верни НЕ МЕНЕЕ {top_n} актуальных заведений в РФ, отсортированных по similarity_score (от большего к меньшему).",
            f"Если не хватает точных совпадений — расширь поиск, но верни минимум {top_n} заведений. НИ В КОЕМ СЛУЧАЕ не меньше.",
            "",
            "Для каждого укажи реальные: id (можно использовать slug или URL), название, адрес (если есть), город, страну, категорию, URL и similarity_score.",
            "Строго выведи JSON в формате: "
            '{"establishments":[{"id":string,"name":string,"address"?:string,"city"?:string,"country"?:string,"category"?:string,"url"?:string,"similarity_score":number}]}',
            "Никакого текста до или после JSON. Никаких пояснений или markdown.",
        ]
    )


def _build_user_prompt_strict(query: str, top_n: int) -> str:
    return _build_user_prompt(query, top_n) + "\n\nТолько один JSON-объект. Никаких комментариев, markdown и текста вне JSON."


def _build_user_prompt_ultra_strict(query: str, top_n: int) -> str:
    return "\n".join(
        [
            "Запрос:",
            query,
            "",
            f"СТРАТЕГИЯ: 1) найти {top_n} по тематике+сегменту, 2) если не хватает — добавить по тематике",
            f"КРИТИЧЕСКОЕ ТРЕБОВАНИЕ: верни РОВНО {top_n} заведений (НЕ МЕНЬШЕ).",
            "Для каждого рассчитай similarity_score (0.0-1.0). Отсортируй по similarity_score (убывание).",
            f"Если точных совпадений меньше {top_n} — расширь критерии поиска, но верни минимум {top_n} заведений.",
            "Формат JSON:",
            '{"establishments":[{"id":"...","name":"...","address":"...","city":"...","country":"...","category":"...","url":"...","similarity_score":0.95}]}',
            "",
            "ТОЛЬКО JSON. Никакого текста, пояснений, markdown, комментариев. Только валидный JSON-объект.",
        ]
    )


def _build_coerce_prompt(raw: str, top_n: int) -> str:
    return "\n".join(
        [
            "Преобразуй приведённый ниже контент в валидный JSON строго по этой схеме:",
            '{"establishments":[{"id":string,"name":string,"address"?:string,"city"?:string,"country"?:string,"category"?:string,"url"?:string,"similarity_score":number}]}',
            "",
            "СТРАТЕГИЯ: 1) найти по тематике+сегменту, 2) если не хватает — добавить по тематике",
            f"ОБЯЗАТЕЛЬНО верни НЕ МЕНЕЕ {top_n} заведений. Для каждого рассчитай similarity_score (0.0-1.0).",
            "Отсортируй по similarity_score (убывание). Никакого текста вне JSON.",
            "",
            "Контент:",
            raw[:8000],
        ]
    )


def _parse_establishments(payload: Any, limit: int) -> List[Establishment]:
    establishments_raw = []
    if isinstance(payload, dict) and isinstance(payload.get("establishments"), list):
        establishments_raw = payload["establishments"]
    elif isinstance(payload, list):
        establishments_raw = payload
    results: List[Establishment] = []
    for item in establishments_raw[:limit]:
        try:
            # Извлекаем similarity_score, нормализуем в диапазон 0.0-1.0
            similarity = item.get("similarity_score")
            if similarity is not None:
                try:
                    similarity = float(similarity)
                    # Ограничиваем диапазон 0.0-1.0
                    similarity = max(0.0, min(1.0, similarity))
                except (ValueError, TypeError):
                    similarity = None
            results.append(
                Establishment(
                    id=str(item.get("id") or item.get("url") or item.get("name")),
                    name=str(item.get("name")),
                    address=item.get("address"),
                    city=item.get("city"),
                    country=item.get("country") or "RU",
                    category=item.get("category"),
                    url=item.get("url"),
                    similarity_score=similarity,
                )
            )
        except Exception:
            continue
    return results


async def find_similar_establishments(query: str, top_n: int = 10) -> SegmentResult:
    config = load_config()
    debug = (config.log_level or "").upper() == "DEBUG"
    if not config.llm_api_key:
        # Fallback на mock при отсутствии ключа
        if debug:
            print("[segment-llm-skip] no LLM_API_KEY, returning mock data")
        mock: List[Establishment] = [
            Establishment(id=f"mock-{i}", name=f"Заведение {i}", city="Москва", country="RU")
            for i in range(1, top_n + 1)
        ]
        return SegmentResult(query=query, establishments=mock)

    settings = LlmSettings(
        provider=config.llm_provider or "perplexity",
        api_key=config.llm_api_key,
        model=config.llm_model or "sonar-reasoning-pro",
    )
    client = get_llm_client(settings)

    try:
        if debug:
            print(f"[segment-llm-start] query={query!r} top_n={top_n}")
        payload = await client.complete_json(
            system=SYSTEM_PROMPT,
            user=_build_user_prompt(query, top_n),
            max_tokens=3000,
        )
        # Если клиент вернул _raw, пробуем коэрсию в нужный JSON
        if isinstance(payload, dict) and "_raw" in payload:
            raw_text = str(payload.get("_raw", ""))
            payload = await client.complete_json(
                system="Ты — конвертор данных в строгий JSON.",
                user=_build_coerce_prompt(raw_text, top_n),
                max_tokens=2500,
            )
    except LlmError as exc:
        if debug:
            print(f"[segment-llm-error] query={query!r}: {exc} -> retry_strict")
        try:
            payload = await client.complete_json(
                system=SYSTEM_PROMPT,
                user=_build_user_prompt_strict(query, top_n),
                max_tokens=2800,
            )
            if isinstance(payload, dict) and "_raw" in payload:
                raw_text = str(payload.get("_raw", ""))
                payload = await client.complete_json(
                    system="Ты — конвертор данных в строгий JSON.",
                    user=_build_coerce_prompt(raw_text, top_n),
                    max_tokens=2500,
                )
        except LlmError as exc2:
            if debug:
                print(f"[segment-llm-error-strict] query={query!r}: {exc2} -> retry_ultra_strict")
            try:
                # Ультра-строгий ретрай
                payload = await client.complete_json(
                    system="Ты — ассистент-исследователь. Верни строго валидный JSON без текста.",
                    user=_build_user_prompt_ultra_strict(query, top_n),
                    max_tokens=3000,
                )
                if isinstance(payload, dict) and "_raw" in payload:
                    raw_text = str(payload.get("_raw", ""))
                    payload = await client.complete_json(
                        system="Ты — конвертор данных в строгий JSON.",
                        user=_build_coerce_prompt(raw_text, top_n),
                        max_tokens=2500,
                    )
            except LlmError as exc3:
                if debug:
                    print(f"[segment-llm-error-final] query={query!r}: {exc3}")
                # Возвращаем безопасный fallback
                mock: List[Establishment] = [
                    Establishment(id=f"mock-{i}", name=f"Заведение {i}", city="Москва", country="RU")
                    for i in range(1, top_n + 1)
                ]
                return SegmentResult(query=query, establishments=mock)

    establishments = _parse_establishments(payload, top_n)
    
    # Проверка: если вернулось меньше top_n, делаем ультра-строгий ретрай
    if len(establishments) < top_n:
        if debug:
            print(f"[segment-llm-insufficient] query={query!r} got {len(establishments)} < {top_n}, retrying ultra_strict")
        try:
            payload_retry = await client.complete_json(
                system="Ты — ассистент-исследователь. Верни строго валидный JSON без текста.",
                user=_build_user_prompt_ultra_strict(query, top_n),
                max_tokens=3000,
            )
            if isinstance(payload_retry, dict) and "_raw" in payload_retry:
                raw_text = str(payload_retry.get("_raw", ""))
                payload_retry = await client.complete_json(
                    system="Ты — конвертор данных в строгий JSON.",
                    user=_build_coerce_prompt(raw_text, top_n),
                    max_tokens=2500,
                )
            establishments_retry = _parse_establishments(payload_retry, top_n)
            if len(establishments_retry) >= top_n:
                establishments = establishments_retry
        except LlmError:
            pass
    
    if not establishments:
        if debug:
            preview = payload if isinstance(payload, dict) else {"_raw": str(payload)[:300]}
            print(f"[segment-llm-empty] query={query!r} payload_preview={preview}")
        # Последняя попытка: если ещё есть _raw-текст, конвертируем и парсим снова
        if isinstance(payload, dict) and "_raw" in payload:
            try:
                raw_text = str(payload.get("_raw", ""))
                payload2 = await client.complete_json(
                    system="Ты — конвертор данных в строгий JSON.",
                    user=_build_coerce_prompt(raw_text, top_n),
                    max_tokens=2500,
                )
                establishments2 = _parse_establishments(payload2, top_n)
                if establishments2:
                    return SegmentResult(query=query, establishments=establishments2)
            except LlmError:
                pass
        # Если конверсия не помогла — возвращаем пустой результат без моков
        return SegmentResult(query=query, establishments=[])
    return SegmentResult(query=query, establishments=establishments)


