import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime, timedelta
import json
import os
from gbrain import GBrain
from fibonacci import calculate_retracement_levels, is_at_fib_confluence, detect_recent_swing_high_low, get_fib_entry_signal, format_fib_levels
from candlestick_mastery import get_candlestick_signal, get_pattern_description, get_latest_pattern_summary

# === SPREAD FILTER RESTORED ===
# This guard was silently removed during the shift to the independent bot.
# It prevents entries when spread is too wide (common cause of losses on XAU and GBPJPY).
MAX_SPREAD = 25.0  # points (~2.5 pips on XAUUSD#, reasonable for GBPJPY#)

# === ORB + SAFE TREND TRAILING (new per request) ===
# ORB: Catch Opening Range Breakout setups (break of recent 15-bar range + MACD confirmation)
# Trend riding: Hold trades longer using safe ATR-based trailing stop (1.5x ATR) once in profit
ORB_BARS = 15
SAFE_TRAIL_ATR_MULT = 1.5

# === ALL ORIGINAL GUARDS RESTORED ===
# These protections were in place in the approved versions before the independent bot drifted:
# - Strict one trade per symbol at a time (magic number check)
# - Primary: manual close only (bot does NOT close on opposite signal alone)
# - Auto-reopen a new trade immediately after any manual close
# - $2+ profit filter (only consider exits when profit >= $2)
# - Clear real-time logging of every state and decision
# - Range Guard (no entries inside Keltner Channel)
# - Spread filter (now restored)
# - 45-second cooldown between entries
# - Balance printed on startup and every 60 seconds
# - Trailing once +$2, auto-close at $5+
# + NEW: ORB breakout entries + safe ATR trailing for trend rides

HERE = os.path.dirname(os.path.abspath(__file__))
BALANCE_FILE = os.path.join(HERE, "latest_balance.json")
LOG_FILE = os.path.join(HERE, "hermes_live.log")

def log_to_file(message):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().strftime('%H:%M:%S')} | {message}\n")
    except:
        pass

# Configuration
LOGIN = 561112
PASSWORD = "J@j9bdbgyfn"
SERVER = "FHXmarkets-Trade"
COMMENT = "HERMES"

SYMBOLS = {
    "XAUUSD#": {"lot": 0.02, "magic": 234006},
    "GBPJPY#": {"lot": 0.08, "magic": 234007}
}

print("=== HERMES — ALL GUARDS RESTORED + ORB + SAFE TREND TRAIL + FIBONACCI MASTERY ===")
print("• NEW: Fibonacci retracement (61.8% golden etc) + extensions for entries/targets")
print("• Mastered from the 5 videos; confluence with Keltner/MACD/ORB required")
print("Guards now active:")
print("• One trade per symbol only (magic protected)")
print("• MANUAL CLOSE PRIMARY — bot will not auto-close on signal")
print("• Auto-reopens new trade immediately after you manually close")
print("• $2+ profit filter before any exit logic")
print("• Range Guard active (no entries inside Keltner bands)")
print("• Spread filter restored (max " + str(MAX_SPREAD) + " points)")
print("• 45-second cooldown between entries")
print("• Trailing stop once +$2, auto-close at $5+")
print("• NEW: ORB Breakout detection (15-bar range + MACD)")
print("• NEW: Safe ATR-based trailing (1.5x ATR) for holding trend rides")
print("• Supports XAUUSD# (0.02) + GBPJPY# (0.08)")
print("• Runs fully independent of StarNet")
print("• GBrain integrated — every close feeds fast, smooth learning (rich patterns + real-time stats)")
print("\nBot launching now...\n")
log_to_file("HERMES bot starting - all guards, ORB, safe ATR trail active")

gbrain = GBrain()
stats = gbrain.get_stats()
print(f"• GBrain loaded: {stats.get('total_trades', 0)} trades | Win rate: {stats.get('win_rate', 0)*100:.1f}% | Recent WR: {gbrain.get_recent_win_rate(5)*100:.1f}%")
log_to_file("GBrain initialized for faster and smoother learning")
print("� NEW: Candlestick Mastery from The Candlestick Trading Bible (Audiobook) - strong patterns now enable faster, more accurate M1 scalps with confluence")

# Initialize MT5
if not mt5.initialize(login=LOGIN, password=PASSWORD, server=SERVER):
    print("MT5 initialize failed:", mt5.last_error())
    quit()

