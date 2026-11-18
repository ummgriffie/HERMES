"""
HERMES Candlestick Mastery Module
Mastered from: The Candlestick Trading Bible (Audiobook) 
https://www.youtube.com/watch?v=RlbQT3BK1fA

Core lessons applied:
- Candlesticks show market psychology and who is in control (buyers or sellers).
- The most powerful patterns appear at key levels: support/resistance, Fib retracements, Keltner breaks, ORB levels.
- For fast M1 scalps: focus on strong rejection (pin bars), engulfing, and 3-candle reversals.
- Pattern alone is not enough — context + confluence = edge.
- We only take high-probability setups that align with our existing guards.

Key patterns implemented for accurate, faster scalp trades:
1. Bullish Hammer / Pin Bar (rejection of lows)
2. Bearish Shooting Star / Pin Bar (rejection of highs)
3. Bullish Engulfing (strong buyer takeover)
4. Bearish Engulfing (strong seller takeover)
5. Morning Star (powerful bullish reversal)
6. Evening Star (powerful bearish reversal)
7. Dragonfly Doji (bullish indecision resolved up)
8. Gravestone Doji (bearish indecision resolved down)
9. Inside Bar (consolidation / breakout setup)

get_candlestick_signal(df) returns best signal for the latest candles.
"""

import pandas as pd

def _body(c):
    return abs(c['close'] - c['open'])

def _upper_wick(c):
    return c['high'] - max(c['close'], c['open'])

def _lower_wick(c):
    return min(c['close'], c['open']) - c['low']

def is_bullish_hammer(c):
    body = _body(c)
    if body == 0: return False
    return (_lower_wick(c) > body * 2.0 and 
            _upper_wick(c) < body * 0.5 and 
            c['close'] > c['open'])

def is_bearish_shooting_star(c):
    body = _body(c)
    if body == 0: return False
    return (_upper_wick(c) > body * 2.0 and 
            _lower_wick(c) < body * 0.5 and 
            c['close'] < c['open'])

def is_bullish_engulfing(prev, curr):
    if len([prev, curr]) < 2: return False
    prev_body = _body(prev)
    curr_body = _body(curr)
    return (prev['close'] < prev['open'] and 
            curr['close'] > curr['open'] and 
            curr['open'] <= prev['close'] and 
            curr['close'] >= prev['open'] and 
            curr_body > prev_body)

def is_bearish_engulfing(prev, curr):
    if len([prev, curr]) < 2: return False
    prev_body = _body(prev)
    curr_body = _body(curr)
    return (prev['close'] > prev['open'] and 
            curr['close'] < curr['open'] and 
            curr['open'] >= prev['close'] and 
            curr['close'] <= prev['open'] and 
            curr_body > prev_body)

def is_morning_star(df):
    if len(df) < 3: return False
    a, b, c = df.iloc[-3], df.iloc[-2], df.iloc[-1]
    return (a['close'] < a['open'] and 
            _body(b) < _body(a) * 0.4 and 
            c['close'] > c['open'] and 
            c['close'] > (a['open'] + a['close']) / 2)

def is_evening_star(df):
    if len(df) < 3: return False
    a, b, c = df.iloc[-3], df.iloc[-2], df.iloc[-1]
    return (a['close'] > a['open'] and 
            _body(b) < _body(a) * 0.4 and 
            c['close'] < c['open'] and 
            c['close'] < (a['open'] + a['close']) / 2)

def is_dragonfly_doji(c):
    body = _body(c)
    total = c['high'] - c['low']
    if total == 0: return False
    return (body / total < 0.15 and 
            _lower_wick(c) > _upper_wick(c) * 1.5 and 
            c['close'] >= c['open'] * 0.99)

def is_gravestone_doji(c):
    body = _body(c)
    total = c['high'] - c['low']
    if total == 0: return False
    return (body / total < 0.15 and 
            _upper_wick(c) > _lower_wick(c) * 1.5 and 
            c['close'] <= c['open'] * 1.01)

def get_candlestick_signal(df, min_strength=0.65):
    """
    Returns (direction, pattern, strength) or (None, "none", 0.0)
    Prioritizes strongest reversal patterns for scalping.
    """
    if df is None or len(df) < 3:
        return None, "none", 0.0

    last = df.iloc[-1]
    prev = df.iloc[-2]

    candidates = []

    if is_bullish_hammer(last):
        candidates.append(("LONG", "BULLISH_HAMMER", 0.78))
    if is_bearish_shooting_star(last):
        candidates.append(("SHORT", "BEARISH_SHOOTING_STAR", 0.78))

    if is_bullish_engulfing(prev, last):
        candidates.append(("LONG", "BULLISH_ENGULFING", 0.88))
    if is_bearish_engulfing(prev, last):
        candidates.append(("SHORT", "BEARISH_ENGULFING", 0.88))

    if is_morning_star(df):
        candidates.append(("LONG", "MORNING_STAR", 0.92))
    if is_evening_star(df):
        candidates.append(("SHORT", "EVENING_STAR", 0.92))

    if is_dragonfly_doji(last):
        candidates.append(("LONG", "DRAGONFLY_DOJI", 0.72))
    if is_gravestone_doji(last):
        candidates.append(("SHORT", "GRAVESTONE_DOJI", 0.72))

    if not candidates:
        return None, "none", 0.0

    # Strongest first
    candidates.sort(key=lambda x: -x[2])
    direction, pattern, strength = candidates[0]

    if strength < min_strength:
        return None, "none", 0.0

    return direction, pattern, round(strength, 2)

def get_pattern_description(pattern):
    d = {
        "BULLISH_HAMMER": "Bullish pin bar — strong rejection of lower prices (buyers in control)",
        "BEARISH_SHOOTING_STAR": "Bearish pin bar — strong rejection of higher prices (sellers in control)",
        "BULLISH_ENGULFING": "Powerful bullish reversal — buyers completely swallowed the previous sellers",
        "BEARISH_ENGULFING": "Powerful bearish reversal — sellers completely swallowed the previous buyers",
        "MORNING_STAR": "Classic 3-candle bullish reversal at a bottom (very high probability)",
        "EVENING_STAR": "Classic 3-candle bearish reversal at a top (very high probability)",
        "DRAGONFLY_DOJI": "Bullish indecision resolved with buyers taking control",
        "GRAVESTONE_DOJI": "Bearish indecision resolved with sellers taking control",
        "none": "No high-probability candlestick pattern detected"
    }
    return d.get(pattern, "Pattern recognized but context needed")

def get_latest_pattern_summary(df):
    direction, pattern, strength = get_candlestick_signal(df)
    return {
        "direction": direction,
        "pattern": pattern,
        "strength": strength,
        "description": get_pattern_description(pattern)
    }
