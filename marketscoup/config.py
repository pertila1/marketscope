from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    spark_api_base_url: Optional[str]
    spark_api_token: Optional[str]
    http_proxy: Optional[str]
    https_proxy: Optional[str]
    log_level: str
    default_city: Optional[str]
    default_country: Optional[str]
    llm_provider: Optional[str]
    llm_api_key: Optional[str]
    llm_model: Optional[str]


def load_config() -> AppConfig:
    load_dotenv()
    return AppConfig(
        spark_api_base_url=os.getenv("SPARK_API_BASE_URL"),
        spark_api_token=os.getenv("SPARK_API_TOKEN"),
        http_proxy=os.getenv("HTTP_PROXY"),
        https_proxy=os.getenv("HTTPS_PROXY"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        default_city=os.getenv("DEFAULT_CITY"),
        default_country=os.getenv("DEFAULT_COUNTRY"),
        llm_provider=os.getenv("LLM_PROVIDER", "perplexity"),
        llm_api_key=os.getenv("LLM_API_KEY"),
        llm_model=os.getenv("LLM_MODEL", "sonar-reasoning-pro"),
    )


