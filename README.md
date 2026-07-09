# AegisAgent

> **Autonomous Forensic Intelligence Agent — Powered by SoSoValue API**

[![Live Demo](https://img.shields.io/badge/Live-aegisagento.vercel.app-00E5FF?style=for-the-badge)](https://aegisagent-sosovalue.vercel.app)
[![SoSoValue](https://img.shields.io/badge/Data-SoSoValue%20API-FCFF52?style=for-the-badge)](https://sosovalue.com)
[![Sovereign AI](https://img.shields.io/badge/AI-Venice.ai-FF3D00?style=for-the-badge)](https://venice.ai)

## Overview

AegisAgent is an autonomous agentic finance application that combines **SoSoValue's on-chain data infrastructure** with proprietary forensic analysis to deliver institutional-grade crypto intelligence. It continuously monitors market data, news sentiment, ETF flows, macro events, and BTC treasuries via SoSoValue API — then computes 100+ forensic metrics and synthesizes actionable risk narratives through sovereign AI (Venice.ai), all without human intervention.

Built for the **SoSoValue Buildathon** — demonstrating how a single-person team can build an agentic finance application that functions as a financial intelligence agency on-chain.

## Essential Links

- **Live Dashboard**: [aegisagento.vercel.app](https://aegisagento.vercel.app)
- **GitHub**: [HushLuxe/AegisAgent](https://github.com/HushLuxe/AegisAgent)

## Problem

Crypto traders and investors lack a unified intelligence layer that combines on-chain forensic data with macro context, news sentiment, and institutional flow signals. Existing tools are fragmented — market data in one place, news in another, macro events elsewhere. No system autonomously synthesizes all these signals into actionable, risk-adjusted intelligence.

## Solution

AegisAgent is a fully autonomous AI agent that runs a **7-step intelligence pipeline** every cycle:

1. **SoSoValue Data Collection** — Ingests market snapshots, news feeds, ETF flows, macro events, BTC treasuries, and index data via SoSoValue API (7 modules)
2. **On-Chain Forensics** — Collects token data via DexScreener + Moralis for holder analysis
3. **Forensic Engine V5** — Computes 100+ proprietary metrics (SAI, LFI, TFA, WCC, BPI, RSI, Bull Flags, Fibonacci)
4. **AI Synthesis** — Venice.ai (Llama 3.3 70B) generates structured risk narratives incorporating SoSoValue intelligence
5. **Signal Tracking** — Compares current vs previous cycle for delta detection
6. **Autonomous Alerts** — Telegram notifications for high-priority signals
7. **Dashboard Export** — Live dashboard with SoSoValue intelligence panels

## SoSoValue API Integration

AegisAgent deeply integrates **7 of 9 SoSoValue API modules**:

| SoSoValue Module | Usage in AegisAgent |
|-----------------|---------------------|
| **Currency & Pairs** | Market snapshots, price, volume, 24h change for 17 tracked assets |
| **ETF** | ETF flow signals (inflow/outflow) for institutional sentiment |
| **SoSoValue Index** | SSI and SSSIAGG index tracking for market benchmarking |
| **Crypto Stocks** | Sector spotlight data for cross-market correlation |
| **BTC Treasuries** | Institutional BTC accumulation signals |
| **Feeds** | News sentiment analysis (bullish/bearish/neutral scoring) |
| **Macro** | Macroeconomic event calendar for risk assessment |

## Architecture

```
SoSoValue API → ForensicEngineV5 → Venice AI → Dashboard
     ↓                ↓               ↓           ↓
  Market Data    100+ Metrics    Risk Narratives  Live UI
  News Sentiment  SAI/LFI/TFA    Phase Analysis   Alerts
  ETF Flows       WCC/BPI        Confidence Score  Memory
  Macro Events    Bull Flags     Structural Insight
```

## Forensic Metric Suite

### SAI — Sovereign Anomaly Index
Weighted composite (0-10) integrating liquidity depth, directional flow, holder concentration, and structural momentum.

### LFI — Liquidity Fragility Index
Simulated price impact of a top-wallet exit event. Alert at LFI > 0.6.

### TFA — Tactical Flow Analysis
Net buy/sell pressure over 24h, normalised against on-chain volume.

### WCC — Whale Concentration Coefficient
Gini-derived supply concentration across top 20 wallets.

### Additional Metrics
`LCR` · `DAI` · `ICR` · `IPS` · `BPI` · `BER` · `RSI 1H/1D` · `Bull Flag (Class 1/2/3)` · `Fibonacci Target` · `NBP` · `EV` · `VWAD` · `SCR` · `TCI` · `FCI`

## API Reference

### `GET /api/forensics`
Returns the active forensic state of all monitored tokens.

### `GET /api/sosovalue?module=all`
Returns live SoSoValue intelligence (market, news, macro, ETF, treasuries, indices).

### `GET /api/status`
Health check endpoint.

## Local Setup

```bash
# 1. Clone
git clone https://github.com/HushLuxe/AegisAgent.git
cd AegisAgent

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install frontend dependencies
cd frontend && npm install && cd ..

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 5. Run the full agent pipeline
python3 backend/agent.py

# 6. Launch the frontend (separate terminal)
cd frontend && npm run dev
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `SOSO_API_KEY` | **SoSoValue API key** (required — primary data source) |
| `VENICE_API_KEY` | Venice.ai LLM for sovereign narrative generation |
| `GROQ_API_KEY` | Groq LLM fallback |
| `MORALIS_API_KEY` | On-chain holder analysis |
| `TELEGRAM_BOT_TOKEN` | Autonomous alert delivery |
| `KV_REST_API_URL` | Upstash Redis persistence |

## Project Structure

```
AegisAgent/
├── backend/
│   ├── agent.py                  # Pipeline orchestrator (7-step cycle)
│   ├── sosovalue_client.py       # SoSoValue API client (all 9 modules)
│   ├── sosovalue_collector.py    # SoSoValue data collection step
│   ├── collector.py              # On-chain data collector
│   ├── forensic_engine_v5.py     # 100+ metric computation engine
│   ├── report_builder.py         # Forensic report generation
│   ├── request_analysis.py       # AI synthesis
│   ├── signal_tracker.py         # Signal delta tracking
│   ├── export_memory_json.py     # Dashboard data export
│   └── telegram_alerts.py        # Autonomous alert delivery
├── api/
│   ├── forensics.py              # /api/forensics — full forensic pipeline
│   ├── sosovalue.py              # /api/sosovalue — SoSoValue intelligence
│   └── status.py                 # /api/status — health check
├── frontend/
│   └── src/
│       ├── pages/Dashboard.jsx   # Dashboard with SoSoValue Intel Panel
│       └── pages/Landing.jsx     # Landing page
├── config/
│   ├── settings.py               # Configuration (SoSoValue API)
│   └── tokens.json               # Tracked token addresses
├── PROMPT_ANALYSIS.md            # Forensic analysis LLM prompt
├── requirements.txt              # Python dependencies
└── .env.example                  # Environment variable template
```

---

*Autonomous intelligence. SoSoValue-powered. Built for the Buildathon.*
