"""
╔══════════════════════════════════════════════════════════════╗
║          ForexBot AI — Intelligent Forex Analyzer            ║
║         Powered by Google Gemini + Real-time Market Data     ║
║                   Built with Streamlit                       ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
from google import genai
from google.genai import types as genai_types
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import yfinance as yf
from typing import Optional, Dict, List, Generator

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="ForexBot AI — Forex Analyzer",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/yourusername/forex-ai-analyzer",
        "About": "ForexBot AI — Intelligent Forex Analyzer powered by Google Gemini",
    },
)

# ============================================================
# INSTRUMENTS REGISTRY
# ============================================================
MAJOR_PAIRS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "USD/CHF": "USDCHF=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CAD": "USDCAD=X",
    "NZD/USD": "NZDUSD=X",
}

CROSS_PAIRS = {
    "EUR/GBP": "EURGBP=X",
    "EUR/JPY": "EURJPY=X",
    "GBP/JPY": "GBPJPY=X",
    "AUD/JPY": "AUDJPY=X",
    "EUR/AUD": "EURAUD=X",
    "EUR/CAD": "EURCAD=X",
}

COMMODITIES = {
    "XAU/USD (Gold)": "GC=F",
    "XAG/USD (Silver)": "SI=F",
    "WTI Crude Oil": "CL=F",
}

CATEGORY_MAP = {
    "Major Pairs 💱": MAJOR_PAIRS,
    "Cross Pairs 🔀": CROSS_PAIRS,
    "Commodities 🪙": COMMODITIES,
}

TIMEFRAMES = {
    "1 Day":    {"period": "1d",  "interval": "5m"},
    "5 Days":   {"period": "5d",  "interval": "15m"},
    "1 Month":  {"period": "1mo", "interval": "1h"},
    "3 Months": {"period": "3mo", "interval": "1d"},
    "6 Months": {"period": "6mo", "interval": "1d"},
    "1 Year":   {"period": "1y",  "interval": "1wk"},
}

RATE_CURRENCIES = [
    "EUR", "GBP", "JPY", "CHF",
    "AUD", "CAD", "NZD", "SGD",
    "CNY", "HKD",
]

# ============================================================
# CUSTOM CSS — DARK TRADING TERMINAL THEME
# ============================================================
DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }

/* ───── Background ───── */
.stApp                      { background-color: #080d14; }
.main .block-container      { padding-top: 0.5rem; max-width: 100%; padding-left: 1.5rem; padding-right: 1.5rem; }

/* ───── Header ───── */
.fx-header {
    background: linear-gradient(135deg, #080d14 0%, #0d1b2a 60%, #091520 100%);
    border-bottom: 2px solid #00c9a7;
    padding: 1.2rem 2rem;
    margin: -0.5rem -1.5rem 1.5rem -1.5rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
}
.fx-logo       { font-size: 2.8rem; }
.fx-title      { font-size: 1.6rem; font-weight: 700; color: #fff; margin: 0; letter-spacing: -0.02em; }
.fx-subtitle   { font-size: 0.78rem; color: #5a8fa8; margin: 0; font-family: 'JetBrains Mono', monospace; }
.fx-live {
    color: #00c9a7; font-size: 0.7rem; font-family: 'JetBrains Mono', monospace;
    background: rgba(0,201,167,0.1); border: 1px solid rgba(0,201,167,0.3);
    border-radius: 4px; padding: 2px 8px;
}

/* ───── Sidebar Brand ───── */
.sidebar-brand {
    text-align: center; padding: 1rem 0 0.8rem;
    border-bottom: 1px solid rgba(0,201,167,0.15);
    margin-bottom: 0.8rem;
}
.sidebar-brand-icon    { font-size: 2.2rem; }
.sidebar-brand-name    { font-weight: 700; color: #00c9a7; font-size: 1rem; margin: 0; }
.sidebar-brand-tagline { color: #4a6080; font-size: 0.72rem; margin: 0; font-family: 'JetBrains Mono', monospace; }

/* ───── Rate Cards ───── */
.rate-card {
    background: linear-gradient(135deg, #0d1b2a, #0a1628);
    border: 1px solid rgba(0,201,167,0.12);
    border-radius: 10px;
    padding: 0.65rem 1rem;
    margin-bottom: 0.35rem;
    transition: border-color 0.2s;
}
.rate-card:hover         { border-color: rgba(0,201,167,0.35); }
.rate-pair-label         { font-family: 'JetBrains Mono', monospace; font-size: 0.70rem; color: #5a8fa8; margin: 0; }
.rate-price              { font-family: 'JetBrains Mono', monospace; font-size: 1rem; font-weight: 600; color: #e8f0f7; margin: 0; }

/* ───── Signal Badges ───── */
.signal {
    display: inline-block;
    padding: 0.15rem 0.65rem;
    border-radius: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.70rem;
    font-weight: 600;
    margin-right: 0.3rem;
}
.signal-buy     { background: rgba(0,230,118,0.12); color: #00e676; border: 1px solid rgba(0,230,118,0.3); }
.signal-sell    { background: rgba(255,82,82,0.12);  color: #ff5252; border: 1px solid rgba(255,82,82,0.3); }
.signal-neutral { background: rgba(247,183,49,0.12); color: #f7b731; border: 1px solid rgba(247,183,49,0.3); }

/* ───── Analysis Panel ───── */
.analysis-box {
    background: linear-gradient(135deg, #0d1b2a, #0a1628);
    border: 1px solid rgba(247,183,49,0.25);
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 1rem;
}
.analysis-header { color: #f7b731; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.8rem; }
.analysis-body   { color: #b8cfe0; line-height: 1.8; font-size: 0.87rem; }

/* ───── Welcome Screen ───── */
.welcome-box {
    text-align: center; padding: 4rem 2rem; color: #4a6080;
}
.welcome-icon  { font-size: 4rem; margin-bottom: 1rem; }
.welcome-title { color: #7fa3c0; font-size: 1.3rem; font-weight: 600; margin-bottom: 0.5rem; }
.welcome-text  { color: #4a6080; font-size: 0.88rem; max-width: 380px; margin: 0 auto 1.5rem; line-height: 1.6; }
.welcome-tip {
    font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #00c9a7;
    background: rgba(0,201,167,0.08); border: 1px solid rgba(0,201,167,0.2);
    border-radius: 8px; padding: 0.6rem 1.2rem; display: inline-block;
}

/* ───── Sidebar ───── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080d14, #080e18) !important;
    border-right: 1px solid rgba(0,201,167,0.12) !important;
}

/* ───── Buttons ───── */
.stButton > button {
    background: linear-gradient(135deg, #00c9a7, #009e87) !important;
    color: #080d14 !important; font-weight: 600 !important;
    border: none !important; border-radius: 8px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    filter: brightness(1.1) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(0,201,167,0.25) !important;
}

/* ───── Tabs ───── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid rgba(0,201,167,0.15);
    gap: 0.5rem;
}
.stTabs [data-baseweb="tab"] {
    color: #5a8fa8 !important; font-weight: 500;
    background: transparent !important;
    border-radius: 8px 8px 0 0;
    padding: 0.5rem 1.2rem;
}
.stTabs [aria-selected="true"] {
    color: #00c9a7 !important;
    background: rgba(0,201,167,0.08) !important;
    border-bottom: 2px solid #00c9a7 !important;
}

/* ───── Metric Cards ───── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0d1b2a, #0a1628) !important;
    border: 1px solid rgba(0,201,167,0.12) !important;
    border-radius: 10px !important;
    padding: 0.8rem !important;
}
[data-testid="metric-container"] label {
    color: #5a8fa8 !important;
    font-size: 0.70rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    color: #e8f0f7 !important;
    font-size: 1.05rem !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
}

/* ───── Chat Messages ───── */
[data-testid="stChatMessage"] {
    background: linear-gradient(135deg, #0d1b2a, #0a1628) !important;
    border: 1px solid rgba(0,201,167,0.1) !important;
    border-radius: 12px !important;
    padding: 0.8rem !important;
    margin-bottom: 0.5rem !important;
}

/* ───── Chat Input ───── */
[data-testid="stChatInput"] textarea {
    background: #0d1b2a !important;
    border: 1px solid rgba(0,201,167,0.3) !important;
    color: #e8f0f7 !important;
    font-family: 'Inter', sans-serif !important;
    border-radius: 10px !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #00c9a7 !important;
    box-shadow: 0 0 0 2px rgba(0,201,167,0.15) !important;
}

/* ───── Selectbox / Input ───── */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    background: #0d1b2a !important;
    border: 1px solid rgba(0,201,167,0.25) !important;
    color: #e8f0f7 !important;
    border-radius: 8px !important;
}

/* ───── Divider ───── */
hr { border-color: rgba(0,201,167,0.1) !important; }

/* ───── Info / Warning / Error ───── */
[data-testid="stAlert"] {
    background: #0d1b2a !important;
    border-radius: 10px !important;
    border-left-width: 3px !important;
}

/* ───── Spinner ───── */
.stSpinner > div { border-top-color: #00c9a7 !important; }

/* ───── Footer ───── */
.fx-footer {
    text-align: center; padding: 1.2rem;
    margin-top: 2rem; color: #2d4a5a;
    font-size: 0.73rem;
    border-top: 1px solid rgba(0,201,167,0.08);
    font-family: 'JetBrains Mono', monospace;
}

/* ───── Scrollbar ───── */
::-webkit-scrollbar       { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #080d14; }
::-webkit-scrollbar-thumb { background: #1a3a4a; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #00c9a7; }

/* ───── Quick Questions Buttons ───── */
.stButton[data-testid*="sq_"] > button {
    background: linear-gradient(135deg, #0d1b2a, #0a1628) !important;
    color: #7fa3c0 !important;
    font-weight: 400 !important;
    font-size: 0.80rem !important;
    border: 1px solid rgba(0,201,167,0.15) !important;
    text-align: left !important;
}
.stButton[data-testid*="sq_"] > button:hover {
    border-color: rgba(0,201,167,0.4) !important;
    color: #00c9a7 !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ───── Table Styling ───── */
table { color: #b8cfe0 !important; }
thead tr th {
    background: #0d1b2a !important;
    color: #00c9a7 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
tbody tr:nth-child(even) { background: rgba(13,27,42,0.5) !important; }
tbody tr:hover { background: rgba(0,201,167,0.05) !important; }
</style>
"""


