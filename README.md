# 💹 ForexBot AI — Intelligent Forex Analyzer

> An AI-powered forex market analyzer and educational chatbot built with **Streamlit** + **Google Gemini AI (FREE)**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Powered%20by-Google%20Gemini-4285F4?style=flat&logo=google&logoColor=white)](https://ai.google.dev)
[![Free](https://img.shields.io/badge/API-100%25%20Free-34A853?style=flat)](https://aistudio.google.com/app/apikey)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)

---

## 📋 Overview

**ForexBot AI** is a fully interactive forex market analysis tool that combines:

- **Real-time market data** via yfinance (Yahoo Finance) and Frankfurter (ECB rates)
- **Technical analysis charts** powered by Plotly with RSI, MACD, Bollinger Bands, Moving Averages
- **AI-powered analysis** using **Google Gemini** (gemini-2.0-flash) — **100% FREE**, no credit card required
- **Dark trading terminal UI** built with Streamlit and custom CSS

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **Interactive Charts** | Candlestick + MA20/50/200, Bollinger Bands, RSI, MACD panels |
| 🤖 **AI Chat Assistant** | Full conversational AI with memory, powered by Google Gemini |
| ⚡ **Quick Analysis** | One-click AI analysis of current chart and indicator readings |
| 🎯 **Signal Panel** | Real-time Buy / Sell / Neutral technical signal summary |
| 💱 **Live Exchange Rates** | 10 currency pairs via Frankfurter/ECB API (updated daily) |
| ⚙️ **Configurable** | Communication style, risk profile, analysis focus, indicators, AI model |
| 🌙 **Dark Terminal Theme** | Professional dark UI inspired by Bloomberg Terminal |
| 🆓 **Free AI Engine** | Powered by Google Gemini's generous free tier |

---

## 📌 Supported Instruments

### Major Pairs 💱
`EUR/USD` · `GBP/USD` · `USD/JPY` · `USD/CHF` · `AUD/USD` · `USD/CAD` · `NZD/USD`

### Cross Pairs 🔀
`EUR/GBP` · `EUR/JPY` · `GBP/JPY` · `AUD/JPY` · `EUR/AUD` · `EUR/CAD`

### Commodities 🪙
`XAU/USD (Gold)` · `XAG/USD (Silver)` · `WTI Crude Oil`

---

## 🛠️ Technology Stack

```
├── Frontend       → Streamlit 1.32+
├── AI Engine      → Google Gemini (gemini-2.0-flash / 1.5-flash / 1.5-pro)
├── Market Data    → yfinance (Yahoo Finance OHLCV)
├── Exchange Rates → Frankfurter API (ECB reference rates)
├── Charts         → Plotly (interactive candlestick + indicators)
└── Language       → Python 3.9+
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- A **FREE** [Google Gemini API key](https://aistudio.google.com/app/apikey) — no credit card needed!

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/forex-ai-analyzer.git
cd forex-ai-analyzer
```

### 2. Create a Virtual Environment (recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get Your FREE Gemini API Key

1. Go to **[aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)**
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key (starts with `AIzaSy...`)

> 🆓 **No credit card required.** Gemini's free tier includes generous daily quotas.

### 5. Configure API Key

Copy the example secrets file and add your key:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "AIzaSy-your-real-key-here"
```

> ⚠️ **IMPORTANT:** Never commit `secrets.toml` to GitHub. It is in `.gitignore`.

Alternatively, you can paste the API key directly in the app's sidebar at runtime —
no file editing needed.

### 6. Run the Application

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## ☁️ Deployment on Streamlit Community Cloud

1. **Push your repository to GitHub** (make sure `secrets.toml` is NOT committed)

2. **Go to** [share.streamlit.io](https://share.streamlit.io)

3. **Connect your GitHub account**

4. **Create a new app:**
   - Repository: `yourusername/forex-ai-analyzer`
   - Branch: `main`
   - Main file path: `app.py`

5. **Add secrets:**
   - Click **Advanced settings**
   - Paste under **Secrets**:
     ```toml
     GEMINI_API_KEY = "AIzaSy-your-key-here"
     ```

6. **Deploy** — Your app will be live at `https://yourusername-forex-ai-analyzer-app-xxxx.streamlit.app`

---

## 📁 Project Structure

```
forex-ai-analyzer/
│
├── app.py                         ← Main application (all logic)
├── requirements.txt               ← Python dependencies
├── README.md                      ← This file
├── .gitignore                     ← Git ignore rules
│
└── .streamlit/
    ├── config.toml                ← Streamlit theme (dark terminal)
    └── secrets.toml.example       ← API key example (copy → secrets.toml)
```

---

## ⚙️ Configuration Options

The sidebar provides these settings:

### Gemini Model
| Model | Speed | Free Tier (RPM / RPD) | Best For |
|-------|-------|------------------------|----------|
| gemini-2.0-flash | ⚡⚡⚡ | 15 / 1,500 | Default — fast & smart |
| gemini-1.5-flash | ⚡⚡⚡ | 15 / 1,500 | Stable alternative |
| gemini-1.5-flash-8b | ⚡⚡⚡⚡ | 15 / 1,500 | Lightweight, fastest |
| gemini-1.5-pro | ⚡⚡ | 2 / 50 | Highest quality, limited quota |

*RPM = Requests Per Minute · RPD = Requests Per Day*

### Communication Style
| Option | Description |
|--------|-------------|
| Professional 📊 | Formal, institutional-grade analysis with technical terminology |
| Educational 🎓 | Clear explanations, concept breakdowns for learners |
| Trader 🎯 | Concise, direct — signals and key levels only |

### Risk Profile
| Option | Description |
|--------|-------------|
| Conservative 🛡️ | Capital preservation, high-probability setups, low risk per trade |
| Moderate ⚖️ | Balanced approach, minimum 1:2 risk/reward |
| Aggressive 🚀 | Higher R:R (1:3+), momentum and breakout strategies |

### Analysis Focus
| Option | Description |
|--------|-------------|
| Technical Analysis | Price action, patterns, indicators |
| Fundamental Analysis | Central banks, economic data, macro drivers |
| Mixed Analysis | Combines both technical and fundamental |

---

## 📊 Technical Indicators

| Indicator | Parameters | Signal Logic |
|-----------|-----------|--------------|
| RSI | Period: 14 | >70 = Overbought (Sell), <30 = Oversold (Buy) |
| MACD | Fast: 12, Slow: 26, Signal: 9 | Crossover direction = signal |
| Bollinger Bands | Period: 20, ±2σ | Price outside bands = extreme move |
| MA 20 | Simple Moving Average | Price above/below = short-term bias |
| MA 50 | Simple Moving Average | Price above/below = medium-term bias |
| MA 200 | Simple Moving Average | Bull/Bear market indicator |

---

## 🔌 API Dependencies

### Google Gemini API (FREE)
- **Models:** `gemini-2.0-flash`, `gemini-1.5-flash`, `gemini-1.5-flash-8b`, `gemini-1.5-pro`
- **Features used:** Chat sessions, Streaming responses, System instructions
- **Get key:** https://aistudio.google.com/app/apikey
- **No credit card required** for free tier
- **Pricing/Limits:** https://ai.google.dev/pricing

### Frankfurter Exchange Rate API
- **Free, no key required**
- **Source:** European Central Bank (ECB)
- **Updates:** Once daily (business days)
- **Docs:** https://www.frankfurter.app/docs

### Yahoo Finance via yfinance
- **Free, no key required**
- **Data:** OHLCV candlestick data
- **Supports:** Forex pairs, commodities, equities
- **Repo:** https://github.com/ranaroussi/yfinance

---

## 🆓 Why Google Gemini?

| Advantage | Detail |
|-----------|--------|
| 💰 **Free Tier** | 1,500 requests/day on Gemini 2.0/1.5 Flash — no payment info needed |
| ⚡ **Fast** | gemini-2.0-flash and 1.5-flash-8b respond in under 1-2 seconds |
| 🧠 **Capable** | Strong reasoning for financial analysis & natural language Q&A |
| 🌐 **Easy Setup** | Just sign in with Google account — get key in under 1 minute |
| 📈 **Scalable** | Upgrade to paid tier anytime for higher limits |

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "API Key tidak valid" | Verify key starts with `AIzaSy` and copy without extra spaces |
| "Quota habis" (429 error) | Wait 1 minute (RPM limit) or 24h (RPD limit), or switch model |
| "Respons diblokir filter keamanan" | Gemini's safety filter triggered — rephrase your question |
| No chart data | Forex markets closed on weekends — try longer timeframe |
| Module not found | Run `pip install -r requirements.txt` again |

---

## ⚠️ Disclaimer

> **ForexBot AI is designed for educational and informational purposes only.**
>
> The analysis, signals, and information provided by this application do NOT constitute
> financial advice, investment advice, or a recommendation to buy or sell any financial instrument.
>
> Forex (foreign exchange) and CFD trading carries a high level of risk and may not be
> suitable for all investors. The high degree of leverage can work against you as well as
> for you. Before deciding to trade foreign exchange or other financial instruments, you
> should carefully consider your investment objectives, level of experience, and risk appetite.
>
> Past performance is not indicative of future results. Always conduct your own due diligence
> and consult with a licensed financial advisor before making any trading decisions.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [Google AI Studio](https://aistudio.google.com) for Gemini API
- [Streamlit](https://streamlit.io) for the app framework
- [Plotly](https://plotly.com) for interactive charts
- [yfinance](https://github.com/ranaroussi/yfinance) for market data
- [Frankfurter](https://www.frankfurter.app) for exchange rates

---

*Built with ❤️ and 💹 | ForexBot AI © 2025*
