"""Run the deterministic quant engine with live market data."""

from __future__ import annotations

import argparse

from market_signal_pipeline.ingest import MarketDataError, YFinanceMarketDataProvider
from market_signal_pipeline.quant import calculate_signal


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticker", default="NVDA")
    parser.add_argument("--period", default="3mo")
    parser.add_argument("--news-score", type=float, default=0.0)
    args = parser.parse_args()

    provider = YFinanceMarketDataProvider()
    quote = provider.get_latest_quote(args.ticker)
    bars = provider.get_price_history(args.ticker, period=args.period)

    result = calculate_signal(
        args.ticker,
        bars,
        news_score=args.news_score,
        current_price=quote.price,
    )

    print(f"{result.ticker}: {result.scores.classification}")
    print(f"quote_provider={quote.provider}")
    print(f"latest_quote={quote.price}")
    print(f"final_score={result.scores.final_score}")
    print(f"confidence_score={result.scores.confidence_score}")
    print(
        "estimated_move="
        f"{result.scores.estimated_direction} "
        f"{abs(result.scores.estimated_move_percent)}% "
        f"over {result.scores.estimated_move_horizon_days} trading days"
    )
    print(f"estimated_base_price={result.scores.estimated_base_price}")
    print(f"estimated_price_change={result.scores.estimated_price_change}")
    print(f"estimated_price={result.scores.estimated_price}")
    print(result.indicators)
    if result.warnings:
        print("warnings:", result.warnings)


if __name__ == "__main__":
    try:
        main()
    except MarketDataError as exc:
        raise SystemExit(f"market data error: {exc}") from exc
