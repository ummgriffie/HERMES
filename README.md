# HERMES

**HERMES** is an advanced, independent algorithmic trading bot built for MetaTrader 5 (MT5). It combines multiple proven strategies (Keltner Channel + MACD, Order Block Range (ORB), Fibonacci retracements/extensions, candlestick patterns) with a fast-learning memory system (GBrain) to improve over time.

The project includes a real-time interactive dashboard styled after StarNetOS (pixel-art arcade station with walking agent sprite), Telegram signal broadcasting, and strict risk management.

## Key Features

- **Multi-Strategy Engine** (`hermes.py`):
  - Keltner Channel + MACD core
  - ORB breakout detection
  - Fibonacci confluence (61.8% golden ratio, extensions)
  - Candlestick pattern recognition (Hammer, Engulfing, Stars, Doji, etc.)
  - Safe ATR-based trailing stops + $5 profit auto-close
  - Range Guard + Spread Filter

- **Learning System** (`gbrain.py`):
  - Records every trade with entry_type, close_reason, and outcome
  - Tracks win rate, top patterns, recent performance
  - Used to bias future entries toward high-probability setups

- **Dashboard** (`dashboard.py` + `render_dashboard/`):
  - Live StarNetOS arcade-style UI with interactive canvas sprite
  - Equity curve (histogram), market strength bars (orange weak → blue strong)
  - Signals terminal, GBrain stats, bot log
  - One-page clean layout with proper spacing
  - PWA-ready for iPhone (add to home screen)

- **Signals & Monitoring**:
  - Telegram signal watcher and sender
  - Live MT5 connection checks
  - Balance/equity tracking

- **Render.com Ready Web Version**:
  - Static modern dashboard in `render_dashboard/`
  - Deploy as static site for remote access

## Supported Symbols
- XAUUSD# (0.02 lot)
- GBPJPY# (0.08 lot)
- (Easily extensible)

## Requirements
- Python 3.10+
- MetaTrader 5 terminal running with your account
- `pip install -r requirements.txt`

## Quick Start (Local Bot)

1. Clone the repo
2. `cd HERMES`
3. `pip install -r requirements.txt`
4. Ensure MT5 is open and logged in
5. `python hermes.py`  (or use `run_live_mt5.bat` / `run_dashboard.bat`)

## Dashboard

- Local: `cd trading_bot && streamlit run dashboard.py`
- Web version: Deploy `render_dashboard/` as static site on Render.com

## Risk & Philosophy
- Strict $2+ profit filter before considering exits
- One trade per symbol at a time
- Manual close is primary; bot only trails or hits hard $5 cap
- All decisions logged for review and learning

## Project Structure
```
HERMES/
├── hermes.py                 # Main trading bot
├── gbrain.py                 # Learning & memory brain
├── fibonacci.py
├── candlestick_mastery.py
├── dashboard.py              # Local StarNetOS arcade dashboard
├── render_dashboard/         # Modern web/PWA dashboard (for Render)
├── requirements.txt
├── .gitignore
├── README.md
└── trading_bot/              # Supporting scripts & legacy
```

## Notes
- This is an independent bot (survives closing StarNet/terminal).
- Never commit real account credentials or Telegram tokens.
- Always test in demo first.

Built iteratively with focus on consistency, learning, and clean risk management.

---

**Status**: Active development. Currently trading XAUUSD# and GBPJPY# on M1 with confluence-based entries.
