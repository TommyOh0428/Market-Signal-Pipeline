"""Deterministic quantitative signal engine.

The final signal is intentionally computed in Python so an LLM can explain the
result later without owning the score or classification decision.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from statistics import fmean


@dataclass(frozen=True)
class PriceBar:
    """Daily market data normalized by a market data adapter."""

    trading_date: date
    close: float
    volume: float


@dataclass(frozen=True)
class QuantConfig:
    """Configurable defaults from the README signal model."""

    news_weight: float = 0.35
    momentum_weight: float = 0.25
    rsi_weight: float = 0.20
    macd_weight: float = 0.10
    volume_weight: float = 0.10
    bullish_threshold: float = 0.35
    bearish_threshold: float = -0.35
    sma_short_window: int = 20
    sma_long_window: int = 50
    rsi_window: int = 14
    macd_fast_window: int = 12
    macd_slow_window: int = 26
    macd_signal_window: int = 9
    volume_window: int = 20
    estimated_move_horizon_days: int = 5
    max_estimated_move_percent: float = 8.0


@dataclass(frozen=True)
class QuantIndicators:
    sma20: float | None
    sma50: float | None
    rsi: float | None
    macd: float | None
    macd_signal: float | None
    macd_histogram: float | None
    volume_ratio: float | None


@dataclass(frozen=True)
class QuantScores:
    news_score: float
    momentum_score: float
    rsi_score: float
    macd_score: float
    volume_score: float
    final_score: float
    confidence_score: float
    classification: str
    estimated_direction: str
    estimated_move_percent: float
    estimated_move_horizon_days: int
    estimated_base_price: float | None = None
    estimated_price_change: float | None = None
    estimated_price: float | None = None


@dataclass(frozen=True)
class SignalResult:
    ticker: str
    indicators: QuantIndicators
    scores: QuantScores
    warnings: list[str] = field(default_factory=list)


def calculate_signal(
    ticker: str,
    bars: list[PriceBar],
    news_score: float,
    current_price: float | None = None,
    config: QuantConfig | None = None,
) -> SignalResult:
    """Calculate indicators, normalized component scores, and final signal."""

    config = config or QuantConfig()
    sorted_bars = sorted(bars, key=lambda bar: bar.trading_date)
    warnings: list[str] = []

    closes = [bar.close for bar in sorted_bars]
    volumes = [bar.volume for bar in sorted_bars]

    _validate_market_data(closes, volumes)
    if current_price is not None and current_price <= 0:
        raise ValueError("Current price must be positive.")

    sma20 = _sma(closes, config.sma_short_window)
    sma50 = _sma(closes, config.sma_long_window)
    rsi = _rsi(closes, config.rsi_window)
    macd_line, macd_signal, macd_histogram = _macd(
        closes,
        config.macd_fast_window,
        config.macd_slow_window,
        config.macd_signal_window,
    )
    volume_ratio = _volume_ratio(volumes, config.volume_window)

    if sma20 is None:
        warnings.append(f"Need at least {config.sma_short_window} bars for SMA20.")
    if sma50 is None:
        warnings.append(f"Need at least {config.sma_long_window} bars for SMA50.")
    if rsi is None:
        warnings.append(f"Need at least {config.rsi_window + 1} bars for RSI.")
    if macd_histogram is None:
        required = config.macd_slow_window + config.macd_signal_window - 1
        warnings.append(f"Need at least {required} bars for MACD histogram.")
    if volume_ratio is None and len(volumes) < config.volume_window:
        warnings.append(f"Need at least {config.volume_window} volume bars.")
    elif volume_ratio is None:
        warnings.append("Volume baseline must be positive.")

    indicators = QuantIndicators(
        sma20=sma20,
        sma50=sma50,
        rsi=rsi,
        macd=macd_line,
        macd_signal=macd_signal,
        macd_histogram=macd_histogram,
        volume_ratio=volume_ratio,
    )

    latest_close = closes[-1] if closes else None
    momentum_score = _momentum_score(latest_close, sma20, sma50)
    rsi_score = _rsi_score(rsi)
    macd_score = _macd_score(macd_histogram, latest_close)
    volume_score = _volume_score(volume_ratio, momentum_score)
    scores = score_from_components(
        news_score=news_score,
        momentum_score=momentum_score,
        rsi_score=rsi_score,
        macd_score=macd_score,
        volume_score=volume_score,
        current_price=current_price or latest_close,
        config=config,
    )

    return SignalResult(
        ticker=ticker.upper(),
        indicators=indicators,
        scores=scores,
        warnings=warnings,
    )


def score_from_components(
    *,
    news_score: float,
    momentum_score: float,
    rsi_score: float,
    macd_score: float,
    volume_score: float,
    current_price: float | None = None,
    config: QuantConfig | None = None,
) -> QuantScores:
    """Score already-normalized components using README defaults."""

    config = config or QuantConfig()
    news_score = _clamp(news_score)
    momentum_score = _clamp(momentum_score)
    rsi_score = _clamp(rsi_score)
    macd_score = _clamp(macd_score)
    volume_score = _clamp(volume_score)

    final_score = (
        config.news_weight * news_score
        + config.momentum_weight * momentum_score
        + config.rsi_weight * rsi_score
        + config.macd_weight * macd_score
        + config.volume_weight * volume_score
    )
    final_score = _clamp(final_score)

    if final_score >= config.bullish_threshold:
        classification = "bullish"
    elif final_score <= config.bearish_threshold:
        classification = "bearish"
    else:
        classification = "neutral"

    estimated_move_percent = round(
        final_score * config.max_estimated_move_percent,
        2,
    )
    if estimated_move_percent > 0:
        estimated_direction = "increase"
    elif estimated_move_percent < 0:
        estimated_direction = "decrease"
    else:
        estimated_direction = "flat"

    estimated_price_change = None
    estimated_price = None
    estimated_base_price = None
    if current_price is not None:
        estimated_base_price = round(current_price, 2)
        estimated_price_change = round(
            current_price * estimated_move_percent / 100.0,
            2,
        )
        estimated_price = round(estimated_base_price + estimated_price_change, 2)

    return QuantScores(
        news_score=news_score,
        momentum_score=momentum_score,
        rsi_score=rsi_score,
        macd_score=macd_score,
        volume_score=volume_score,
        final_score=round(final_score, 4),
        confidence_score=round(min(abs(final_score), 1.0), 4),
        classification=classification,
        estimated_direction=estimated_direction,
        estimated_move_percent=estimated_move_percent,
        estimated_move_horizon_days=config.estimated_move_horizon_days,
        estimated_base_price=estimated_base_price,
        estimated_price_change=estimated_price_change,
        estimated_price=estimated_price,
    )


def _validate_market_data(closes: list[float], volumes: list[float]) -> None:
    if not closes:
        raise ValueError("At least one price bar is required.")
    if any(close <= 0 for close in closes):
        raise ValueError("Close prices must be positive.")
    if any(volume < 0 for volume in volumes):
        raise ValueError("Volumes cannot be negative.")


def _sma(values: list[float], window: int) -> float | None:
    if len(values) < window:
        return None
    return fmean(values[-window:])


def _rsi(closes: list[float], window: int) -> float | None:
    if len(closes) < window + 1:
        return None

    gains: list[float] = []
    losses: list[float] = []
    for previous, current in zip(closes[-window - 1 : -1], closes[-window:]):
        change = current - previous
        gains.append(max(change, 0.0))
        losses.append(max(-change, 0.0))

    average_gain = fmean(gains)
    average_loss = fmean(losses)
    if average_loss == 0:
        return 100.0 if average_gain > 0 else 50.0

    relative_strength = average_gain / average_loss
    return 100.0 - (100.0 / (1.0 + relative_strength))


def _macd(
    closes: list[float],
    fast_window: int,
    slow_window: int,
    signal_window: int,
) -> tuple[float | None, float | None, float | None]:
    if len(closes) < slow_window + signal_window - 1:
        return None, None, None

    fast_ema = _ema_series(closes, fast_window)
    slow_ema = _ema_series(closes, slow_window)
    macd_series: list[float] = []

    for fast_value, slow_value in zip(fast_ema, slow_ema):
        if fast_value is not None and slow_value is not None:
            macd_series.append(fast_value - slow_value)

    signal_series = _ema_series(macd_series, signal_window)
    signal_values = [value for value in signal_series if value is not None]
    if not macd_series or not signal_values:
        return None, None, None

    macd_line = macd_series[-1]
    signal_line = signal_values[-1]
    return macd_line, signal_line, macd_line - signal_line


def _ema_series(values: list[float], window: int) -> list[float | None]:
    if len(values) < window:
        return [None] * len(values)

    multiplier = 2.0 / (window + 1)
    series: list[float | None] = [None] * (window - 1)
    previous_ema = fmean(values[:window])
    series.append(previous_ema)

    for value in values[window:]:
        previous_ema = (value - previous_ema) * multiplier + previous_ema
        series.append(previous_ema)

    return series


def _volume_ratio(volumes: list[float], window: int) -> float | None:
    if len(volumes) < window:
        return None

    baseline = fmean(volumes[-window:])
    if baseline <= 0:
        return None
    return volumes[-1] / baseline


def _momentum_score(
    latest_close: float | None,
    sma20: float | None,
    sma50: float | None,
) -> float:
    if latest_close is None or sma20 is None or sma50 is None:
        return 0.0

    price_vs_sma20 = (latest_close - sma20) / sma20
    sma_spread = (sma20 - sma50) / sma50
    return _clamp((price_vs_sma20 + sma_spread) / 0.10)


def _rsi_score(rsi: float | None) -> float:
    if rsi is None:
        return 0.0
    return _clamp((50.0 - rsi) / 20.0)


def _macd_score(macd_histogram: float | None, latest_close: float | None) -> float:
    if macd_histogram is None or latest_close is None:
        return 0.0
    return _clamp((macd_histogram / latest_close) / 0.02)


def _volume_score(volume_ratio: float | None, momentum_score: float) -> float:
    if volume_ratio is None or momentum_score == 0:
        return 0.0
    volume_confirmation = _clamp((volume_ratio - 1.0) / 1.0)
    return volume_confirmation if momentum_score > 0 else -volume_confirmation


def _clamp(value: float, lower: float = -1.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))