# ============================================================
# TECHNICAL INDICATORS
# ============================================================

def calc_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index (RSI)"""
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(window=period).mean()
    loss  = (-delta.clip(upper=0)).rolling(window=period).mean()
    rs    = gain / loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


def calc_macd(
    series: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> tuple:
    """Moving Average Convergence Divergence (MACD)"""
    ema_fast   = series.ewm(span=fast,   adjust=False).mean()
    ema_slow   = series.ewm(span=slow,   adjust=False).mean()
    macd_line  = ema_fast - ema_slow
    signal_line= macd_line.ewm(span=signal, adjust=False).mean()
    histogram  = macd_line - signal_line
    return macd_line, signal_line, histogram


def calc_bb(
    series: pd.Series,
    period: int = 20,
    std_dev: float = 2.0,
) -> tuple:
    """Bollinger Bands (Upper, Middle, Lower)"""
    mid   = series.rolling(window=period).mean()
    sigma = series.rolling(window=period).std()
    return mid + std_dev * sigma, mid, mid - std_dev * sigma


def get_signals(df: pd.DataFrame) -> Dict[str, tuple]:
    """
    Calculate Buy / Sell / Neutral signals for all indicators.
    Returns dict: { "RSI": ("OVERBOUGHT", "sell"), ... }
    """
    signals = {}
    close   = df["Close"]

    # ── RSI Signal ──────────────────────────────────────────
    rsi     = calc_rsi(close)
    rsi_val = rsi.iloc[-1] if not rsi.empty else None
    if rsi_val is not None and not pd.isna(rsi_val):
        if   rsi_val > 70: signals["RSI"] = ("OVERBOUGHT",  "sell")
        elif rsi_val < 30: signals["RSI"] = ("OVERSOLD",    "buy")
        elif rsi_val > 55: signals["RSI"] = ("BULLISH",     "buy")
        elif rsi_val < 45: signals["RSI"] = ("BEARISH",     "sell")
        else:              signals["RSI"] = ("NEUTRAL",      "neutral")

    # ── MACD Signal ─────────────────────────────────────────
    ml, sl, _ = calc_macd(close)
    if not ml.empty:
        m, s = ml.iloc[-1], sl.iloc[-1]
        if   m > s and m > 0: signals["MACD"] = ("BULLISH",     "buy")
        elif m > s:            signals["MACD"] = ("CROSS UP ↑",  "buy")
        elif m < s and m < 0:  signals["MACD"] = ("BEARISH",     "sell")
        elif m < s:            signals["MACD"] = ("CROSS DOWN ↓","sell")
        else:                  signals["MACD"] = ("NEUTRAL",      "neutral")

    # ── MA20 Signal ─────────────────────────────────────────
    price = float(close.iloc[-1])
    ma20  = close.rolling(20).mean().iloc[-1]
    if not pd.isna(ma20):
        if price > float(ma20): signals["MA20"] = ("ABOVE MA", "buy")
        else:                   signals["MA20"] = ("BELOW MA", "sell")

    # ── MA50 Signal ─────────────────────────────────────────
    if len(close) >= 50:
        ma50 = close.rolling(50).mean().iloc[-1]
        if not pd.isna(ma50):
            if price > float(ma50): signals["MA50"] = ("ABOVE MA", "buy")
            else:                   signals["MA50"] = ("BELOW MA", "sell")

    # ── Bollinger Band Signal ────────────────────────────────
    upper, _, lower = calc_bb(close)
    if not upper.empty:
        u, l = float(upper.iloc[-1]), float(lower.iloc[-1])
        if   price > u: signals["BB"] = ("OVERBOUGHT", "sell")
        elif price < l: signals["BB"] = ("OVERSOLD",   "buy")
        else:           signals["BB"] = ("IN RANGE",   "neutral")

    return signals


# ============================================================
# DATA FETCHING
# ============================================================

@st.cache_data(ttl=3600)   # ECB rates update once a day
def get_live_rates() -> Optional[Dict]:
    """Fetch live USD base exchange rates via Frankfurter (ECB) API."""
    try:
        r = requests.get(
            "https://api.frankfurter.app/latest?from=USD",
            timeout=8,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=300)   # Cache chart data 5 min
def fetch_ohlcv(ticker: str, period: str, interval: str) -> Optional[pd.DataFrame]:
    """Download OHLCV data from Yahoo Finance via yfinance."""
    try:
        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=True,
        )
        if df.empty:
            return None
        # Handle MultiIndex columns (newer yfinance versions)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        # Normalize column names to Title Case
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        df = df.dropna()
        return df
    except Exception:
        return None


def build_summary(df: pd.DataFrame) -> Dict:
    """Compute key market statistics from OHLCV dataframe."""
    if df is None or df.empty:
        return {}
    c      = df["Close"]
    latest = float(c.iloc[-1])
    prev   = float(c.iloc[-2]) if len(c) > 1 else latest
    first  = float(c.iloc[0])

    rsi       = calc_rsi(c)
    ml, sl, _ = calc_macd(c)

    ma20_raw = c.rolling(20).mean().iloc[-1]
    ma50_raw = c.rolling(50).mean().iloc[-1] if len(c) >= 50 else None
    ma200_raw= c.rolling(200).mean().iloc[-1] if len(c) >= 200 else None

    return {
        "latest":          latest,
        "change":          latest - prev,
        "change_pct":      ((latest - prev) / prev) * 100,
        "period_chg_pct":  ((latest - first) / first) * 100,
        "high":            float(df["High"].max()),
        "low":             float(df["Low"].min()),
        "open":            float(df["Open"].iloc[0]),
        "rsi":             float(rsi.iloc[-1]) if not rsi.empty else None,
        "macd":            float(ml.iloc[-1])  if not ml.empty  else None,
        "signal_line":     float(sl.iloc[-1])  if not sl.empty  else None,
        "ma20":            float(ma20_raw)      if ma20_raw  is not None and not pd.isna(ma20_raw)  else None,
        "ma50":            float(ma50_raw)      if ma50_raw  is not None and not pd.isna(ma50_raw)  else None,
        "ma200":           float(ma200_raw)     if ma200_raw is not None and not pd.isna(ma200_raw) else None,
    }


# ============================================================
# INTERACTIVE CHART BUILDER
# ============================================================

def build_chart(
    df: pd.DataFrame,
    pair: str,
    indicators: List[str],
) -> go.Figure:
    """Build an interactive Plotly candlestick chart with optional overlays."""
    # Determine row count based on selected sub-indicators
    rows, heights = 1, [0.65]
    if "RSI"  in indicators: rows += 1; heights.append(0.18)
    if "MACD" in indicators: rows += 1; heights.append(0.17)

    subtitles = [pair]
    if "RSI"  in indicators: subtitles.append("RSI (14)")
    if "MACD" in indicators: subtitles.append("MACD (12, 26, 9)")

    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=heights,
        subplot_titles=subtitles,
    )

    # ── Candlestick ───────────────────────────────────────────
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"],   close=df["Close"],
        name=pair,
        increasing=dict(line=dict(color="#00e676", width=1), fillcolor="#00e676"),
        decreasing=dict(line=dict(color="#ff5252", width=1), fillcolor="#ff5252"),
        whiskerwidth=0.5,
    ), row=1, col=1)

    # ── Volume (overlay, secondary y) ────────────────────────
    if "Volume" in df.columns and df["Volume"].sum() > 0:
        vol_colors = [
            "#00e676" if float(c) >= float(o) else "#ff5252"
            for c, o in zip(df["Close"], df["Open"])
        ]
        fig.add_trace(go.Bar(
            x=df.index, y=df["Volume"],
            name="Volume",
            marker_color=vol_colors,
            opacity=0.25,
            yaxis="y2",
        ), row=1, col=1)

    # ── Moving Average 20 ─────────────────────────────────────
    if "MA20" in indicators:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Close"].rolling(20).mean(),
            name="MA 20",
            line=dict(color="#00c9a7", width=1.5),
        ), row=1, col=1)

    # ── Moving Average 50 ─────────────────────────────────────
    if "MA50" in indicators:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Close"].rolling(50).mean(),
            name="MA 50",
            line=dict(color="#f7b731", width=1.5),
        ), row=1, col=1)

    # ── Moving Average 200 ────────────────────────────────────
    if "MA200" in indicators:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Close"].rolling(200).mean(),
            name="MA 200",
            line=dict(color="#a55eea", width=1.5),
        ), row=1, col=1)

    # ── Bollinger Bands ───────────────────────────────────────
    if "Bollinger Bands" in indicators:
        upper, mid, lower = calc_bb(df["Close"])
        fig.add_trace(go.Scatter(
            x=df.index, y=upper,
            name="BB Upper",
            line=dict(color="rgba(165,94,234,0.6)", width=1, dash="dot"),
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=lower,
            name="BB Lower",
            line=dict(color="rgba(165,94,234,0.6)", width=1, dash="dot"),
            fill="tonexty",
            fillcolor="rgba(165,94,234,0.04)",
        ), row=1, col=1)

    # ── RSI Panel ─────────────────────────────────────────────
    cur_row = 2
    if "RSI" in indicators:
        rsi = calc_rsi(df["Close"])
        fig.add_trace(go.Scatter(
            x=df.index, y=rsi,
            name="RSI (14)",
            line=dict(color="#45aaf2", width=1.5),
        ), row=cur_row, col=1)

        # Overbought / Oversold zones
        fig.add_hrect(y0=70, y1=100, fillcolor="rgba(255,82,82,0.06)",  line_width=0, row=cur_row, col=1)
        fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(0,230,118,0.06)", line_width=0, row=cur_row, col=1)
        fig.add_hline(y=70, line=dict(color="rgba(255,82,82,0.4)",  dash="dash", width=1), row=cur_row, col=1)
        fig.add_hline(y=50, line=dict(color="rgba(127,163,192,0.2)", dash="dot",  width=1), row=cur_row, col=1)
        fig.add_hline(y=30, line=dict(color="rgba(0,230,118,0.4)",  dash="dash", width=1), row=cur_row, col=1)
        fig.update_yaxes(range=[0, 100], row=cur_row, col=1)
        cur_row += 1

    # ── MACD Panel ────────────────────────────────────────────
    if "MACD" in indicators:
        ml, sl, hist = calc_macd(df["Close"])
        hist_colors  = ["#00e676" if float(v) >= 0 else "#ff5252" for v in hist]

        fig.add_trace(go.Bar(
            x=df.index, y=hist,
            name="Histogram",
            marker_color=hist_colors,
            opacity=0.75,
        ), row=cur_row, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=ml,
            name="MACD",
            line=dict(color="#00c9a7", width=1.5),
        ), row=cur_row, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=sl,
            name="Signal",
            line=dict(color="#f7b731", width=1.5, dash="dash"),
        ), row=cur_row, col=1)
        fig.add_hline(y=0, line=dict(color="rgba(127,163,192,0.2)", width=1), row=cur_row, col=1)

    # ── Layout ────────────────────────────────────────────────
    chart_h = 500 + max(0, rows - 1) * 140

    fig.update_layout(
        plot_bgcolor  = "#080d14",
        paper_bgcolor = "#080d14",
        font          = dict(color="#5a8fa8", family="JetBrains Mono, monospace", size=10),
        height        = chart_h,
        margin        = dict(l=70, r=20, t=55, b=30),
        xaxis_rangeslider_visible=False,
        legend=dict(
            bgcolor      = "rgba(13,27,42,0.85)",
            bordercolor  = "rgba(0,201,167,0.2)",
            borderwidth  = 1,
            font         = dict(size=10),
            orientation  = "h",
            yanchor      = "bottom",
            y            = 1.01,
            xanchor      = "right",
            x            = 1,
        ),
        hovermode   = "x unified",
        hoverlabel  = dict(
            bgcolor    = "#0d1b2a",
            bordercolor= "#00c9a7",
            font       = dict(color="#e8f0f7", family="JetBrains Mono", size=11),
        ),
    )

    # Grid styling for all axes
    axis_style = dict(
        gridcolor="#0d1b2a",
        showgrid=True,
        zeroline=False,
        tickfont=dict(color="#3a5a6a", size=9),
        linecolor="rgba(0,201,167,0.1)",
    )
    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)

    # Subplot title color
    for ann in fig.layout.annotations:
        ann.font = dict(color="#5a8fa8", size=11)

    return fig


# ============================================================
# GOOGLE GEMINI AI — SYSTEM PROMPT BUILDER
# ============================================================

def build_system_prompt(style: str, risk: str, focus: str) -> str:
    """Build the Gemini system prompt (system_instruction) based on user-selected settings."""

    style_desc = {
        "Professional 📊": (
            "formal and institutional. Use precise financial terminology, "
            "structured headers, and concise data-driven statements."
        ),
        "Educational 🎓": (
            "educational and explanatory. Break down every concept clearly, "
            "use analogies, and ensure a beginner can follow the analysis."
        ),
        "Trader 🎯": (
            "direct and action-oriented. Skip preamble, jump to signals, "
            "key levels, and catalysts. Bullet points preferred."
        ),
    }.get(style, "professional and informative")

    risk_desc = {
        "Conservative 🛡️": (
            "Emphasize capital preservation. Only highlight high-probability setups "
            "(>65% historical win rate scenarios). Always mention wide stop-losses "
            "and low position sizing (0.5–1% risk per trade)."
        ),
        "Moderate ⚖️": (
            "Balance risk and reward. Minimum 1:2 risk/reward ratio. Consider "
            "both trend-following and counter-trend setups."
        ),
        "Aggressive 🚀": (
            "Accept higher risk for greater reward (1:3+ R:R). Highlight "
            "momentum plays, breakouts, and high-volatility setups."
        ),
    }.get(risk, "balanced risk/reward approach")

    return f"""You are **ForexBot AI**, an elite AI-powered forex market analyst and educator.

