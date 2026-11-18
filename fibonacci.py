"""
HERMES Fibonacci Mastery Module
Mastered from the 5 videos:
- Fibonacci Retracement explained in under 5 minutes (nYKpik-o8zI)
- How To Trade Fibonacci In 2026 (5MFXsjZGkDQ)
- This Fibonacci Trading Strategy will Make MILLIONAIRES... (H3AeKS2APdk)
- The 1-Minute Fibonacci Scalping Strategy (That Actually Works) (AlsXNhTm4AA)
- Fibonacci Trading Full Course, Retracement, Extension, Entries & Targets (tM1o5Zii0qI)

Master Principles:
- Retracements: 23.6% (shallow), 38.2%, 50% (psychological), 61.8% (golden ratio - strongest), 78.6%
- Extensions: 127.2%, 161.8% (golden), 200%, 261.8% for targets
- Draw retracement from swing low to swing high in uptrend (support zones)
- Draw from swing high to swing low in downtrend (resistance zones)
- Always require confluence: candlestick patterns, volume, other indicators (Keltner, MACD, ORB)
- For scalping (1min): use with market structure, enter on pullback to Fib + confirmation
- Use extensions for profit targets beyond the move
- Risk management: stop beyond next Fib level
- Limitations: best in trends, combine tools, not standalone
- Self-fulfilling due to widespread use by algos and traders

Integration goal: Enhance HERMES entries, targets, and learning with Fib for more consistent big winners.
"""

import numpy as np
from typing import Dict, Tuple, Optional, List

FIB_RATIOS_RETR = [0.236, 0.382, 0.5, 0.618, 0.786]
FIB_RATIOS_EXT = [1.272, 1.618, 2.0, 2.618]

def calculate_retracement_levels(swing_high: float, swing_low: float) -> Dict[float, float]:
    """Calculate standard Fibonacci retracement levels.
    Standard: for retracement in uptrend, levels from high down to low.
    """
    if swing_high <= swing_low:
        swing_high, swing_low = swing_low, swing_high
    diff = swing_high - swing_low
    levels = {0.0: swing_high}
    for r in FIB_RATIOS_RETR:
        levels[r] = swing_high - diff * r
    levels[1.0] = swing_low
    return levels

def calculate_extension_levels(swing_high: float, swing_low: float, direction: str = 'long') -> Dict[float, float]:
    """Calculate Fibonacci extension levels for targets.
    For long: extensions above swing_high
    For short: below swing_low
    """
    diff = abs(swing_high - swing_low)
    if direction == 'long':
        base = swing_high
        levels = {1.0: base}
        for r in FIB_RATIOS_EXT:
            levels[r] = base + diff * (r - 1.0)
    else:
        base = swing_low
        levels = {1.0: base}
        for r in FIB_RATIOS_EXT:
            levels[r] = base - diff * (r - 1.0)
    return levels

def find_closest_fib_level(price: float, levels: Dict[float, float], tolerance_pct: float = 0.15) -> Optional[Tuple[float, float]]:
    """Return (ratio, level_price) if price is within tolerance_pct of a Fib level."""
    for ratio, level in levels.items():
        if level == 0:
            continue
        pct_diff = abs((price - level) / level) * 100
        if pct_diff <= tolerance_pct:
            return ratio, level
    return None

def is_at_fib_confluence(price: float, retr_levels: Dict[float, float], other_confirmation: bool = True, tolerance_pct: float = 0.15) -> Tuple[bool, Optional[float]]:
    """Check if price is at a key Fib retracement with confirmation.
    Focus on golden 0.618 and 0.5/0.382 for high probability.
    """
    closest = find_closest_fib_level(price, retr_levels, tolerance_pct)
    if closest:
        ratio, _ = closest
        if ratio in [0.5, 0.618, 0.382] and other_confirmation:
            return True, ratio
        if other_confirmation:
            return True, ratio
    return False, None

def get_fib_target(price: float, swing_high: float, swing_low: float, direction: str = 'long', target_ratio: float = 1.618) -> float:
    """Get Fib extension target."""
    ext_levels = calculate_extension_levels(swing_high, swing_low, direction)
    if target_ratio in ext_levels:
        return ext_levels[target_ratio]
    diff = abs(swing_high - swing_low)
    if direction == 'long':
        return price + diff * (target_ratio - 1)
    else:
        return price - diff * (target_ratio - 1)

def detect_recent_swing_high_low(prices: List[float], lookback: int = 20) -> Tuple[Optional[float], Optional[float]]:
    """Simple recent swing high/low detection from price list (use close prices)."""
    if len(prices) < lookback:
        return None, None
    recent = prices[-lookback:]
    swing_high = max(recent)
    swing_low = min(recent)
    return swing_high, swing_low

def get_fib_entry_signal(current_price: float, swing_high: float, swing_low: float, direction: str, other_ok: bool) -> Tuple[bool, Optional[float], Optional[str]]:
    """Master level entry signal using Fib.
    Returns (should_enter, fib_ratio, level_type)
    """
    if swing_high is None or swing_low is None:
        return False, None, None
    retr_levels = calculate_retracement_levels(swing_high, swing_low)
    at_fib, ratio = is_at_fib_confluence(current_price, retr_levels, other_ok)
    if at_fib and ratio in [0.382, 0.5, 0.618]:
        return True, ratio, 'retracement_support'
    return False, None, None

# For dashboard / logging
def format_fib_levels(levels: Dict[float, float]) -> str:
    return ", ".join([f"{r*100:.1f}%: {p:.2f}" for r, p in sorted(levels.items())])

print("HERMES Fibonacci Mastery Module loaded - ready to enhance entries, targets, and learning.")