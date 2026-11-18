"""GBrain - Central learning brain for HERMES trading bot.
Makes the learning process faster (in-memory buffer + atomic saves) 
and smoother (rich structured patterns from entry_type + close_reason, 
running averages, recent trades cache).
Used by hermes.py to record every closed trade automatically.
"""

import json
import os
from datetime import datetime

class GBrain:
    def __init__(self):
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.memory_file = os.path.join(self.here, "learning_memory.json")
        self.memory = self._load_memory()
        self.recent_trades = self.memory.get("recent_trades", [])[-50:]

    def _load_memory(self):
        default = {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "big_wins": 0,
            "top_patterns": [],
            "last_updated": None,
            "recent_trades": []
        }
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for k, v in default.items():
                    if k not in data:
                        data[k] = v
                return data
            except Exception:
                return default.copy()
        return default.copy()

    def _save(self):
        try:
            self.memory["last_updated"] = datetime.now().isoformat()
            self.memory["recent_trades"] = self.recent_trades[-50:]
            tmp = self.memory_file + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, indent=2)
            os.replace(tmp, self.memory_file)
        except Exception as e:
            print(f"GBrain save warning: {e}")

    def record_trade(self, trade: dict):
        """
        Record a closed trade for fast learning.
        trade dict must include:
          timestamp, symbol, direction, entry_type ('keltner', 'orb', or 'fib_618' etc),
          profit (float), close_reason
          Fib patterns now prioritized for faster/smoother learning of big winners.
        """
        self.recent_trades.append(trade)

        total = int(self.memory.get("total_trades", 0)) + 1
        self.memory["total_trades"] = total

        profit = float(trade.get("profit", 0.0))
        if profit > 0:
            wins = int(self.memory.get("wins", 0)) + 1
            self.memory["wins"] = wins
            if profit >= 5.0:
                self.memory["big_wins"] = int(self.memory.get("big_wins", 0)) + 1
            old_avg = float(self.memory.get("avg_win", 0.0))
            self.memory["avg_win"] = ((old_avg * (wins - 1)) + profit) / max(wins, 1)
        else:
            losses = int(self.memory.get("losses", 0)) + 1
            self.memory["losses"] = losses
            old_avg = float(self.memory.get("avg_loss", 0.0))
            self.memory["avg_loss"] = ((old_avg * (losses - 1)) + profit) / max(losses, 1)

        self.memory["win_rate"] = self.memory["wins"] / total if total > 0 else 0.0

        # Build rich pattern for smoother learning (Fib enhanced)
        entry = trade.get("entry_type", "keltner")
        close_r = trade.get("close_reason", "manual")
        pattern = f"{entry} + {close_r}"
        if "fib" in entry.lower():
            pattern = f"FIB_{entry} + {close_r}"
        patterns = self.memory.get("top_patterns", [])
        if pattern not in patterns:
            patterns.append(pattern)
            if len(patterns) > 5:
                patterns.pop(0)
            self.memory["top_patterns"] = patterns

        self._save()
        return round(self.memory["win_rate"] * 100, 1)

    def get_stats(self):
        return self.memory.copy()

    def get_recent_win_rate(self, n=5):
        if not self.recent_trades:
            return 0.0
        recent = self.recent_trades[-n:]
        wins = sum(1 for t in recent if float(t.get("profit", 0)) > 0)
        return wins / len(recent) if recent else 0.0