## Core Expertise

### Technical Analysis
- Candlestick patterns: Doji, Engulfing, Hammer, Pin Bar, Evening/Morning Star, Harami
- Support & Resistance levels, trend lines, price channels, trendline breaks
- Indicators: RSI (14), MACD (12,26,9), Bollinger Bands (20,±2σ), ATR, Stochastic
- Moving Averages: MA20 (short-term), MA50 (medium-term), MA200 (long-term)
- Fibonacci retracements & extensions (23.6%, 38.2%, 50%, 61.8%, 78.6%)
- Chart patterns: Head & Shoulders, Double/Triple Top & Bottom, Triangles (ascending/descending/symmetrical), Flags, Pennants, Wedges

### Fundamental Analysis
- Central bank policies: Federal Reserve (Fed), ECB, Bank of Japan (BOJ), Bank of England (BOE), RBA, SNB, RBNZ
- Key releases: NFP (Non-Farm Payrolls), CPI/PPI, GDP, PMI (Markit/ISM), Retail Sales, Trade Balance, Consumer Confidence
- Interest rate differentials and carry trade mechanics
- Geopolitical risk events and their typical market impact
- Commodity-currency correlations: Oil ↔ CAD/NOK/RUB, Gold ↔ AUD/CHF/USD

### Risk Management
- Position sizing using ATR or fixed-percentage methods
- Stop-loss placement (ATR-based, structure-based, time-based)
- Take-profit strategies: partial exits, trailing stops, scaled targets
- Correlation risk: EUR/USD vs GBP/USD (positive), USD/JPY vs USD/CHF (positive)
- Trading session overview: Sydney → Tokyo → London → New York

