# AegisAgent — Agent Capabilities & Interface

> Autonomous forensic intelligence agent on the Celo L2 network.

## What AegisAgent Does

AegisAgent autonomously monitors Celo-native tokens on-chain and generates sovereign, AI-powered forensic risk narratives — with zero human intervention.

- **Runs every 60 minutes** via Vercel Cron
- **Ingests live on-chain data** across monitored Celo tokens via Moralis API
- **Computes 100+ proprietary metrics** through `ForensicEngineV5` (whale clustering, liquidity fragility, volatility divergence, etc.)
- **Generates structured forensic narratives** via Venice.ai (LLaMA 3.3 70B) — sovereign, private, uncensorable
- **Seals findings on-chain** as an immutable Celo transaction hash
- **Emits gasless telemetry beacons** to Status Network (chain 1660990954) — every scan cycle is traceable on-chain at zero cost
- **Executes autonomous defensive swaps** via Uniswap Trading API v1 when critical risk is detected
- **Monetizes access** via non-custodial x402 micropayment subscriptions (0.1 CELO / 24h)

## Agent Interface

### REST API (Vercel Serverless)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/forensics` | `GET` | Latest forensic scan result (public preview) |
| `/api/forensics?token=<addr>` | `GET` | Token-specific forensic analysis |
| `/api/uniswap` | `GET` | Autonomous Uniswap swap route (Celo → USDC) |
| `/api/status_network` | `GET` | Status Network connection info + current block |
| `/api/status_network` | `POST` | Emit forensic beacon tx to Status Network (gasless) |
| `/api/subscribe` | `POST` | Initiate x402 CELO subscription |
| `/api/status` | `GET` | Agent health & last scan timestamp |
| `/api/scan` | `POST` | Trigger manual forensic scan (admin) |

### Nanobot Skills

AegisAgent exposes the following skills via its `nanobot.yaml` manifest:

```yaml
skills:
  - scan_token         # Run forensic scan on a given Celo token address
  - get_risk_report    # Retrieve the latest risk narrative for a token
  - execute_bailout    # Autonomously route defensive swaps via Uniswap API
  - emit_beacon        # Emit gasless forensic telemetry to Status Network
  - subscribe          # Subscribe to token intelligence via x402
  - submit_project     # Autonomous hackathon submission
```

### Invocation

```bash
# Via Nanobot
nanobot agent -m "scan token 0x471EcE3750Da237f93B8E339c536989b8978a438"
nanobot agent -m "get risk report for CELO"

# Via direct API
curl https://aegisagento.vercel.app/api/forensics
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Runtime | Python 3.11 / Next.js |
| LLM | LLaMA 3.3 70B via Venice.ai (sovereign) |
| On-chain Data | Moralis API (Celo L2) |
| Storage | Vercel KV (Redis) |
| Frontend | React + Tailwind (Vercel) |
| Forensics | ForensicEngineV5 (custom) |
| Agent Harness | Nanobot v0.1.4 |
| Payments | x402 (non-custodial CELO) |
| Agentic Finance | Uniswap Trading API v1 (Celo, chain 42220) |
| Telemetry | Status Network Testnet (chain 1660990954, gasless) |
| Chains | Celo L2 Mainnet + Status Network Testnet |

## On-Chain Identity

- **ERC-8004 Agent NFT:** `#35263` on Base
- **Operator Wallet:** `0xE32A943635107CA464a2c1328EFf34AE0bFa8247`
- **Celo Sepolia Contract:** `0x74B24d2cd92046772674bFf9B85c11cFd2b9C3d2`

## Live Deployment

- **Dashboard:** [https://aegisagento.vercel.app](https://aegisagento.vercel.app)
- **Demo Video:** [https://www.loom.com/share/511cc349479841839e2bb760fff0ca71](https://www.loom.com/share/511cc349479841839e2bb760fff0ca71)
- **GitHub:** [https://github.com/hushluxe/aegisagent](https://github.com/hushluxe/aegisagent)

## Hackathon

Built for **The Synthesis** hackathon — March 2026.

**Tracks:**
- 🛡️ Private Agents, Trusted Actions (Venice AI)
- 💸 Agentic Finance (Best Uniswap API Integration)
- 📡 Go Gasless on Status Network
- 🌐 Best Agent on Celo
- 🏆 Synthesis Open Track
