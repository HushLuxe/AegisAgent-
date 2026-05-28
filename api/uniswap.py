import os
import json
import requests
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Celo configuration
USDC_CELO = "0xcebA9300f2b948710d2653dD7B07f33A8B32118C"
CELO_CHAIN_ID = 42220
UNISWAP_API = "https://trade-api.gateway.uniswap.org/v1"


class handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress default server logging

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        self.end_headers()

    def _respond(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_GET(self):
        """Vercel Serverless Function — Uniswap Trading API proxy for Celo bailout swaps.
        
        Flow: GET /api/uniswap?token=<addr>&wallet=<addr>&amount=<wei>
          1. POST /v1/quote  → get full routing quote
          2. POST /v1/swap   → get unsigned transaction calldata
          3. Return { swap: { to, data, value, chainId }, quote: { ... } }
        """
        url_bits = urlparse(self.path)
        params = parse_qs(url_bits.query)

        token_address = params.get('token', [''])[0]
        wallet_address = params.get('wallet', [''])[0]
        amount = params.get('amount', ['1000000000000000000'])[0]
        api_key = os.environ.get("UNISWAP_API_KEY", "").strip()

        if not api_key:
            self._respond({"error": "Missing UNISWAP_API_KEY. Add it to Vercel environment variables."})
            return

        if not token_address or not wallet_address:
            self._respond({"error": "Missing token or wallet query parameters"})
            return

        api_headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "x-universal-router-version": "2.0",
            "Origin": "https://aegisagento.vercel.app"
        }

        try:
            # === Step 1: Get Quote ===
            quote_body = {
                "tokenIn": token_address,
                "tokenInChainId": CELO_CHAIN_ID,
                "tokenOut": USDC_CELO,
                "tokenOutChainId": CELO_CHAIN_ID,
                "amount": amount,
                "type": "EXACT_INPUT",
                "slippageTolerance": 2.0,
                "routingPreference": "FASTEST",
                "swapper": wallet_address
            }
            r1 = requests.post(f"{UNISWAP_API}/quote", json=quote_body, headers=api_headers, timeout=10)
            quote_data = r1.json()

            if r1.status_code != 200:
                self._respond({"error": "Uniswap quote failed", "details": quote_data})
                return

            # === Step 2: Get Swap Calldata ===
            # Strip permitData / permitTransaction — not needed since no signature for CLASSIC without Permit2
            swap_body = {k: v for k, v in quote_data.items() if k not in ("permitData", "permitTransaction")}
            r2 = requests.post(f"{UNISWAP_API}/swap", json=swap_body, headers=api_headers, timeout=10)
            swap_data = r2.json()

            if r2.status_code != 200:
                self._respond({"error": "Uniswap swap calldata failed", "details": swap_data})
                return

            # === Step 3: Return normalized response ===
            swap_tx = swap_data.get("swap", {})
            self._respond({
                "success": True,
                "swap": {
                    "to": swap_tx.get("to"),
                    "data": swap_tx.get("data"),
                    "value": swap_tx.get("value", "0x00"),
                    "chainId": swap_tx.get("chainId", CELO_CHAIN_ID),
                    "gasLimit": swap_tx.get("gasLimit"),
                    "gasPrice": swap_tx.get("gasPrice"),
                },
                "quoteId": quote_data.get("quote", {}).get("quoteId"),
                "estimatedOutput": quote_data.get("quote", {}).get("output", {}).get("amount"),
                "tokenOut": USDC_CELO
            })

        except requests.exceptions.Timeout:
            self._respond({"error": "Uniswap API timed out. Please retry."})
        except Exception as e:
            self._respond({"error": str(e)})