## Communication Style
{style_desc}

## User Risk Profile
{risk_desc}

## Analysis Focus
Primary focus: **{focus}**

## Response Structure (when applicable)
Use these sections where relevant:
📊 **Technical Outlook** — Price action, patterns, indicator readings  
🌍 **Fundamental Context** — Macro drivers, economic calendar, central banks  
🎯 **Key Levels** — Support zones, resistance zones, entry/exit areas  
📐 **Fibonacci/Structure** — Key retracement levels if applicable  
⚠️ **Risk Warning** — Always include a brief risk note  
💡 **Educational Note** — Explain concepts when helpful  

## Important Rules
- ALWAYS include a brief disclaimer that analysis is educational/informational only, not financial advice
- Never guarantee specific price outcomes or profits
- Always recommend proper risk management practices
- Remind users that forex trading carries substantial risk of loss
- Use markdown formatting (bold, bullets, headers) for clarity

Today's date: {datetime.now().strftime("%A, %B %d, %Y at %H:%M UTC")}"""


def build_context_str(pair: str, summary: Dict, timeframe: str) -> str:
    """Build a live market context string to prepend to the AI prompt."""
    if not summary:
        return f"\n\n[Context: Analyzing {pair} | Timeframe: {timeframe}]"

    rsi_str  = f"{summary['rsi']:.1f}"    if summary.get("rsi")  else "N/A"
    ma20_str = f"{summary['ma20']:.5f}"   if summary.get("ma20") else "N/A"
    ma50_str = f"{summary['ma50']:.5f}"   if summary.get("ma50") else "N/A"

    return (
        f"\n\n[📊 LIVE MARKET DATA — {pair} | Timeframe: {timeframe}]\n"
        f"Current Price : {summary['latest']:.5f}\n"
        f"1-Bar Change  : {summary['change_pct']:+.3f}%\n"
        f"Period Change : {summary['period_chg_pct']:+.2f}%\n"
        f"Period High   : {summary['high']:.5f}\n"
        f"Period Low    : {summary['low']:.5f}\n"
        f"Period Open   : {summary['open']:.5f}\n"
        f"MA (20)       : {ma20_str}\n"
        f"MA (50)       : {ma50_str}\n"
        f"RSI (14)      : {rsi_str}\n"
    )


