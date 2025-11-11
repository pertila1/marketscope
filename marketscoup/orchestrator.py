from __future__ import annotations

import asyncio
from typing import List

from .config import load_config
from .domain.models import (
    AggregatedAnalysis,
    AggregatedEstablishment,
    Establishment,
)
from .modules.aggregator import aggregate
from .modules.finance import fetch_finance_batch
from .modules.reviews import fetch_reviews_batch
from .modules.segment import find_similar_establishments


async def run_analysis(query: str, top_n: int = 10) -> AggregatedAnalysis:
    config = load_config()
    debug = (config.log_level or "").upper() == "DEBUG"

    segment = await find_similar_establishments(query=query, top_n=top_n)
    establishments: List[Establishment] = segment.establishments
    if debug:
        print(f"[orchestrator] establishments_count={len(establishments)}")

    finance_task = asyncio.create_task(
        fetch_finance_batch(establishments, config=config)
    )
    reviews_task = asyncio.create_task(
        fetch_reviews_batch(establishments, config=config)
    )

    finance, reviews = await asyncio.gather(finance_task, reviews_task)

    items: List[AggregatedEstablishment] = aggregate(
        establishments=establishments, finance=finance, reviews=reviews
    )
    if debug:
        print(f"[orchestrator] aggregated_items_count={len(items)}")

    return AggregatedAnalysis(query=query, items=items)


