# AegisAgent — Agent Capabilities & Interface

> Autonomous forensic intelligence agent powered by SoSoValue API.

## What AegisAgent Does

AegisAgent is an agentic finance application that combines SoSoValue's on-chain data infrastructure with proprietary forensic analysis to deliver institutional-grade crypto intelligence.

- **Runs every 60 minutes** via Vercel Cron
- **Ingests live data** from SoSoValue API across 7 modules (market, news, macro, ETF, treasuries, indices, sectors)
- **Collects on-chain data** via DexScreener + Moralis
- **Computes 100+ proprietary metrics** through `ForensicEngineV5` (whale clustering, liquidity fragility, volatility divergence, etc.)
- **Generates structured forensic narratives** via Venice.ai (LLaMA 3.3 70B) — sovereign, private
- **Emits autonomous alerts** via Telegram for high-priority signals
- **Exports live dashboard data** with SoSoValue intelligence panels

## Agent Interface

### REST API (Vercel Serverless)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/forensics` | `GET` | Latest forensic scan result |
| `/api/forensics?token=<addr>` | `GET` | Token-specific forensic analysis |
| `/api/sosovalue?module=all` | `GET` | SoSoValue intelligence (market, news, macro, ETF, treasuries, indices) |
| `/api/status` | `GET` | Agent health & last scan timestamp |

### Pipeline Steps

1. **SoSoValue Collection** — Ingests market snapshots, news sentiment, ETF flows, macro events, BTC treasuries, and index data
2. **On-Chain Collection** — Fetches token data (liquidity, holders, OHLCV)
3. **Forensic Analysis** — Computes 100+ metrics (SAI, LFI, TFA, WCC, BPI, etc.)
4. **AI Synthesis** — Generates structured risk narratives incorporating SoSoValue intelligence
5. **Signal Tracking** — Compares current vs previous cycle for delta detection
6. **Alert Delivery** — Sends Telegram notifications for critical signals
7. **Dashboard Export** — Publishes `memory.json` with SoSoValue data for frontend

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Runtime | Python 3.11 / Vercel Serverless |
| Data Source | SoSoValue API (7 modules) |
| On-chain Data | DexScreener + Moralis |
| LLM | LLaMA 3.3 70B via Venice.ai |
| Storage | Vercel KV (Redis) |
| Frontend | React + Tailwind (Vercel) |
| Forensics | ForensicEngineV5 (custom) |
| Alerts | Telegram Bot API |

## Live Deployment

- **Dashboard:** [https://aegisagento.vercel.app](https://aegisagento.vercel.app)
- **GitHub:** [https://github.com/hushluxe/aegisagent](https://github.com/hushluxe/aegisagent)

## SoSoValue Buildathon

Built for the **SoSoValue Buildathon** — demonstrating how a single-person team can build an agentic finance application that functions as a financial intelligence agency.

**Judging Criteria Alignment:**
- User Value & Practical Impact (30%)
- Functionality & Working Demo (25%)
- Logic, Workflow & Product Design (20%)
- Data / API Integration (15%)
- UX & Clarity (10%)
