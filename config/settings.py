import os
from dotenv import load_dotenv
load_dotenv()

# ── API Keys (set via environment variables) ────────────────────────────────
DEXSCREENER_API   = "https://api.dexscreener.com/latest/dex/tokens/"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
VENICE_API_KEY = os.environ.get("VENICE_API_KEY")
# Discord Webhook pour OpenClaw Agent
MORALIS_API_KEY   = os.environ.get("MORALIS_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID  = os.environ.get("TELEGRAM_CHAT_ID", "")
MOLTBOOK_API_KEY  = os.environ.get("MOLTBOOK_API_KEY", "")

# ── SoSoValue API ───────────────────────────────────────────────────────────
SOSO_API_KEY      = os.environ.get("SOSO_API_KEY", "")
SOSO_BASE_URL     = os.environ.get("SOSO_BASE_URL", "https://openapi.sosovalue.com/openapi/v1")

# ── SoDEX API ───────────────────────────────────────────────────────────────
SODEX_REST_SPOT   = os.environ.get("SODEX_REST_SPOT", "https://testnet-gw.sodex.dev/api/v1/spot")
SODEX_REST_PERPS  = os.environ.get("SODEX_REST_PERPS", "https://testnet-gw.sodex.dev/api/v1/perps")
SODEX_WS_SPOT     = os.environ.get("SODEX_WS_SPOT", "wss://testnet-gw.sodex.dev/ws/spot")
SODEX_WS_PERPS    = os.environ.get("SODEX_WS_PERPS", "wss://testnet-gw.sodex.dev/ws/perps")
SODEX_API_KEY_NAME = os.environ.get("SODEX_API_KEY_NAME", "")
SODEX_API_KEY_PRIV = os.environ.get("SODEX_API_KEY_PRIV", "")
SODEX_CHAIN_ID     = int(os.environ.get("SODEX_CHAIN_ID", "138565"))  # 138565=testnet, 286623=mainnet

# ── SoSoValue Tracked Assets ───────────────────────────────────────────────
SOSO_TRACKED_CURRENCIES = [
    "1673723677362319866",  # Bitcoin
    "1673723677362319867",  # Ethereum
    "1673723677362319875",  # Solana
    "1673723677362319869",  # BNB
    "1673723677362319871",  # XRP
    "1673723677362319873",  # Cardano
    "1673723677362319874",  # Dogecoin
    "1673723677362320386",  # TRON
    "1673723677362319883",  # Avalanche
    "1673723677362319887",  # Chainlink
    "1673723677362319877",  # Polkadot
    "1673723677362319903",  # NEAR
    "1673723677362319899",  # Aptos
    "1673723677362319954",  # Sui
    "1673723677362319902",  # Arbitrum
    "1673723677362319919",  # Optimism
]
SOSO_TRACKED_INDICES = ["ssiLayer1", "ssiAI", "ssiDeFi"]

# ── Rate-limit delays (seconds) ─────────────────────────────────────────────
DEXSCREENER_DELAY  = 1.0
GECKOTERMINAL_DELAY = 1.5
MORALIS_DELAY      = 1.0
SOSO_DELAY         = 2.0

# ── Network ──────────────────────────────────────────────────────────────────
CHAIN = "celo"
CHAIN_ID = 42220  # Celo Mainnet

# ── Paywall ──────────────────────────────────────────────────────────────────
CUSD_ADDRESS  = "0x765DE816845861e75A25fCA122bb6898B8B1282a"  # cUSD Mainnet
RECEIVER_ADDR = "0x71fd4359eB2da83C1BCd34f93a1C206d68b1eFba"
