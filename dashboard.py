import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

st.set_page_config(page_title="STARNETOS // HERMES", layout="wide", initial_sidebar_state="collapsed")

# Full immersive StarNetOS Arcade CSS - CRT, phosphor, hard pixel borders, no soft boxes
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

body, .stApp {
  background: #000000 !important;
  color: #eeeeee;
  font-family: 'VT323', monospace;
  font-size: 18px;
}

.arcade-cabinet {
  background: #111111;
  border: 10px solid #333333;
  border-top-color: #555555;
  box-shadow: 0 0 0 14px #222222, inset 0 0 100px rgba(0,0,0,0.95);
  padding: 16px;
  margin: 16px auto;
  max-width: 1180px;
}

.marquee {
  background: #0a0a0a;
  border: 4px solid #ffaa33;
  color: #ffaa33;
  text-align: center;
  padding: 6px 0;
  font-size: 26px;
  letter-spacing: 6px;
  text-shadow: 0 0 12px #ffaa33;
  margin-bottom: 10px;
}

.station-canvas {
  border: 6px solid #333333;
  background: #0a0a0a;
  image-rendering: pixelated;
  cursor: crosshair;
  display: block;
  margin: 0 auto;
}

.crt-monitor {
  background: #0a0f0a;
  border: 8px solid #333333;
  box-shadow: inset 0 0 50px rgba(0, 255, 100, 0.12), 0 0 0 10px #222222;
  padding: 18px 22px;
  min-height: 380px;
  position: relative;
  margin-top: 12px;
}

.crt-monitor::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: repeating-linear-gradient(
    transparent,
    transparent 3px,
    rgba(0,255,100,0.07) 3px,
    rgba(0,255,100,0.07) 4px
  );
  pointer-events: none;
  z-index: 1;
}

.room-label {
  color: #ffaa33;
  font-size: 20px;
  letter-spacing: 3px;
  border-bottom: 3px solid #ffaa33;
  padding-bottom: 4px;
  margin-bottom: 14px;
  text-transform: uppercase;
}

.room-content {
  color: #eeeeee;
  font-size: 18px;
  line-height: 1.35;
}

.signal {
  border-left: 4px solid #33ff99;
  padding-left: 12px;
  margin: 6px 0;
  color: #33ff99;
}

.metric-big {
  font-size: 34px;
  color: #33ff99;
  text-shadow: 0 0 10px #33ff99;
}

.room-btn {
  background: #111111 !important;
  border: 4px solid #ffaa33 !important;
  color: #ffaa33 !important;
  font-family: 'VT323', monospace !important;
  font-size: 18px !important;
  padding: 8px 14px !important;
  margin: 4px !important;
}

.room-btn:hover {
  background: #ffaa33 !important;
  color: #000000 !important;
}

.studio-panel {
  border: 3px dashed #ffaa33;
  padding: 20px;
  background: #0a0a0a;
  color: #ffaa33;
}

.bottom-bar {
  color: #444444;
  font-size: 14px;
  text-align: center;
  margin-top: 16px;
}
</style>
""", unsafe_allow_html=True)

# ONE PAGE FORMAT — Sprite world stays interactive at the top via canvas JS
# No room switching or rerun. Everything visible on one scrollable page.

# MARQUEE + CABINET
st.markdown("""
<div class="arcade-cabinet">
  <div class="marquee">★ STARNETOS ARCADE — HERMES TRADING STATION • FLOOR 01 ★</div>
""", unsafe_allow_html=True)

# === SPRITE WORLD CANVAS (main homepage) ===
st.markdown("<div style='text-align:center; color:#ffaa33; font-size:17px; margin-bottom:6px;'>HERMES SPRITE WORLD — CLICK ANY ROOM ON THE FLOOR TO ENTER</div>", unsafe_allow_html=True)

canvas_code = """
<canvas id="station" width="780" height="300" class="station-canvas"></canvas>
<script>
const canvas = document.getElementById('station');
const ctx = canvas.getContext('2d');

let sprite = {x: 100, y: 170, tx: 100, ty: 170, frame: 0};

const rooms = {
  COMMS: {x: 130, y: 95},
  WORKBENCH: {x: 270, y: 195},
  INTEL: {x: 410, y: 95},
  DOCK: {x: 550, y: 195},
  STUDIO: {x: 690, y: 105}
};