# ============================================================
# GOOGLE GEMINI AI INTEGRATION (google-genai SDK)
# ============================================================

def _to_gemini_history(messages: List[Dict]) -> List["genai_types.Content"]:
    """
    Convert Streamlit session messages (all but last) to Gemini chat history.
    Format Streamlit (assistant/user)  →  Gemini Content objects:
      role: "assistant"  →  role: "model"
      content: "text"    →  parts: [Part(text="text")]
    """
    history = []
    for msg in messages[:-1]:
        role = "model" if msg["role"] == "assistant" else "user"
        history.append(
            genai_types.Content(
                role=role,
                parts=[genai_types.Part(text=msg["content"])],
            )
        )
    return history


def _build_chat(
    messages: List[Dict],
    system: str,
    api_key: str,
    model_name: str,
    max_tokens: int,
):
    """Create a Gemini chat session pre-loaded with conversation history."""
    client  = genai.Client(api_key=api_key)
    history = _to_gemini_history(messages)
    config  = genai_types.GenerateContentConfig(
        system_instruction=system,
        max_output_tokens=max_tokens,
        temperature=0.7,
    )
    chat = client.chats.create(
        model=model_name,
        config=config,
        history=history,
    )
    return chat


def stream_gemini(
    messages: List[Dict],
    system: str,
    api_key: str,
    model_name: str = "gemini-2.0-flash",
) -> Generator[str, None, None]:
    """Stream Gemini response chunks as a generator for st.write_stream()."""
    chat         = _build_chat(messages, system, api_key, model_name, max_tokens=2048)
    last_message = messages[-1]["content"]

    for chunk in chat.send_message_stream(last_message):
        if chunk.text:
            yield chunk.text


