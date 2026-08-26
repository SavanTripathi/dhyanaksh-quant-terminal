"""
Unit tests for Lifecycle Alert State Machine.
"""
from datetime import datetime
import pytest
from app.domain.enums import Timeframe, ZoneDirection, AlertType, AlertState
from app.domain.schemas import TradePlanSchema, CandleSchema
from app.alerts.state_machine import LifecycleStateMachine


def test_state_machine_demand_transitions():
    """
    Test Demand Plan:
    Entry = 1000.0, SL = 950.0, T1 = 1100.0, T2 = 1175.0, T3 = 1250.0, Overlap = [960.0, 1000.0]
    """
    plan = TradePlanSchema(
        symbol="RELIANCE",
        direction=ZoneDirection.DEMAND,
        current_price=1060.0,
        overlap_min_price=960.0,
        overlap_max_price=1000.0,
        entry_price=1000.0,
        stop_loss=950.0,
        risk_per_share=50.0,
        target_1=1100.0,
        target_2=1175.0,
        target_3=1250.0,
        atr_1d_14=20.0,
        atr_buffer=4.0,
        distance_pct=6.0,
        is_approaching=False,
        achievements=3,
        participating_timeframes=[Timeframe.MONTHLY, Timeframe.WEEKLY, Timeframe.DAILY]
    )

    t0 = datetime(2026, 1, 1)

    # 1. Monitoring: Price is far away (Close 1080 -> Distance ~7.4%)
    c_mon = CandleSchema(timestamp=t0, open=1070, high=1090, low=1065, close=1080, timeframe=Timeframe.DAILY, symbol="RELIANCE")
    state, alert = LifecycleStateMachine.evaluate_state_transition(plan, c_mon)
    assert state == AlertState.MONITORING
    assert alert is None

    # 2. Approaching: Price nears entry (Close 1020 -> Distance = (20/1020)*100 = 1.96% <= 2.5%)
    c_app = CandleSchema(timestamp=t0, open=1040, high=1045, low=1015, close=1020, timeframe=Timeframe.DAILY, symbol="RELIANCE")
    state, alert = LifecycleStateMachine.evaluate_state_transition(plan, c_app)
    assert state == AlertState.APPROACHING
    assert alert == AlertType.APPROACHING

    # 3. Zone Hit / Inside Zone: Low touches 980 (inside [960, 1000])
    c_hit = CandleSchema(timestamp=t0, open=1010, high=1015, low=980, close=995, timeframe=Timeframe.DAILY, symbol="RELIANCE")
    state, alert = LifecycleStateMachine.evaluate_state_transition(plan, c_hit)
    assert state == AlertState.INSIDE_ZONE
    assert alert == AlertType.ZONE_HIT

    # 4. Target 1 Reached: High touches 1110 (>= T1 1100)
    c_t1 = CandleSchema(timestamp=t0, open=1000, high=1110, low=995, close=1105, timeframe=Timeframe.DAILY, symbol="RELIANCE")
    state, alert = LifecycleStateMachine.evaluate_state_transition(plan, c_t1)
    assert state == AlertState.TARGET_1_HIT
    assert alert == AlertType.TARGET_1_HIT

    # 5. Invalidated: Low breaks below SL (Low 945 <= SL 950)
    c_inv = CandleSchema(timestamp=t0, open=960, high=965, low=945, close=948, timeframe=Timeframe.DAILY, symbol="RELIANCE")
    state, alert = LifecycleStateMachine.evaluate_state_transition(plan, c_inv)
    assert state == AlertState.INVALIDATED
    assert alert == AlertType.INVALIDATED


def test_state_machine_supply_transitions():
    """
    Test Supply Plan:
    Entry = 2000.0, SL = 2080.0, T1 = 1840.0, T2 = 1720.0, T3 = 1600.0, Overlap = [2000.0, 2070.0]
    """
    plan = TradePlanSchema(
        symbol="TCS",
        direction=ZoneDirection.SUPPLY,
        current_price=1900.0,
        overlap_min_price=2000.0,
        overlap_max_price=2070.0,
        entry_price=2000.0,
        stop_loss=2080.0,
        risk_per_share=80.0,
        target_1=1840.0,
        target_2=1720.0,
        target_3=1600.0,
        atr_1d_14=30.0,
        atr_buffer=6.0,
        distance_pct=5.0,
        is_approaching=False,
        achievements=2,
        participating_timeframes=[Timeframe.WEEKLY, Timeframe.DAILY]
    )

    t0 = datetime(2026, 1, 1)

    # 1. Approaching: Close 1970 -> Distance = ((2000-1970)/1970)*100 = 1.52% <= 2.5%
    c_app = CandleSchema(timestamp=t0, open=1950, high=1980, low=1945, close=1970, timeframe=Timeframe.DAILY, symbol="TCS")
    state, alert = LifecycleStateMachine.evaluate_state_transition(plan, c_app)
    assert state == AlertState.APPROACHING
    assert alert == AlertType.APPROACHING

    # 2. Zone Hit: High reaches 2030 (inside [2000, 2070])
    c_hit = CandleSchema(timestamp=t0, open=1990, high=2030, low=1985, close=2010, timeframe=Timeframe.DAILY, symbol="TCS")
    state, alert = LifecycleStateMachine.evaluate_state_transition(plan, c_hit)
    assert state == AlertState.INSIDE_ZONE
    assert alert == AlertType.ZONE_HIT

    # 3. Invalidated: High breaches SL (High 2085 >= SL 2080)
    c_inv = CandleSchema(timestamp=t0, open=2060, high=2085, low=2050, close=2075, timeframe=Timeframe.DAILY, symbol="TCS")
    state, alert = LifecycleStateMachine.evaluate_state_transition(plan, c_inv)
    assert state == AlertState.INVALIDATED
    assert alert == AlertType.INVALIDATED
