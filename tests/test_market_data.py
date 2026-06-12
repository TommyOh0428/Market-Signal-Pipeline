from __future__ import annotations

from datetime import datetime

import pytest

from market_signal_pipeline.ingest import MarketDataError, YFinanceMarketDataProvider


class FakeSeries:
    def __init__(self, values: list[float | None]) -> None:
        self._values = values

    def dropna(self) -> "FakeSeries":
        return FakeSeries([value for value in self._values if value is not None])

    def tolist(self) -> list[float | None]:
        return self._values


class FakeDataFrame:
    def __init__(self, rows: list[tuple[datetime, dict[str, float | None]]]) -> None:
        self._rows = rows
        self.columns = set(rows[0][1].keys()) if rows else set()
        self.empty = not rows

    def iterrows(self):
        return iter(self._rows)

    def __getitem__(self, key: str) -> FakeSeries:
        return FakeSeries([row[key] for _, row in self._rows])


class FakeTicker:
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.fast_info = {"last_price": 208.64, "currency": "USD"}

    def history(self, period: str, interval: str, auto_adjust: bool = False) -> FakeDataFrame:
        return FakeDataFrame(
            [
                (datetime(2026, 1, 1), {"Close": 100.0, "Volume": 1000}),
                (datetime(2026, 1, 2), {"Close": 101.5, "Volume": 1200}),
            ]
        )


class FakeYFinance:
    @staticmethod
    def Ticker(symbol: str) -> FakeTicker:
        return FakeTicker(symbol)


def test_yfinance_adapter_normalizes_price_history() -> None:
    provider = YFinanceMarketDataProvider(yfinance_module=FakeYFinance)

    bars = provider.get_price_history("nvda")

    assert len(bars) == 2
    assert bars[0].trading_date.isoformat() == "2026-01-01"
    assert bars[0].close == 100.0
    assert bars[0].volume == 1000.0


def test_yfinance_adapter_returns_latest_quote() -> None:
    provider = YFinanceMarketDataProvider(yfinance_module=FakeYFinance)

    quote = provider.get_latest_quote("nvda")

    assert quote.ticker == "NVDA"
    assert quote.price == 208.64
    assert quote.provider == "yfinance"
    assert quote.currency == "USD"


def test_yfinance_adapter_rejects_empty_history() -> None:
    class EmptyTicker(FakeTicker):
        def history(
            self,
            period: str,
            interval: str,
            auto_adjust: bool = False,
        ) -> FakeDataFrame:
            return FakeDataFrame([])

    class EmptyYFinance:
        @staticmethod
        def Ticker(symbol: str) -> EmptyTicker:
            return EmptyTicker(symbol)

    provider = YFinanceMarketDataProvider(yfinance_module=EmptyYFinance)

    with pytest.raises(MarketDataError, match="No price history"):
        provider.get_price_history("NVDA")
