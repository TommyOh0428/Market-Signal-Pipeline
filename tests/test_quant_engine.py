from __future__ import annotations

from datetime import date, timedelta

import pytest

from market_signal_pipeline.quant import PriceBar, calculate_signal, score_from_components


def test_bullish_threshold_boundary() -> None:
    scores = score_from_components(
        news_score=1.0,
        momentum_score=0.0,
        rsi_score=0.0,
        macd_score=0.0,
        volume_score=0.0,
    )

    assert scores.final_score == 0.35
    assert scores.classification == "bullish"
    assert scores.confidence_score == 0.35
    assert scores.estimated_direction == "increase"
    assert scores.estimated_move_percent == 2.8


def test_bearish_threshold_boundary() -> None:
    scores = score_from_components(
        news_score=-1.0,
        momentum_score=0.0,
        rsi_score=0.0,
        macd_score=0.0,
        volume_score=0.0,
    )

    assert scores.final_score == -0.35
    assert scores.classification == "bearish"
    assert scores.confidence_score == 0.35
    assert scores.estimated_direction == "decrease"
    assert scores.estimated_move_percent == -2.8


def test_neutral_range_behavior() -> None:
    scores = score_from_components(
        news_score=0.0,
        momentum_score=1.0,
        rsi_score=0.0,
        macd_score=0.0,
        volume_score=0.0,
    )

    assert scores.final_score == 0.25
    assert scores.classification == "neutral"
    assert scores.estimated_move_percent == 2.0


def test_component_scores_are_clamped() -> None:
    scores = score_from_components(
        news_score=3.0,
        momentum_score=3.0,
        rsi_score=3.0,
        macd_score=3.0,
        volume_score=3.0,
    )

    assert scores.news_score == 1.0
    assert scores.momentum_score == 1.0
    assert scores.rsi_score == 1.0
    assert scores.macd_score == 1.0
    assert scores.volume_score == 1.0
    assert scores.final_score == 1.0
    assert scores.confidence_score == 1.0
    assert scores.estimated_move_percent == 8.0


def test_estimated_price_move_uses_current_price_when_available() -> None:
    scores = score_from_components(
        news_score=1.0,
        momentum_score=0.0,
        rsi_score=0.0,
        macd_score=0.0,
        volume_score=0.0,
        current_price=100.0,
    )

    assert scores.estimated_move_horizon_days == 5
    assert scores.estimated_base_price == 100.0
    assert scores.estimated_price_change == 2.8
    assert scores.estimated_price == 102.8


def test_calculate_signal_can_project_from_current_price_override() -> None:
    bars = [
        PriceBar(
            trading_date=date(2026, 1, 1) + timedelta(days=offset),
            close=180.0 + offset * 0.85,
            volume=1_000_000 + offset * 7_500,
        )
        for offset in range(60)
    ]

    result = calculate_signal("NVDA", bars, news_score=1.0, current_price=208.64)

    assert result.indicators.sma20 == 222.075
    assert result.scores.estimated_base_price == 208.64
    assert result.scores.estimated_move_percent == 3.19
    assert result.scores.estimated_price_change == 6.66
    assert result.scores.estimated_price == 215.3


def test_short_history_returns_warnings_and_neutral_quant_scores() -> None:
    bars = [
        PriceBar(date(2026, 1, 1) + timedelta(days=offset), 100.0 + offset, 1000)
        for offset in range(10)
    ]

    result = calculate_signal("aapl", bars, news_score=0.0)

    assert result.ticker == "AAPL"
    assert result.scores.classification == "neutral"
    assert result.indicators.sma20 is None
    assert result.indicators.sma50 is None
    assert len(result.warnings) == 5


def test_zero_volume_baseline_warns_and_volume_score_is_neutral() -> None:
    bars = [
        PriceBar(date(2026, 1, 1) + timedelta(days=offset), 100.0 + offset, 0)
        for offset in range(60)
    ]

    result = calculate_signal("TSLA", bars, news_score=0.0)

    assert result.indicators.volume_ratio is None
    assert result.scores.volume_score == 0.0
    assert "Volume baseline must be positive." in result.warnings


def test_fixed_fixture_is_deterministic() -> None:
    bars = [
        PriceBar(
            date(2026, 1, 1) + timedelta(days=offset),
            close=100.0 + offset * 0.5,
            volume=1_000_000 + offset * 10_000,
        )
        for offset in range(60)
    ]

    first = calculate_signal("NVDA", bars, news_score=1.0)
    second = calculate_signal("NVDA", list(reversed(bars)), news_score=1.0)

    assert first == second
    assert first.scores.classification == "bullish"
    assert first.scores.final_score == 0.4064
    assert first.scores.estimated_direction == "increase"
    assert first.scores.estimated_move_percent == 3.25
    assert first.scores.estimated_price_change == 4.21
    assert first.scores.estimated_price == 133.71


def test_invalid_market_data_raises() -> None:
    with pytest.raises(ValueError, match="Close prices must be positive"):
        calculate_signal("NVDA", [PriceBar(date(2026, 1, 1), 0.0, 1000)], 0.0)


def test_invalid_current_price_raises() -> None:
    with pytest.raises(ValueError, match="Current price must be positive"):
        calculate_signal(
            "NVDA",
            [PriceBar(date(2026, 1, 1), 100.0, 1000)],
            news_score=0.0,
            current_price=0.0,
        )