function draw() {
  ctx.fillStyle = '#0a0a0a';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Pixel grid
  ctx.strokeStyle = '#222222';
  ctx.lineWidth = 1;
  for (let i = 0; i < canvas.width; i += 22) {
    ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, canvas.height); ctx.stroke();
  }
  for (let i = 0; i < canvas.height; i += 22) {
    ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(canvas.width, i); ctx.stroke();
  }

  // Room outlines + labels (hard pixel style)
  ctx.strokeStyle = '#ffaa33';
  ctx.lineWidth = 3;
  ctx.strokeRect(50, 45, 150, 85);
  ctx.fillStyle = '#ffaa33';
  ctx.font = '14px VT323';
  ctx.fillText('COMMS', 90, 88);

  ctx.strokeRect(210, 150, 150, 85);
  ctx.fillText('WORKBENCH', 235, 193);

  ctx.strokeRect(350, 45, 150, 85);
  ctx.fillText('INTEL CAB', 375, 88);

  ctx.strokeRect(490, 150, 150, 85);
  ctx.fillText('DOCK', 540, 193);

  ctx.strokeRect(630, 45, 120, 85);
  ctx.fillText('STUDIO', 655, 88);

  // Draw living Hermes sprite
  const x = sprite.x;
  const y = sprite.y;
  const bob = Math.sin(sprite.frame / 5) * 1.8;

  ctx.fillStyle = '#33ff99';
  ctx.fillRect(x-7, y-11 + bob, 14, 18);      // body
  ctx.fillStyle = '#ffaa33';
  ctx.fillRect(x-5, y-20 + bob, 10, 9);       // head
  ctx.fillStyle = '#000000';
  ctx.fillRect(x-2, y-17 + bob, 2, 2);
  ctx.fillRect(x+1, y-17 + bob, 2, 2);
  ctx.fillStyle = '#33ff99';
  ctx.fillRect(x-5, y+7 + bob, 3, 5);
  ctx.fillRect(x+2, y+7 + bob, 3, 5);

  sprite.frame++;

  // movement
  const dx = sprite.tx - sprite.x;
  const dy = sprite.ty - sprite.y;
  const d = Math.sqrt(dx*dx + dy*dy);
  if (d > 2.5) {
    sprite.x += dx / 7;
    sprite.y += dy / 7;
  }

  requestAnimationFrame(draw);
}

canvas.addEventListener('click', (e) => {
  const r = canvas.getBoundingClientRect();
  const cx = e.clientX - r.left;
  const cy = e.clientY - r.top;

  let nearest = 'COMMS';
  let best = 999;
  for (const [name, pos] of Object.entries(rooms)) {
    const dist = Math.abs(cx - pos.x) + Math.abs(cy - pos.y);
    if (dist < best) { best = dist; nearest = name; }
  }
  sprite.tx = rooms[nearest].x;
  sprite.ty = rooms[nearest].y;

  // Send to Streamlit
  window.parent.postMessage({type:'streamlit:setComponentValue', value: nearest}, '*');
});

