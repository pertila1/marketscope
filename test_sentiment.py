#!/usr/bin/env python3
"""
Тест модуля тональности на block3_reviews_raw.json.
Запуск: python test_sentiment.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW_PATH = ROOT / "restaurant_pipeline" / "data_exchange" / "block3_reviews_raw.json"
OUT_PATH = ROOT / "restaurant_pipeline" / "data_exchange" / "block3_reviews_enriched_test.json"


def main():
    if not RAW_PATH.exists():
        print(f"Файл не найден: {RAW_PATH}")
        return

    with open(RAW_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    total = sum(len(p.get("reviews") or []) for p in data)
    print(f"Загружено: {len(data)} заведений, {total} отзывов")

    # Ограничим для быстрого теста (раскомментируйте для полного прогона)
    LIMIT_REVIEWS = 30  # None = все отзывы
    if LIMIT_REVIEWS:
        for place in data:
            reviews = place.get("reviews") or []
            if len(reviews) > LIMIT_REVIEWS:
                place["reviews"] = reviews[:LIMIT_REVIEWS]
        total = sum(len(p.get("reviews") or []) for p in data)
        print(f"Тест на первых {total} отзывах...")

    from restaurant_pipeline.blocks.block3_reviews.sentiment import add_sentiment_to_reviews

    add_sentiment_to_reviews(data)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Сохранено в {OUT_PATH}")
    print("\nПримеры (текст -> sentiment: -1/0/1):")
    for place in data[:2]:
        for r in (place.get("reviews") or [])[:3]:
            text = (r.get("text") or "")[:80].replace("\n", " ")
            print(f"  [{r.get('sentiment')}] {text}...")


if __name__ == "__main__":
    main()
