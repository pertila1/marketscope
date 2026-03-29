# -*- coding: utf-8 -*-
"""
Скачать энкодер (sentence-transformers) в encoder_cache один раз, чтобы при поиске не ждать загрузки.
Запуск: python download_encoder.py
"""
from place_search import (
    DEFAULT_ENCODER_MODEL,
    download_encoder,
    _encoder_cache_exists,
    _get_encoder_cache_dir,
)

if __name__ == "__main__":
    cache_dir = _get_encoder_cache_dir(DEFAULT_ENCODER_MODEL)
    if _encoder_cache_exists(cache_dir):
        print(f"Энкодер уже в кэше: {cache_dir}")
    else:
        print(f"Скачиваю энкодер {DEFAULT_ENCODER_MODEL}…")
        path = download_encoder(model_name=DEFAULT_ENCODER_MODEL, device="cpu")
        print(f"Готово. Веса сохранены в: {path}")