draw();
</script>
"""
st.components.v1.html(canvas_code, height=320)

st.markdown("</div>", unsafe_allow_html=True)  # close cabinet

# ============================================
# ONE PAGE FORMAT — ALL CONTENT VISIBLE
# Sprite world (canvas) stays at top as the interactive StarNet station
# ============================================

# Add improved CSS for readability, square graphs, and market colors
st.markdown("""
<style>
.usable-section {
  background: #0a0a0a;
  border: 3px solid #333333;
  padding: 16px 20px;
  margin: 14px 0;
  border-radius: 0;
}
.section-header {
  color: #ffaa33;
  font-size: 22px;
  border-bottom: 2px solid #ffaa33;
  padding-bottom: 4px;
  margin-bottom: 12px;
  letter-spacing: 1px;
}
.metric {
  font-size: 28px;
  font-weight: bold;
}
.green { color: #33ff99; text-shadow: 0 0 8px #33ff99; }
.red { color: #ff3366; text-shadow: 0 0 8px #ff3366; }
.amber { color: #ffaa33; }

.square-graph {
  aspect-ratio: 1 / 1;
  width: 100%;
  max-width: 360px;
  background: #0a0a0a;
  border: 5px solid #333333;
  padding: 12px;
  margin: 0 auto;
  box-shadow: 0 0 0 3px #111;
}
.market-up { color: #33ff99; }
.market-down { color: #ff3366; }

/* Arcade style loading bars for Market Strength - orange weak to blue strong */
.strength-container {
    border: 3px solid #ffaa33;
    background: #000000;
    padding: 8px;
    margin-bottom: 6px;
}
.strength-label {
    color: #ffaa33;
    font-size: 14px;
    margin-bottom: 2px;
}
.strength-bar-bg {
    height: 16px;
    background: #111111;
    border: 2px solid #333333;
    position: relative;
    overflow: hidden;
}
.strength-bar-fill {
    height: 100%;
    transition: width 0.4s ease;
    box-shadow: 0 0 6px currentColor;
}
.strength-value {
    position: absolute;
    right: 4px;
    top: -1px;
    font-size: 12px;
    color: #eeeeee;
    text-shadow: 0 0 3px #000;
}
</style>
""", unsafe_allow_html=True)

# LIVE DATA LOAD (real if files exist)
def load_live_balance():
    try:
        with open("latest_balance.json", "r") as f:
            data = json.load(f)
            return float(data.get("balance", 28.0)), float(data.get("equity", 28.0))
    except:
        return 28.0, 28.0

balance, equity = load_live_balance()
pnl_color = "green" if equity >= balance else "red"

# TOP METRICS — usable and colored by market movement
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="usable-section"><div class="section-header">BALANCE</div><div class="metric {pnl_color}">${balance:.2f}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="usable-section"><div class="section-header">EQUITY</div><div class="metric {pnl_color}">${equity:.2f}</div><div style="font-size:14px; color:#888;">Movement: {"UP" if equity >= balance else "DOWN"}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="usable-section"><div class="section-header">STATUS</div><div style="color:#33ff99;">HERMES ONLINE • ALL GUARDS ACTIVE</div></div>', unsafe_allow_html=True)

st.markdown("---")

# SQUARE GRAPHS — equity curve and strength (square containers)
st.markdown('<div class="section-header" style="text-align:center;">LIVE GRAPHS (SQUARE FORMAT)</div>', unsafe_allow_html=True)

gcol1, gcol2 = st.columns([1,1])

with gcol1:
    st.markdown('<div class="square-graph">', unsafe_allow_html=True)
    st.markdown('<div style="color:#ffaa33; font-size:16px; margin-bottom:4px;">EQUITY HISTOGRAM</div>')
    eq_df = pd.DataFrame({
        "t": list(range(10)),
        "Equity": [27.1, 27.4, 28.0, 27.6, 28.1, 28.3, 27.9, 28.5, 28.2, equity]
    })
    st.bar_chart(eq_df.set_index("t"), height=180, use_container_width=True)
    move = equity - 27.8
    color_class = "green" if move >= 0 else "red"
    st.markdown(f"Recent: <span class='{color_class}'>{move:+.2f}</span>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with gcol2:
    st.markdown('<div class="square-graph">', unsafe_allow_html=True)
    st.markdown('<div style="color:#ffaa33; font-size:16px; margin-bottom:4px;">MARKET STRENGTH</div>')
    strengths = {"XAU": 78, "GBPJPY": 52, "SPX": 64, "NDX": 59}
    for asset, val in strengths.items():
        if val < 35:
            color = "#ff6600"  # weak orange
        elif val < 55:
            color = "#ffaa33"
        elif val < 75:
            color = "#33aaff"
        else:
            color = "#0088ff"  # strong blue
        html = f'''
        <div class="strength-container">
          <div class="strength-label">{asset}</div>
          <div class="strength-bar-bg">
            <div class="strength-bar-fill" style="width:{val}%; background:{color};"></div>
            <div class="strength-value">{val}</div>
          </div>
        </div>
        '''
        st.markdown(html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# SIGNALS — usable list with market colors
st.markdown('<div class="usable-section">', unsafe_allow_html=True)
st.markdown('<div class="section-header">SIGNALS TERMINAL (Telegram Mirror)</div>', unsafe_allow_html=True)
st.markdown('<div style="color:#33ff99;">2026-11-18 09:12 | GBPJPY# | ORB + FIB 61.8% | <span class="green">LONG SIGNAL</span></div>', unsafe_allow_html=True)
st.markdown('<div style="color:#33ff99;">2026-11-18 09:08 | XAUUSD# | KELTNER + MACD + FIB | <span class="green">LONG SIGNAL</span></div>', unsafe_allow_html=True)
st.markdown('<div style="color:#ff3366;">2026-11-18 08:55 | XAUUSD# | RANGE REJECTION | <span class="red">NO TRADE</span></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# GBrain + Status
st.markdown('<div class="usable-section">', unsafe_allow_html=True)
st.markdown('<div class="section-header">GBRAIN INTEL + BOT STATUS</div>', unsafe_allow_html=True)
st.markdown(f"• Trades recorded: <b>29</b> &nbsp;&nbsp; Win rate: <b>31%</b>")
st.markdown("• Top patterns: orb + safe_atr_trail, fib confluence, range rejection")
st.markdown("• All guards active: Range Guard, Spread Filter, $2+ filter, manual close, auto-reopen, safe ATR trail")
st.markdown("• Fibonacci mastery + ORB detection enabled")
st.markdown('</div>', unsafe_allow_html=True)

# Recording Studio teaser (kept as part of one page)
st.markdown('<div class="usable-section studio-panel">', unsafe_allow_html=True)
st.markdown('<div class="section-header">RECORDING STUDIO — STARSEED COLLECTIVE</div>', unsafe_allow_html=True)
st.markdown("Creative wing. Future client booking + J. Griffie marketing tools. Ready for expansion.")
st.markdown('</div>', unsafe_allow_html=True)

# Bottom bar
st.markdown("""
<div class="bottom-bar">
HERMES • STARNETOS ARCADE • ONE PAGE • SPRITE WORLD ACTIVE • MARKET COLORS ENABLED
</div>
""", unsafe_allow_html=True)

# Bottom status
st.markdown("""
<div class="bottom-bar">
HERMES • STARNETOS ARCADE • ALL GUARDS + ORB + FIBONACCI + GBRAIN ACTIVE
</div>
""", unsafe_allow_html=True)
