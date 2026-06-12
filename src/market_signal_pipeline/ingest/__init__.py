"""Market data and news ingestion adapters."""

from market_signal_pipeline.ingest.market_data import (
    MarketDataError,
    MarketDataProvider,
    MarketQuote,
    YFinanceMarketDataProvider,
)

__all__ = [
    "MarketDataError",
    "MarketDataProvider",
    "MarketQuote",
    "YFinanceMarketDataProvider",
]