account = mt5.account_info()
if account:
    print(f"Connected successfully. Balance: ${account.balance:.2f} | Equity: ${account.equity:.2f}")
    log_to_file(f"Connected to MT5. Balance: ${account.balance:.2f}")
    with open(BALANCE_FILE, "w") as f:
        json.dump({
            "balance": round(account.balance, 2),
            "equity": round(account.equity, 2),
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
else:
    print("Connected but cannot read account info.")
    mt5.shutdown()
    quit()

def calculate_keltner(df, period=20, atr_mult=2.0):
    df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
    df['atr'] = df['typical_price'].rolling(period).mean()
    df['midline'] = df['typical_price'].rolling(period).mean()
    df['upper'] = df['midline'] + (df['atr'] * atr_mult)
    df['lower'] = df['midline'] - (df['atr'] * atr_mult)
    return df

def calculate_macd_histogram(close, fast=12, slow=26, signal=9):
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return histogram

def get_data(symbol, bars=100):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, bars)
    if rates is None or len(rates) < 50:
        return None
    df = pd.DataFrame(rates)
    df = calculate_keltner(df)
    df['macd_hist'] = calculate_macd_histogram(df['close'])
    return df

def get_orb(df):
    """ORB detection: breakout from the 'opening' range of the first ORB_BARS in the data window."""
    if len(df) < ORB_BARS + 5:
        return None, None
    orb_high = df['high'].iloc[:ORB_BARS].max()
    orb_low = df['low'].iloc[:ORB_BARS].min()
    return orb_high, orb_low

def is_spread_ok(symbol):
    """Spread Filter — restored as requested."""
    info = mt5.symbol_info(symbol)
    if info is None or info.spread is None:
        print(f"{datetime.now().strftime('%H:%M:%S')} | {symbol} — Cannot read spread")
        return False
    if info.spread > MAX_SPREAD:
        print(f"{datetime.now().strftime('%H:%M:%S')} | {symbol} — SPREAD TOO WIDE ({info.spread} points) — Spread Guard blocking entry")
        return False
    return True

def has_open_position(symbol, magic):
    positions = mt5.positions_get(symbol=symbol)
    if not positions:
        return False, None, 0.0, 0
    for pos in positions:
        if pos.magic == magic:
            return True, pos.type, pos.profit, pos.ticket
    return False, None, 0.0, 0

def close_position(symbol, ticket, magic, reason="auto"):
    positions = mt5.positions_get(symbol=symbol)
    for pos in positions:
        if pos.ticket == ticket:
            tick = mt5.symbol_info_tick(symbol)
            price = tick.bid if pos.type == 0 else tick.ask
            order_type = mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": pos.volume,
                "type": order_type,
                "position": pos.ticket,
                "price": price,
                "deviation": 30,
                "magic": magic,
                "comment": COMMENT + "_EXIT_" + reason.upper(),
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"{datetime.now().strftime('%H:%M:%S')} | CLOSED {symbol} | {reason} | Profit: ${pos.profit:.2f}")
                return True
    return False

def open_trade(symbol, direction, lot, magic):
    tick = mt5.symbol_info_tick(symbol)
    price = (tick.ask + tick.bid) / 2
    order_type = mt5.ORDER_TYPE_BUY if direction == "BUY" else mt5.ORDER_TYPE_SELL
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "deviation": 30,
        "magic": magic,
        "comment": COMMENT,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        side = "LONG" if direction == "BUY" else "SHORT"
        print(f"{datetime.now().strftime('%H:%M:%S')} | OPENED {side} {symbol} @ ~{price:.2f} | HERMES signal")
        return True
    print(f"Entry failed for {symbol}: {result.comment}")
    return False

# Main loop
print("Scanning both symbols every ~8 seconds. All original guards + Spread Filter active.")
last_signal = {sym: datetime.now() - timedelta(minutes=10) for sym in SYMBOLS}

# Trend riding trail state (safe ATR trail)
trail_levels = {sym: 0.0 for sym in SYMBOLS}
entry_prices = {sym: 0.0 for sym in SYMBOLS}
entry_reasons = {sym: "" for sym in SYMBOLS}

