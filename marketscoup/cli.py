from __future__ import annotations

import asyncio
import json
from argparse import ArgumentParser

from .orchestrator import run_analysis


def main() -> None:
    parser = ArgumentParser(description="MarketScoup CLI")
    parser.add_argument("--query", required=True, help="Пользовательский запрос (описание заведения)")
    parser.add_argument("--top", type=int, default=10, help="Сколько похожих заведений выбрать")
    args = parser.parse_args()

    analysis = asyncio.run(run_analysis(query=args.query, top_n=args.top))
    # Support both Pydantic v2 (model_dump) and v1 (dict)
    analysis_dict = (
        analysis.model_dump() if hasattr(analysis, "model_dump") else analysis.dict()
    )
    print(json.dumps(analysis_dict, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


