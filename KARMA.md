# AegisAgent — Karma Hackathon Registration

## Project Name
AegisAgent — Sovereign Forensic Intelligence on Celo

---

## Mission Statement
AegisAgent's mission is to make autonomous, institutional-grade on-chain intelligence accessible to every participant in the Celo ecosystem. By running a fully self-sustaining forensic AI agent that continuously monitors token health, detects anomalies, and generates AI-synthesized risk narratives — all gated by a non-custodial micropayment on Celo — we prove that AI agents can operate with genuine economic autonomy, providing real utility to real users without a centralized operator.

---

## Short Description / Tagline
Autonomous on-chain forensic intelligence for the Celo ecosystem. AegisAgent computes 100+ risk metrics per token, every hour, fully autonomously — with access gated by a non-custodial Celo micropayment.

---

## Problem
The Celo ecosystem lacks real-time, autonomous on-chain risk intelligence. Traders, protocols, and investors have no systematic way to detect liquidity fragility, whale manipulation, or adversarial patterns in Celo-native tokens before they cause harm. Existing tools are reactive, manual, and do not model the full on-chain signal surface.

---

## Solution
AegisAgent is a fully autonomous AI forensic agent running natively on Celo L2. Every 60 minutes, it ingests live on-chain data across monitored Celo tokens and computes 100+ proprietary metrics — Sovereign Anomaly Index (SAI), Liquidity Fragility Index (LFI), Tactical Flow Analysis (TFA), Whale Concentration Coefficient (WCC), and Bull Flag structural scoring — through ForensicEngineV5. A Groq LLM synthesizes all signals into a structured forensic narrative with zero human input.

Full per-token intelligence is monetized via a non-custodial x402 micropayment subscription (0.1 CELO / 24h) enforced by an on-chain smart contract on Celo Sepolia, demonstrating genuine agent-native economic autonomy on Celo.

---

## Milestone 1 — Core Autonomous Agent & Forensic Engine
**Status: Completed**

Designed and deployed the full autonomous agent pipeline on Celo L2. Built ForensicEngineV5 from scratch — a Python-based computation engine that fetches live on-chain data (liquidity pools, OHLCV, holder distribution) from DexScreener, GeckoTerminal, and Moralis, then computes 100+ proprietary forensic metrics including SAI, LFI, TFA, WCC, LCR, BPI, and Bull Flag detection. Deployed the AegisSubscription smart contract on Celo Sepolia, implementing a non-custodial x402 micropayment paywall (0.1 CELO / 24h) with on-chain subscription state. Integrated a Groq LLM (LLaMA 3.3-70b) to autonomously generate structured forensic narratives — phase classification, structural insight, and risk assessment — for each monitored token with no human input. Deployed the full stack to Vercel with serverless Python functions and a scheduled cron pipeline.

---

## Milestone 2 — Live Intelligence Dashboard & Submission-Ready Polish
**Status: Completed**

Shipped a production-grade React frontend at aegisagento.vercel.app exposing the full forensic feed to users. The dashboard surfaces real-time SAI scores, LFI fragility, Net Buy Pressure, Whale Concentration, RSI, Bull Flag status, and AI narrative — all populated from live on-chain data fetched in parallel via ThreadPoolExecutor to stay within Vercel serverless execution limits. Implemented a wallet-gated paywall overlay using ethers.js with automatic Celo L2 network switching, subscribed-state verification against the smart contract, and a memory.json fallback for uninterrupted availability. Fixed SPA routing on Vercel, resolved Python cache corruption, updated all frontend copy to be technically accurate, and corrected pricing parity between the UI and the deployed contract. Project is fully deployed, publicly accessible, and submission-ready.

---

## Key Links

- Live Demo: https://aegisagento.vercel.app
- GitHub: https://github.com/HushLuxe/AegisAgent
- Agent Wallet: 0xE32A943635107CA464a2c1328EFf34AE0bFa8247
- Contract (Celo Sepolia): 0x74B24d2cd92046772674bFf9B85c11cFd2b9C3d2
- Track: Track 1 — Best Agent on Celo
