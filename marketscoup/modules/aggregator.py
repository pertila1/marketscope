from __future__ import annotations

from typing import Dict, List

from ..domain.models import (
    AggregatedEstablishment,
    Establishment,
    FinanceSnapshot,
    ReviewSummary,
)


def aggregate(
    establishments: List[Establishment],
    finance: Dict[str, FinanceSnapshot],
    reviews: Dict[str, ReviewSummary],
) -> List[AggregatedEstablishment]:
    aggregated: List[AggregatedEstablishment] = []
    for e in establishments:
        aggregated.append(
            AggregatedEstablishment(
                establishment=e,
                finance=finance.get(e.id),
                reviews=reviews.get(e.id),
            )
        )
    return aggregated


