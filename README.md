# 🛡️ AegisAgent
> **Autonomous Forensic Intelligence Agent — Powered by SoSoValue API**

---

[![Live Demo](https://img.shields.io/badge/Live-aegisagento.vercel.app-00E5FF?style=for-the-badge)](https://aegisagento.vercel.app)
[![SoSoValue](https://img.shields.io/badge/Data-SoSoValue%20API-FCFF52?style=for-the-badge)](https://sosovalue.com)
[![Celo L2](https://img.shields.io/badge/Network-Celo%20L2-FCFF52?style=for-the-badge)](https://explorer.celo.org/sepolia/)
[![Sovereign AI](https://img.shields.io/badge/AI-Venice.ai-FF3D00?style=for-the-badge)](https://venice.ai)

## 🚀 Overview

AegisAgent is an autonomous agentic finance application that combines **SoSoValue's on-chain data infrastructure** with proprietary forensic analysis to deliver institutional-grade crypto intelligence. It continuously monitors market data, news sentiment, ETF flows, macro events, and BTC treasuries via SoSoValue API — then computes 100+ forensic metrics and synthesizes actionable risk narratives through sovereign AI (Venice.ai), all without human intervention.

Built for the **SoSoValue Buildathon** — demonstrating how a single-person team can build an agentic finance application that functions as a financial intelligence agency on-chain.

---

### 🔗 Essential Links
- **Live Dashboard**: [aegisagento.vercel.app](https://aegisagento.vercel.app)
- **Demo Video**: [Loom Demo](https://www.loom.com/share/511cc349479841839e2bb760fff0ca71)
- **GitHub**: [HushLuxe/AegisAgent](https://github.com/HushLuxe/AegisAgent)

---

## 🔍 Problem

Crypto traders and investors lack a unified intelligence layer that combines on-chain forensic data with macro context, news sentiment, and institutional flow signals. Existing tools are fragmented — market data in one place, news in another, macro events elsewhere. No system autonomously synthesizes all these signals into actionable, risk-adjusted intelligence.

---

## ✅ Solution

AegisAgent is a fully autonomous AI agent that runs a **6-step intelligence pipeline** every cycle:

1. **SoSoValue Data Collection** — Ingests market snapshots, news feeds, ETF flows, macro events, BTC treasuries, and index data via SoSoValue API (9 modules)
2. **On-Chain Forensics** — Collects Celo L2 token data via DexScreener + Moralis for holder analysis
3. **Forensic Engine V5** — Computes 100+ proprietary metrics (SAI, LFI, TFA, WCC, BPI, RSI, Bull Flags, Fibonacci)
4. **AI Synthesis** — Venice.ai (Llama 3.3 70B) generates structured risk narratives incorporating SoSoValue intelligence
5. **Autonomous Alerts** — Telegram notifications for high-priority signals
6. **Dashboard Export** — Live dashboard with SoSoValue intelligence panels

---

## 📊 SoSoValue API Integration

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

### API Endpoint

```
GET /api/sosovalue?module=all|market|news|macro|etf|treasuries|indices
```

Returns live SoSoValue intelligence data consumed by the dashboard and forensic engine.

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AegisAgent Pipeline                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  SoSoValue   │  │   Forensic   │  │   Venice AI      │  │
│  │  API Client   │→ │   Engine V5  │→ │   Synthesis      │  │
│  │  (9 modules)  │  │  (100+ met)  │  │  (Llama 3.3 70B) │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│        │                                      │              │
│        ▼                                      ▼              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Live Dashboard (React + Tailwind)        │   │
│  │   Forensic Panel · SoSoValue Intel · Alerts · x402   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Uniswap API │  │ Status Network│  │  Celo L2 Chain   │  │
│  │  (Bailout)   │  │  (Beacons)   │  │  (x402 Payments) │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚡ Forensic Metric Suite

### **SAI — Sovereign Anomaly Index**
Weighted composite (0–10) integrating liquidity depth, directional flow, holder concentration, and structural momentum.

### **LFI — Liquidity Fragility Index**
Simulated price impact of a top-wallet exit event. Alert at LFI > 0.6.

### **TFA — Tactical Flow Analysis**
Net buy/sell pressure over 24h, normalised against on-chain volume.

### **WCC — Whale Concentration Coefficient**
Gini-derived supply concentration across top 20 wallets.

### Additional Metrics
`LCR` · `DAI` · `ICR` · `IPS` · `BPI` · `BER` · `RSI 1H/1D` · `Bull Flag (Class 1/2/3)` · `Fibonacci Target` · `NBP` · `EV` · `VWAD` · `SCR` · `TCI` · `FCI`

---

## 🏆 Capabilities

### 🔥 Autonomous Intelligence Loop
Every 60 minutes: SoSoValue data → Forensic analysis → AI synthesis → Dashboard update. Zero human input.

### 📊 SoSoValue Intelligence Panel
The dashboard displays a dedicated SoSoValue intelligence section showing news sentiment, ETF flows, macro risk level, BTC treasury signals, and index performance — all sourced from SoSoValue API.

### 💸 Agentic Finance (Uniswap Integration)
When LFI > 50%, the agent pre-computes an optimal defensive swap route into USDC via Uniswap Trading API v1 on Celo. Users execute with one click.

### 📡 Status Network Telemetry
Cryptographic forensic audit beacons emitted to Status Network (gasless L2) every cycle — immutable, verifiable, zero-cost.

### 💰 On-Chain Economic Autonomy
Non-custodial x402 micropayment subscription (0.1 CELO / 24h) enforced by on-chain smart contract on Celo L2.

---

## 🧭 API Reference

### `GET /api/forensics`
Returns the active forensic state of all monitored tokens.

### `GET /api/sosovalue?module=all`
Returns live SoSoValue intelligence (market, news, macro, ETF, treasuries, indices).

### `GET /api/uniswap?token=<addr>&wallet=<addr>`
Returns an autonomous Uniswap swap route for emergency bailout.

### `POST /api/status_network`
Emits a forensic audit beacon to Status Network.

---

## 🛠️ Local Setup

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
# Edit .env with your API keys (see Environment Variables below)

# 5. Run the full agent pipeline
python3 backend/agent.py

# 6. Launch the frontend (separate terminal)
cd frontend && npm run dev
```

### Health Check

```bash
curl http://localhost:3000/api/status
# Returns: { "status": "operational", "tokens_monitored": 16, ... }
```

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `SOSO_API_KEY` | **SoSoValue API key** (required — primary data source) |
| `VENICE_API_KEY` | Venice.ai LLM for sovereign narrative generation |
| `GROQ_API_KEY` | Groq LLM fallback |
| `MORALIS_API_KEY` | On-chain holder analysis |
| `UNISWAP_API_KEY` | Agentic Finance autonomous swap routing |
| `PRIVATE_KEY` | Celo L2 + Status Network beacon signing |
| `TELEGRAM_BOT_TOKEN` | Autonomous alert delivery |
| `KV_REST_API_URL` | Upstash Redis persistence |

---

## 🏆 SoSoValue Buildathon Submission

### Judging Criteria Alignment

| Category | Weight | How AegisAgent Delivers |
|----------|--------|------------------------|
| **User Value & Practical Impact** | 30% | Autonomous forensic intelligence combining SoSoValue market data with on-chain forensics — traders get institutional-grade risk analysis without manual research |
| **Functionality & Working Demo** | 25% | Live dashboard at aegisagento.vercel.app with real-time SoSoValue data, forensic metrics, and AI narratives |
| **Logic, Workflow & Product Design** | 20% | Clean 6-step pipeline: SoSoValue collection → Forensic analysis → AI synthesis → Dashboard export. Well-documented architecture |
| **Data / API Integration** | 15% | Deep integration of 7 SoSoValue API modules (Currency, ETF, Index, Stocks, Treasuries, Feeds, Macro) + SoDEX testnet endpoint ready |
| **UX & Clarity** | 10% | Dark-themed dashboard with dedicated SoSoValue Intelligence Panel, per-token forensic cards, and actionable alerts |

### What Makes This Strong

- **Genuine SoSoValue integration** — Not just a data fetch; news sentiment, ETF flows, macro events, and treasury signals are woven into the forensic scoring engine
- **Complete flow from data to action** — SoSoValue data → metrics → AI narrative → one-click Uniswap bailout
- **AI-enhanced** — Venice.ai sovereign LLM synthesizes all signals into human-readable risk briefs
- **Risk control** — LFI alerts, WCC clustering detection, autonomous bailout triggers
- **Agentic finance** — Real Uniswap swaps on Celo, x402 micropayments, on-chain report sealing

---

## 📁 Project Structure

```
AegisAgent/
├── backend/
│   ├── agent.py                  # Pipeline orchestrator (7-step cycle + cleanup)
│   ├── sosovalue_client.py       # SoSoValue API client (all 9 modules)
│   ├── sosovalue_collector.py    # SoSoValue data collection step
│   ├── collector.py              # Celo on-chain data collector
│   ├── forensic_engine_v5.py     # 100+ metric computation engine
│   ├── report_builder.py         # Forensic report generation
│   ├── request_analysis.py       # AI synthesis + on-chain sealing
│   ├── signal_tracker.py         # Signal delta tracking
│   ├── export_memory_json.py     # Dashboard data export (incl. SoSoValue)
│   └── telegram_alerts.py        # Autonomous alert delivery
├── api/
│   ├── forensics.py              # /api/forensics — full forensic pipeline
│   ├── sosovalue.py              # /api/sosovalue — SoSoValue intelligence (cached)
│   ├── status.py                 # /api/status — health check endpoint
│   ├── uniswap.py                # /api/uniswap — autonomous swap routing
│   └── status_network.py         # /api/status_network — gasless beacon emission
├── frontend/
│   └── src/
│       ├── pages/Dashboard.jsx   # Dashboard with SoSoValue Intel Panel
│       ├── pages/Landing.jsx     # Dynamic landing page with live stats
│       └── pages/NotFound.jsx    # 404 error page
├── config/
│   ├── settings.py               # Configuration (SoSoValue + SoDEX + Celo)
│   └── tokens.json               # Tracked Celo token addresses
├── contracts/
│   └── AegisAgent.sol            # x402 subscription smart contract (Celo)
├── scripts/                      # Deployment + utility scripts
├── PROMPT_ANALYSIS.md            # Forensic analysis LLM prompt template
├── requirements.txt              # Python dependencies
└── .env.example                  # Environment variable template
```

---

*Autonomous intelligence. SoSoValue-powered. Built for the Buildathon.*