def call_gemini(
    messages: List[Dict],
    system: str,
    api_key: str,
    model_name: str = "gemini-2.0-flash",
    max_tokens: int = 1500,
) -> Optional[str]:
    """Non-streaming Gemini call. Returns full response text."""
    try:
        chat         = _build_chat(messages, system, api_key, model_name, max_tokens)
        last_message = messages[-1]["content"]
        response     = chat.send_message(last_message)
        return response.text

    except Exception as e:
        err = str(e).lower()
        if "api key" in err or "api_key" in err or "invalid" in err or "permission" in err or "401" in err or "403" in err:
            st.error(
                "❌ **API Key tidak valid.** "
                "Dapatkan key gratis di [aistudio.google.com](https://aistudio.google.com/app/apikey)"
            )
        elif "quota" in err or "429" in err or "exhausted" in err or "resource_exhausted" in err:
            st.error(
                "⚠️ **Quota API habis.** Tunggu sebentar atau coba model lain. "
                "Cek limit di [ai.google.dev/pricing](https://ai.google.dev/pricing)"
            )
        elif "safety" in err or "blocked" in err or "harm" in err:
            st.warning("⚠️ Respons diblokir oleh filter keamanan Gemini. Coba ubah pertanyaan.")
        elif "not found" in err or "404" in err:
            st.error(f"❌ **Model `{model_name}` tidak ditemukan.** Coba pilih model lain di sidebar.")
        else:
            st.error(f"❌ **Error:** {e}")
        return None


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():
    # ── Inject CSS ────────────────────────────────────────────
    st.markdown(DARK_CSS, unsafe_allow_html=True)

    # ── Session State Initialisation ─────────────────────────
    if "messages"    not in st.session_state: st.session_state.messages    = []
    if "last_pair"   not in st.session_state: st.session_state.last_pair   = ""
    if "ai_analysis" not in st.session_state: st.session_state.ai_analysis = ""

    # ══════════════════════════════════════════════════════════
    # SIDEBAR
    # ══════════════════════════════════════════════════════════
    with st.sidebar:
        # Brand
        st.markdown("""
        <div class="sidebar-brand">
            <div class="sidebar-brand-icon">💹</div>
            <p class="sidebar-brand-name">ForexBot AI</p>
            <p class="sidebar-brand-tagline">gemini-2.0-flash · v1.0</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**🔑 Google Gemini API Key**")
        default_key = ""
        try:
            default_key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            pass

        api_key = st.text_input(
            "Gemini API Key",
            value=default_key,
            type="password",
            placeholder="AIzaSy...",
            help="Dapatkan API key GRATIS di: aistudio.google.com/app/apikey",
            label_visibility="collapsed",
        )

        if not api_key:
            st.warning("Masukkan API key untuk fitur AI", icon="🔑")
            st.caption("🆓 Gratis di [aistudio.google.com](https://aistudio.google.com/app/apikey)")
        else:
            st.success("API key terkonfigurasi ✅", icon="")

        st.divider()

        # ── Gemini Model Selection ────────────────────────────
        st.markdown("**🤖 Gemini Model**")
        model_name = st.selectbox(
            "Model",
            [
                "gemini-2.0-flash",
                "gemini-1.5-flash",
                "gemini-1.5-flash-8b",
                "gemini-1.5-pro",
            ],
            index=0,
            help="Semua model FREE tier tersedia di Google AI Studio",
        )
        st.caption("✅ **gemini-2.0-flash** → Terbaru & Gratis\n✅ **gemini-1.5-flash** → Stabil & Gratis")

        st.divider()

        # ── Bot Configuration ─────────────────────────────────
        st.markdown("**⚙️ Bot Configuration**")

        style = st.selectbox(
            "Communication Style",
            ["Professional 📊", "Educational 🎓", "Trader 🎯"],
            index=0,
        )
        risk = st.selectbox(
            "Risk Profile",
            ["Conservative 🛡️", "Moderate ⚖️", "Aggressive 🚀"],
            index=1,
        )
        focus = st.selectbox(
            "Analysis Focus",
            ["Technical Analysis", "Fundamental Analysis", "Mixed Analysis"],
            index=2,
        )

        st.divider()

        # ── Chart Configuration ───────────────────────────────
        st.markdown("**📈 Chart Settings**")

        cat = st.selectbox(
            "Instrument Category",
            list(CATEGORY_MAP.keys()),
            index=0,
        )
        pair_dict = CATEGORY_MAP[cat]

        pair = st.selectbox(
            "Instrument",
            list(pair_dict.keys()),
            index=0,
        )

        tf = st.selectbox(
            "Timeframe",
            list(TIMEFRAMES.keys()),
            index=2,  # Default: 1 Month
        )

        inds = st.multiselect(
            "Overlay Indicators",
            ["MA20", "MA50", "MA200", "Bollinger Bands", "RSI", "MACD"],
            default=["MA20", "MA50", "RSI", "MACD"],
        )

        st.divider()

        # ── Live Exchange Rates ───────────────────────────────
        st.markdown("**💱 Live Rates (USD Base)**")
        rates = get_live_rates()

        if rates and "rates" in rates:
            updated = rates.get("date", "N/A")
            st.caption(f"📅 ECB Reference Rate · {updated}")
            for curr in RATE_CURRENCIES:
                v = rates["rates"].get(curr)
                if v is not None:
                    # Format: low values → 5 decimals, JPY etc → 3 decimals
                    price_str = f"{v:.5f}" if v < 100 else f"{v:.3f}"
                    st.markdown(
                        f"""<div class="rate-card">
                            <p class="rate-pair-label">USD / {curr}</p>
                            <p class="rate-price">{price_str}</p>
                        </div>""",
                        unsafe_allow_html=True,
                    )
        else:
            st.info("🔌 Live rates unavailable — check network", icon="ℹ️")

        st.divider()

        # ── Action Buttons ────────────────────────────────────
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🗑️ Clear Chat", use_container_width=True, help="Clear conversation history"):
                st.session_state.messages    = []
                st.session_state.ai_analysis = ""
                st.rerun()
        with col_b:
            if st.button("🔄 Refresh Data", use_container_width=True, help="Reload market data"):
                st.cache_data.clear()
                st.rerun()

    # ══════════════════════════════════════════════════════════
    # HEADER
    # ══════════════════════════════════════════════════════════
    st.markdown(
        f"""
        <div class="fx-header">
            <div class="fx-logo">💹</div>
            <div>
                <h1 class="fx-title">ForexBot AI — Intelligent Forex Analyzer</h1>
                <p class="fx-subtitle">
                    Real-time Analysis &nbsp;·&nbsp; AI-Powered Insights &nbsp;·&nbsp;
                    Technical &amp; Fundamental Research
                    &nbsp;&nbsp;&nbsp;
                    <span class="fx-live">● LIVE</span>
                    &nbsp;&nbsp;
                    {datetime.now().strftime("%d %b %Y · %H:%M UTC")}
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ══════════════════════════════════════════════════════════
    # LOAD MARKET DATA
    # ══════════════════════════════════════════════════════════
    tf_cfg = TIMEFRAMES[tf]
    ticker = pair_dict[pair]

    with st.spinner(f"📡 Fetching {pair} — {tf}..."):
        df = fetch_ohlcv(ticker, tf_cfg["period"], tf_cfg["interval"])

    summary = build_summary(df)
    signals = get_signals(df) if df is not None else {}

    # ══════════════════════════════════════════════════════════
    # METRICS BAR
    # ══════════════════════════════════════════════════════════
    if summary:
        m1, m2, m3, m4, m5, m6, m7 = st.columns(7)

        delta_pct  = f"{summary['change_pct']:+.2f}%"
        delta_color= "normal"

        m1.metric(f"💹 {pair}",   f"{summary['latest']:.5f}",  delta_pct)
        m2.metric("📈 High",       f"{summary['high']:.5f}")
        m3.metric("📉 Low",        f"{summary['low']:.5f}")
        m4.metric("🔓 Open",       f"{summary['open']:.5f}")
        m5.metric(
            "〰️ MA 20",
            f"{summary['ma20']:.5f}"  if summary.get("ma20")  else "—",
        )
        m6.metric(
            "📊 RSI (14)",
            f"{summary['rsi']:.1f}"   if summary.get("rsi")   else "—",
        )
        m7.metric(
            "📅 Period Δ",
            f"{summary['period_chg_pct']:+.2f}%",
        )

    st.markdown("---")

    # ══════════════════════════════════════════════════════════
    # MAIN TABS
    # ══════════════════════════════════════════════════════════
    tab_chart, tab_chat, tab_about = st.tabs([
        "📊 Chart Analysis",
        "🤖 AI Chat Assistant",
        "ℹ️ About & Guide",
    ])

    # ──────────────────────────────────────────────────────────
    # TAB 1 — CHART ANALYSIS
    # ──────────────────────────────────────────────────────────
    with tab_chart:
        if df is not None and not df.empty:

            # Signal badges
            if signals:
                badge_html = "&nbsp;&nbsp;".join([
                    f'<span class="signal signal-{cls}">{name}: {label}</span>'
                    for name, (label, cls) in signals.items()
                ])
                st.markdown(
                    f"**🎯 Technical Signals** &nbsp;&nbsp; {badge_html}",
                    unsafe_allow_html=True,
                )
                st.markdown("")

            # Interactive chart
            fig = build_chart(df, pair, inds)
            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "displayModeBar"         : True,
                    "displaylogo"            : False,
                    "modeBarButtonsToRemove" : ["lasso2d", "select2d"],
                    "toImageButtonOptions"   : {
                        "format"  : "png",
                        "filename": f"ForexBot_{pair.replace('/', '_')}_{tf}",
                        "height"  : 900,
                        "width"   : 1800,
                        "scale"   : 2,
                    },
                },
            )

            # ── Quick AI Analysis ─────────────────────────────
            st.markdown("---")

            if api_key:
                left_col, right_col = st.columns([4, 1])
                with left_col:
                    st.markdown(f"**🤖 Quick AI Analysis** — {pair} · {tf} timeframe")
                    st.caption(
                        "Tap the button to get a comprehensive AI-generated market analysis "
                        "based on live indicator readings and price action."
                    )
                with right_col:
                    analyze_clicked = st.button(
                        "⚡ Analyze Now",
                        use_container_width=True,
                        key="quick_analyze_btn",
                    )

                if analyze_clicked:
                    ctx       = build_context_str(pair, summary, tf)
                    prompt    = (
                        f"Provide a comprehensive technical market analysis for **{pair}** "
                        f"on the **{tf}** timeframe. Cover: "
                        f"(1) Current price action and trend direction, "
                        f"(2) Key indicator readings (RSI, MACD, Moving Averages), "
                        f"(3) Important support and resistance levels, "
                        f"(4) Pattern observations and what to watch for next, "
                        f"(5) Key fundamental factors affecting this pair right now."
                        f"{ctx}"
                    )

                    sys_p = build_system_prompt(style, risk, focus)

                    with st.spinner("🧠 Gemini AI sedang menganalisis pasar..."):
                        ai_text = call_gemini(
                            [{"role": "user", "content": prompt}],
                            sys_p,
                            api_key,
                            model_name=model_name,
                            max_tokens=1600,
                        )

                    if ai_text:
                        st.session_state.ai_analysis = ai_text
                        # Also save to chat history
                        st.session_state.messages.append({
                            "role"   : "user",
                            "content": f"Quick Chart Analysis: {pair} ({tf})",
                        })
                        st.session_state.messages.append({
                            "role"   : "assistant",
                            "content": ai_text,
                        })

                # Display cached analysis
                if st.session_state.ai_analysis:
                    safe_text = st.session_state.ai_analysis.replace(
                        "\n", "<br>"
                    )
                    st.markdown(
                        f"""<div class="analysis-box">
                            <div class="analysis-header">
                                🤖 AI Market Analysis &nbsp;—&nbsp; {pair} ({tf})
                            </div>
                            <div class="analysis-body">{safe_text}</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )

            else:
                st.info(
                    "💡 Masukkan **Google Gemini API Key** (gratis) di sidebar untuk "
                    "mengaktifkan fitur AI Chart Analysis. "
                    "Dapatkan di [aistudio.google.com](https://aistudio.google.com/app/apikey)",
                    icon="🔑",
                )

        else:
            st.error(f"❌ No data returned for **{pair}** on the **{tf}** timeframe.")
            st.info(
                "💡 **Tip:** Forex markets are closed on weekends. "
                "Try a longer timeframe (3 Months / 1 Year) or a different instrument.",
                icon="ℹ️",
            )

    # ──────────────────────────────────────────────────────────
    # TAB 2 — AI CHAT ASSISTANT
    # ──────────────────────────────────────────────────────────
    with tab_chat:
        chat_main, chat_side = st.columns([3, 1])

        # ── Right Panel: Quick Questions ──────────────────────
        with chat_side:
            st.markdown("**⚡ Quick Questions**")

            quick_qs = [
                f"📊 Analyze {pair} now",
                f"🎯 Key S/R levels for {pair}",
                "📰 How does NFP impact USD?",
                "🏦 Fed vs ECB policy divergence",
                "🔍 Explain RSI divergence",
                "📐 Fibonacci retracement guide",
                "💱 Best forex trading sessions",
                "📈 What is carry trade strategy?",
                "🕯️ Bullish engulfing pattern",
                "⚠️ Forex risk management rules",
                "🔁 Currency correlation table",
                "📉 What is a dead cat bounce?",
            ]

            for q in quick_qs:
                if st.button(q, key=f"sq_{q}", use_container_width=True):
                    if api_key:
                        # Strip emoji prefix for cleaner prompt
                        parts   = q.split(" ", 1)
                        clean_q = parts[1].strip() if len(parts) > 1 else q

                        ctx      = build_context_str(pair, summary, tf)
                        sys_p    = build_system_prompt(style, risk, focus)

                        # Build messages list (include history + context on first messages)
                        history  = st.session_state.messages
                        prompt_q = clean_q + (ctx if len(history) == 0 else "")

                        msgs = [*history, {"role": "user", "content": prompt_q}]

                        st.session_state.messages.append({
                            "role"   : "user",
                            "content": clean_q,
                        })

                        reply = call_gemini(msgs, sys_p, api_key, model_name=model_name, max_tokens=900)
                        if reply:
                            st.session_state.messages.append({
                                "role"   : "assistant",
                                "content": reply,
                            })
                        st.rerun()
                    else:
                        st.error("🔑 Add your API key first!")

            if st.session_state.messages:
                st.markdown("---")
                msg_count = len(st.session_state.messages)
                st.caption(f"💬 {msg_count} message{'s' if msg_count != 1 else ''} in session")

        # ── Left Panel: Chat Interface ────────────────────────
        with chat_main:
            # Welcome screen when no messages
            if not st.session_state.messages:
                st.markdown("""
                <div class="welcome-box">
                    <div class="welcome-icon">🤖</div>
                    <h3 class="welcome-title">ForexBot AI Ready</h3>
                    <p class="welcome-text">
                        Ask me anything about forex markets — technical analysis,
                        fundamental drivers, currency correlations, risk management,
                        trading strategies, or specific currency pairs.
                    </p>
                    <span class="welcome-tip">
                        💡 Try: "What are the key support levels for EUR/USD right now?"
                    </span>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Display conversation history
                for msg in st.session_state.messages:
                    avatar = "👤" if msg["role"] == "user" else "🤖"
                    with st.chat_message(msg["role"], avatar=avatar):
                        st.markdown(msg["content"])

            # ── Chat Input ────────────────────────────────────
            user_input = st.chat_input(
                placeholder=f"Ask about {pair}, technical analysis, market outlook, trading strategies...",
                disabled=not bool(api_key),
            )

            if user_input:
                # Show user message immediately
                st.session_state.messages.append({
                    "role"   : "user",
                    "content": user_input,
                })
                with st.chat_message("user", avatar="👤"):
                    st.markdown(user_input)

                # Build context (inject live data on first few messages)
                ctx       = build_context_str(pair, summary, tf)
                is_early  = len(st.session_state.messages) <= 3
                full_prompt = user_input + (ctx if is_early else "")

                msgs_to_send = [
                    *st.session_state.messages[:-1],
                    {"role": "user", "content": full_prompt},
                ]
                sys_p = build_system_prompt(style, risk, focus)

                # Stream Gemini response
                with st.chat_message("assistant", avatar="🤖"):
                    try:
                        bot_reply = st.write_stream(
                            stream_gemini(msgs_to_send, sys_p, api_key, model_name)
                        )
                        st.session_state.messages.append({
                            "role"   : "assistant",
                            "content": bot_reply,
                        })
                    except Exception as e:
                        err = str(e).lower()
                        if "api_key" in err or "invalid" in err or "400" in err:
                            st.error("❌ API Key tidak valid. Cek sidebar.")
                        elif "quota" in err or "429" in err or "exhausted" in err:
                            st.warning("⚠️ Quota habis. Tunggu sebentar lalu coba lagi.")
                        elif "safety" in err or "blocked" in err:
                            st.warning("⚠️ Respons diblokir filter keamanan. Coba ubah pertanyaan.")
                        else:
                            st.error(f"❌ Error: {str(e)}")
                        st.session_state.messages.pop()  # Hapus pesan user yang gagal

    # ──────────────────────────────────────────────────────────
    # TAB 3 — ABOUT & GUIDE
    # ──────────────────────────────────────────────────────────
    with tab_about:
        col_left, col_right = st.columns([3, 2])

        with col_left:
            st.markdown("""
## 💹 About ForexBot AI

**ForexBot AI** is an AI-powered forex market analyzer and educational assistant
built with **Streamlit** and **Google Gemini AI (gemini-2.0-flash)** — completely **FREE** to use.
It is designed for traders, students, and market enthusiasts who want deeper
understanding of forex markets through AI-assisted analysis.

---

### 🛠️ Technology Stack

| Component         | Technology                         |
|-------------------|------------------------------------|
| UI Framework      | Streamlit                          |
| AI Engine         | Google Gemini (2.0 Flash / 1.5 Flash / 1.5 Pro) |
| Market Data       | yfinance (Yahoo Finance)           |
| Exchange Rates    | Frankfurter API (ECB)              |
| Charting          | Plotly (Interactive)               |
| Language          | Python 3.9+                        |
| Deployment        | Streamlit Community Cloud          |

---

### ✨ Features

- **📊 Interactive Charts** — Candlestick + MA20/50/200, RSI, MACD, Bollinger Bands
- **🤖 AI Chat** — Natural language forex analysis with full conversation memory
- **⚡ Quick Analysis** — One-click AI chart analysis using live indicator data
- **🎯 Signal Panel** — Real-time Buy/Sell/Neutral signal summary per indicator
- **💱 Live Rates** — Real-time ECB reference exchange rates (10 currencies)
- **⚙️ Configurable** — Adjustable communication style, risk profile & focus
- **🆓 100% Free AI** — Powered by Google Gemini's generous free tier

---

### 📌 Supported Instruments

**Major Pairs** — EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, USD/CAD, NZD/USD

**Cross Pairs** — EUR/GBP, EUR/JPY, GBP/JPY, AUD/JPY, EUR/AUD, EUR/CAD

**Commodities** — XAU/USD (Gold), XAG/USD (Silver), WTI Crude Oil

---

### 📊 Technical Indicators Reference

| Indicator        | Parameters     | Interpretation                          |
|------------------|----------------|-----------------------------------------|
| RSI              | Period: 14     | >70 Overbought, <30 Oversold            |
| MACD             | 12, 26, Signal 9 | Crossover = direction change signal   |
| Bollinger Bands  | 20 period, ±2σ | Price near bands = momentum signal      |
| MA 20            | SMA 20 bars    | Short-term trend direction              |
| MA 50            | SMA 50 bars    | Medium-term trend direction             |
| MA 200           | SMA 200 bars   | Long-term bull/bear market indicator    |

---

### 🆓 Gemini Free Tier Limits

| Model | RPM (Free) | RPD (Free) |
|-------|-----------|-----------|
| gemini-2.0-flash | 15 | 1,500 |
| gemini-1.5-flash | 15 | 1,500 |
| gemini-1.5-flash-8b | 15 | 1,500 |
| gemini-1.5-pro | 2 | 50 |

*RPM = Requests Per Minute, RPD = Requests Per Day. Limits may change — check [ai.google.dev/pricing](https://ai.google.dev/pricing)*

---

### ⚠️ Risk Disclosure

> **Important:** ForexBot AI is designed **for educational and informational purposes only**.
> Analysis provided does not constitute investment or financial advice.
> Forex and CFD trading carries **significant risk of loss** and is not suitable for all investors.
> Past performance does not guarantee future results.
> Always conduct independent research and consult a licensed financial professional before trading.
            """)

        with col_right:
            st.markdown("""
### 🚀 Quick Start Guide

**Step 1 — Get FREE API Key**

Visit [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey),
sign in with your Google account
and click **"Create API Key"**.
No credit card required!

**Step 2 — Configure**

Enter the key in the sidebar.
Choose your preferred:
- Gemini Model
- Communication Style
- Risk Profile
- Analysis Focus

**Step 3 — Select Instrument**

Pick a currency pair category,
then choose the specific pair
and timeframe you want to analyze.

**Step 4 — Analyze**

View the chart → click **⚡ Analyze Now**
or switch to the Chat tab and ask anything.

---

### ⚙️ Deployment Guide

**Local Setup:**
```bash
git clone <repo-url>
cd forex-ai-analyzer
pip install -r requirements.txt
streamlit run app.py
```

**Streamlit Cloud:**
1. Push repo to GitHub
2. Go to share.streamlit.io
3. Connect repo → set `app.py`
4. Add `GEMINI_API_KEY` to Secrets

---

### 🔗 Resources

[Google AI Studio](https://aistudio.google.com/app/apikey)

[Gemini API Docs](https://ai.google.dev/docs)

[Gemini Pricing/Limits](https://ai.google.dev/pricing)

[Frankfurter API](https://www.frankfurter.app)

[yfinance Docs](https://github.com/ranaroussi/yfinance)

[Plotly Docs](https://plotly.com/python)

[Streamlit Docs](https://docs.streamlit.io)

---

### 📁 Project Structure

```
forex-ai-analyzer/
├── app.py              ← Main application
├── requirements.txt    ← Dependencies
├── .streamlit/
│   └── config.toml     ← Theme config
├── README.md
└── .gitignore
```
            """)

    # ══════════════════════════════════════════════════════════
    # FOOTER
    # ══════════════════════════════════════════════════════════
    st.markdown(
        """
        <div class="fx-footer">
            💹 <strong>ForexBot AI</strong>
            &nbsp;·&nbsp; Powered by Google Gemini (Free)
            &nbsp;·&nbsp; Built with Streamlit
            &nbsp;·&nbsp; For Educational &amp; Informational Purposes Only
            <br>
            ⚠️ Forex trading involves substantial risk of loss.
            This tool does not provide financial advice.
            &nbsp;·&nbsp; © 2025 ForexBot AI
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    main()