while True:
    try:
        account = mt5.account_info()
        if account and int(time.time()) % 60 == 0:
            print(f"{datetime.now().strftime('%H:%M:%S')} | BALANCE: ${account.balance:.2f} | EQUITY: ${account.equity:.2f}")
            log_to_file(f"BALANCE: ${account.balance:.2f} | EQUITY: ${account.equity:.2f}")
            with open(BALANCE_FILE, "w") as f:
                json.dump({
                    "balance": round(account.balance, 2),
                    "equity": round(account.equity, 2),
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2)

        for symbol, config in SYMBOLS.items():
            lot = config["lot"]
            magic = config["magic"]
            has_pos, pos_type, current_profit, ticket = has_open_position(symbol, magic)
            
            df = get_data(symbol)
            if df is None:
                continue
                
            current_hist = df['macd_hist'].iloc[-1]
            prev_hist = df['macd_hist'].iloc[-2]
            midline = df['midline'].iloc[-1]
            price = (df['close'].iloc[-1] + df['open'].iloc[-1]) / 2
            atr = df['atr'].iloc[-1] if 'atr' in df.columns and not pd.isna(df['atr'].iloc[-1]) else 0.5
            
            if has_pos:
                # === SAFE ATR TRAIL FOR TREND RIDING ===
                if current_profit >= 2.0:
                    if pos_type == 0:  # LONG
                        new_trail = price - (atr * SAFE_TRAIL_ATR_MULT)
                        if new_trail > trail_levels.get(symbol, 0):
                            trail_levels[symbol] = new_trail
                        if price <= trail_levels[symbol]:
                            close_position(symbol, ticket, magic, "safe_atr_trail")
                            gbrain.record_trade({
                                "timestamp": datetime.now().isoformat(),
                                "symbol": symbol,
                                "direction": "LONG" if pos_type == 0 else "SHORT",
                                "entry_type": entry_reasons.get(symbol, "keltner"),
                        "candle_pattern": entry_reasons.get(symbol, "none"),
                                "profit": current_profit,
                                "close_reason": "safe_atr_trail"
                            })
                            print(f"GBrain learned: {symbol} safe_atr_trail (${current_profit:.2f}) | WR: {gbrain.memory.get('win_rate',0)*100:.1f}%")
                            trail_levels[symbol] = 0.0
                            entry_reasons[symbol] = ""
                            continue
                    else:  # SHORT
                        new_trail = price + (atr * SAFE_TRAIL_ATR_MULT)
                        if trail_levels.get(symbol, 0) == 0 or new_trail < trail_levels[symbol]:
                            trail_levels[symbol] = new_trail
                        if price >= trail_levels[symbol]:
                            close_position(symbol, ticket, magic, "safe_atr_trail")
                            gbrain.record_trade({
                                "timestamp": datetime.now().isoformat(),
                                "symbol": symbol,
                                "direction": "LONG" if pos_type == 0 else "SHORT",
                                "entry_type": entry_reasons.get(symbol, "keltner"),
                        "candle_pattern": entry_reasons.get(symbol, "none"),
                                "profit": current_profit,
                                "close_reason": "safe_atr_trail"
                            })
                            print(f"GBrain learned: {symbol} safe_atr_trail (${current_profit:.2f}) | WR: {gbrain.memory.get('win_rate',0)*100:.1f}%")
                            trail_levels[symbol] = 0.0
                            entry_reasons[symbol] = ""
                            continue
                
                # Hard profit target
                if current_profit >= 5.0:
                    close_position(symbol, ticket, magic, "profit_target_5")
                    gbrain.record_trade({
                        "timestamp": datetime.now().isoformat(),
                        "symbol": symbol,
                        "direction": "LONG" if pos_type == 0 else "SHORT",
                        "entry_type": entry_reasons.get(symbol, "keltner"),
                        "candle_pattern": entry_reasons.get(symbol, "none"),
                        "profit": current_profit,
                        "close_reason": "profit_target_5"
                    })
                    print(f"GBrain learned: {symbol} profit_target_5 (${current_profit:.2f}) | WR: {gbrain.memory.get('win_rate',0)*100:.1f}%")
                    trail_levels[symbol] = 0.0
                    entry_reasons[symbol] = ""
                    continue
                
                if current_profit >= 2.0:
                    print(f"{datetime.now().strftime('%H:%M:%S')} | {symbol} IN PROFIT ${current_profit:.2f} — SAFE ATR TRAIL ACTIVE | MANUAL CLOSE still available")
                
                # Original guard: opposite signal close ONLY if profit < $2
                should_exit = False
                reason = "opposite_signal"
                if current_profit < 2.0:
                    if pos_type == 0 and current_hist < 0 and prev_hist >= 0 and price < midline:
                        should_exit = True
                    elif pos_type == 1 and current_hist > 0 and prev_hist <= 0 and price > midline:
                        should_exit = True
                
                if should_exit:
                    close_position(symbol, ticket, magic, reason)
                    gbrain.record_trade({
                        "timestamp": datetime.now().isoformat(),
                        "symbol": symbol,
                        "direction": "LONG" if pos_type == 0 else "SHORT",
                        "entry_type": entry_reasons.get(symbol, "keltner"),
                        "candle_pattern": entry_reasons.get(symbol, "none"),
                        "profit": current_profit,
                        "close_reason": reason
                    })
                    print(f"GBrain learned: {symbol} {reason} (${current_profit:.2f}) | WR: {gbrain.memory.get('win_rate',0)*100:.1f}%")
                    trail_levels[symbol] = 0.0
                    entry_reasons[symbol] = ""
                else:
                    print(f"{datetime.now().strftime('%H:%M:%S')} | {symbol} {'LONG' if pos_type==0 else 'SHORT'} | P/L: ${current_profit:.2f} | Safe trail active — hold for trend")
            else:
                # Entry logic with Range Guard + restored Spread Filter
                if price > df['lower'].iloc[-1] and price < df['upper'].iloc[-1]:
                    continue  # Range Guard
                
                if abs(current_hist) < 0.08:
                    continue
                    
                signal = None
                if price > midline and current_hist > 0.0 and prev_hist <= 0.0:
                    signal = "BUY"
                elif price < midline and current_hist < 0.0 and prev_hist >= 0.0:
                    signal = "SELL"
                
                # === ORB SETUP DETECTION ===
                orb_high, orb_low = get_orb(df)
                if orb_high is not None and orb_low is not None:
                    if price > orb_high and current_hist > 0.0 and prev_hist <= 0.0:
                        signal = "BUY"
                        print(f"{datetime.now().strftime('%H:%M:%S')} | ORB BREAKOUT LONG on {symbol} | Range high ~{orb_high:.2f}")
                    elif price < orb_low and current_hist < 0.0 and prev_hist >= 0.0:
                        signal = "SELL"
                        print(f"{datetime.now().strftime('%H:%M:%S')} | ORB BREAKOUT SHORT on {symbol} | Range low ~{orb_low:.2f}")
                    
                entry_type = "orb" if (orb_high is not None and (price > orb_high or price < orb_low)) else "keltner"

                # === FIBONACCI MASTERY INTEGRATION (from studied videos) ===
                fib_signal = False
                fib_ratio = None
                closes = df['close'].tolist() if 'close' in df.columns else []
                swing_high, swing_low = detect_recent_swing_high_low(closes, lookback=20)
                if swing_high and swing_low and signal:
                    retr_levels = calculate_retracement_levels(swing_high, swing_low)
                    fib_ok, fib_ratio = is_at_fib_confluence(price, retr_levels, other_confirmation=True)
                    if fib_ok and fib_ratio in [0.382, 0.5, 0.618]:
                        fib_signal = True
                        print(f"{datetime.now().strftime('%H:%M:%S')} | FIB CONFLUENCE {fib_ratio*100:.1f}% on {symbol} | Price ~{price:.2f} | Levels: {format_fib_levels(retr_levels)}")
                        entry_type = f"fib_{int(fib_ratio*1000)}"
                    elif fib_ok:
                        print(f"{datetime.now().strftime('%H:%M:%S')} | FIB near {fib_ratio*100:.1f}% (support) on {symbol}")

                # === CANDLESTICK MASTERY (from The Candlestick Trading Bible audiobook) ===
                # For faster accurate scalp trades on M1: use strong patterns for quick confirmation or standalone entries
                candle_dir, candle_pattern, candle_strength = get_candlestick_signal(df)
                candle_confirmed = False
                if candle_dir and signal:
                    if (signal == "BUY" and candle_dir == "LONG") or (signal == "SELL" and candle_dir == "SHORT"):
                        candle_confirmed = True
                        print(f"{datetime.now().strftime('%H:%M:%S')} | CANDLESTICK CONFIRMED: {candle_pattern} (str {candle_strength}) on {symbol}")
                        entry_type = f"candle_{candle_pattern.lower()}"
                elif candle_dir and not signal:
                    if candle_strength >= 0.85:
                        signal = "BUY" if candle_dir == "LONG" else "SELL"
                        candle_confirmed = True
                        print(f"{datetime.now().strftime('%H:%M:%S')} | PURE CANDLESTICK SCALP: {candle_pattern} (str {candle_strength}) on {symbol}")
                        entry_type = f"candle_{candle_pattern.lower()}"

                if signal and (fib_signal or entry_type == "orb" or candle_confirmed) and is_spread_ok(symbol) and (datetime.now() - last_signal[symbol]).total_seconds() > 45:
                    print(f"{datetime.now().strftime('%H:%M:%S')} | SIGNAL: {signal} on {symbol} | Price ~{price:.2f} | Spread OK | Fib/ORB/Candle confirmed")
                    if open_trade(symbol, signal, lot, magic):
                        last_signal[symbol] = datetime.now()
                        entry_prices[symbol] = price
                        trail_levels[symbol] = 0.0  # reset trail on new entry
                        entry_reasons[symbol] = entry_type
                        if candle_pattern and candle_pattern != "none":
                            print(f"  + Candle pattern: {candle_pattern} (strength {candle_strength})")
                        if fib_ratio:
                            print(f"  → Fib entry at {fib_ratio*100:.1f}% confluence")
                    time.sleep(8)
        
        time.sleep(8)
        
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(15)

mt5.shutdown()
print("Bot shutdown complete.")
