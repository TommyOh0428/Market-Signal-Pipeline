"""Market data provider adapters."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Protocol

from market_signal_pipeline.quant import PriceBar


class MarketDataError(RuntimeError):
    """Raised when a market data provider cannot return usable data."""


@dataclass(frozen=True)
class MarketQuote:
    ticker: str
    price: float
    provider: str
    currency: str | None = None
    as_of: datetime | None = None


class MarketDataProvider(Protocol):
    def get_price_history(self, ticker: str, period: str = "3mo") -> list[PriceBar]:
        """Return normalized daily price bars for quant indicators."""

    def get_latest_quote(self, ticker: str) -> MarketQuote:
        """Return the latest available quote for projection base price."""


class YFinanceMarketDataProvider:
    """Market data adapter backed by yfinance."""

    provider_name = "yfinance"

    def __init__(self, yfinance_module: Any | None = None) -> None:
        if yfinance_module is not None:
            self._yf = yfinance_module
            return

        try:
            import yfinance as yf
        except ImportError as exc:
            raise MarketDataError(
                "yfinance is required for live market data. Install project dependencies first."
            ) from exc

        self._yf = yf

    def get_price_history(self, ticker: str, period: str = "3mo") -> list[PriceBar]:
        symbol = ticker.upper()
        history = self._ticker(symbol).history(
            period=period,
            interval="1d",
            auto_adjust=False,
        )
        if history is None or history.empty:
            raise MarketDataError(f"No price history returned for {symbol}.")
        if "Close" not in history.columns or "Volume" not in history.columns:
            raise MarketDataError(f"Price history for {symbol} is missing Close or Volume.")

        bars: list[PriceBar] = []
        for index, row in history.iterrows():
            close = row["Close"]
            volume = row["Volume"]
            if _is_missing(close) or _is_missing(volume):
                continue

            bars.append(
                PriceBar(
                    trading_date=_index_to_date(index),
                    close=float(close),
                    volume=float(volume),
                )
            )

        if not bars:
            raise MarketDataError(f"No usable price bars returned for {symbol}.")
        return bars

    def get_latest_quote(self, ticker: str) -> MarketQuote:
        symbol = ticker.upper()
        ticker_obj = self._ticker(symbol)
        fast_info = getattr(ticker_obj, "fast_info", {}) or {}

        price = _first_positive(
            _get_info_value(fast_info, "last_price"),
            _get_info_value(fast_info, "regular_market_price"),
            _get_info_value(fast_info, "lastPrice"),
        )
        currency = _get_info_value(fast_info, "currency")

        if price is None:
            intraday = ticker_obj.history(period="1d", interval="1m")
            if intraday is not None and not intraday.empty and "Close" in intraday.columns:
                closes = [
                    float(value)
                    for value in intraday["Close"].dropna().tolist()
                    if float(value) > 0
                ]
                if closes:
                    price = closes[-1]

        if price is None:
            raise MarketDataError(f"No latest quote returned for {symbol}.")

        return MarketQuote(
            ticker=symbol,
            price=float(price),
            provider=self.provider_name,
            currency=str(currency) if currency else None,
        )

    def _ticker(self, ticker: str) -> Any:
        return self._yf.Ticker(ticker)


def _index_to_date(value: Any) -> date:
    if hasattr(value, "date"):
        return value.date()
    if isinstance(value, date):
        return value
    raise MarketDataError(f"Unsupported market data date value: {value!r}")


def _is_missing(value: Any) -> bool:
    return value is None or value != value


def _get_info_value(info: Any, key: str) -> Any:
    if hasattr(info, key):
        return getattr(info, key)
    if hasattr(info, "get"):
        return info.get(key)
    return None


def _first_positive(*values: Any) -> float | None:
    for value in values:
        if value is None:
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if number > 0:
            return number
    return None
