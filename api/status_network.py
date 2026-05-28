import os
import json
import time
import hashlib
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Status Network Testnet Configuration
# Fully gasless Ethereum L2 — no ETH required for transactions
STATUS_NETWORK_RPC = "https://public.sepolia.rpc.status.network"
STATUS_NETWORK_CHAIN_ID = 1660990954
STATUS_NETWORK_EXPLORER = "https://sepoliascan.status.network"


class handler(BaseHTTPRequestHandler):
    """Status Network Telemetry Endpoint for AegisAgent.

    AegisAgent emits a cryptographic telemetry beacon to Status Network on every
    forensic scan cycle. Each beacon encodes the scan timestamp, token count,
    and a SHA-256 fingerprint of the forensic report — creating a verifiable,
    gasless audit trail of agent activity on Status Network.

    The Status Network is fully gasless: no ETH is required for transactions,
    making it ideal for autonomous agent telemetry at scale.
    """

    def log_message(self, format, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        self.end_headers()

    def _respond(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_GET(self):
        """Return Status Network telemetry info — network config and last beacon."""
        try:
            import requests as req
            # Verify Status Network RPC is reachable
            r = req.post(
                STATUS_NETWORK_RPC,
                json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1},
                timeout=5
            )
            rpc_data = r.json()
            block_hex = rpc_data.get("result", "0x0")
            block_number = int(block_hex, 16) if block_hex else 0
        except Exception as e:
            block_number = None
            block_hex = "unavailable"

        self._respond({
            "network": "Status Network Testnet",
            "chainId": STATUS_NETWORK_CHAIN_ID,
            "rpc": STATUS_NETWORK_RPC,
            "explorer": STATUS_NETWORK_EXPLORER,
            "gasless": True,
            "blockNumber": block_number,
            "agentAddress": os.environ.get("OPERATOR_WALLET", "0xE32A943635107CA464a2c1328EFf34AE0bFa8247"),
            "description": "AegisAgent emits forensic audit beacons to Status Network on every scan cycle. Fully gasless.",
        })

    def do_POST(self):
        """Emit a forensic telemetry beacon to Status Network.

        POST /api/status_network
        Body: { "reportHash": "<hex>", "tokenCount": <n>, "scanTimestamp": "<iso>" }

        Since Status Network is fully gasless, this submits a zero-value transaction
        with the forensic fingerprint as calldata — creating an immutable on-chain log
        of every agent scan cycle.
        """
        content_length = int(self.headers.get('Content-Length', 0))
        body = {}
        if content_length > 0:
            raw = self.rfile.read(content_length)
            try:
                body = json.loads(raw)
            except Exception:
                pass

        private_key = os.environ.get("PRIVATE_KEY", "").strip()
        operator = os.environ.get("OPERATOR_WALLET", "0xE32A943635107CA464a2c1328EFf34AE0bFa8247")

        # Build forensic fingerprint
        report_hash = body.get("reportHash") or hashlib.sha256(
            f"{body.get('scanTimestamp', time.time())}{body.get('tokenCount', 0)}".encode()
        ).hexdigest()

        scan_ts = body.get("scanTimestamp", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        token_count = body.get("tokenCount", 0)

        # Calldata encodes the forensic beacon: "AEGIS:<sha256_fingerprint>"
        beacon_payload = f"AEGIS:v1:scan={scan_ts}:tokens={token_count}:hash={report_hash[:16]}"
        calldata_hex = "0x" + beacon_payload.encode().hex()

        if not private_key:
            # Return the unsigned beacon for display (no key configured)
            self._respond({
                "success": False,
                "reason": "PRIVATE_KEY not set — returning beacon data only",
                "beacon": {
                    "network": "Status Network Testnet",
                    "chainId": STATUS_NETWORK_CHAIN_ID,
                    "to": operator,
                    "from": operator,
                    "data": calldata_hex,
                    "value": "0x0",
                    "gasless": True,
                    "fingerprint": report_hash,
                    "scanTimestamp": scan_ts,
                    "tokenCount": token_count,
                    "explorer": STATUS_NETWORK_EXPLORER,
                }
            })
            return

        # With private key: sign and broadcast to Status Network
        try:
            import requests as req
            from eth_account import Account

            account = Account.from_key(private_key)

            # Get nonce
            nonce_r = req.post(STATUS_NETWORK_RPC, json={
                "jsonrpc": "2.0", "method": "eth_getTransactionCount",
                "params": [account.address, "latest"], "id": 1
            }, timeout=5)
            nonce = int(nonce_r.json()["result"], 16)

            # Build tx (gasless — gas price is 0 on Status Network)
            tx = {
                "nonce": nonce,
                "to": account.address,
                "value": 0,
                "gas": 50000,
                "gasPrice": 0,
                "data": calldata_hex.encode() if isinstance(calldata_hex, str) else calldata_hex,
                "chainId": STATUS_NETWORK_CHAIN_ID,
            }

            signed = account.sign_transaction(tx)
            tx_r = req.post(STATUS_NETWORK_RPC, json={
                "jsonrpc": "2.0", "method": "eth_sendRawTransaction",
                "params": [signed.rawTransaction.hex()], "id": 1
            }, timeout=10)

            tx_hash = tx_r.json().get("result")

            self._respond({
                "success": True,
                "txHash": tx_hash,
                "explorer": f"{STATUS_NETWORK_EXPLORER}/tx/{tx_hash}",
                "network": "Status Network Testnet",
                "chainId": STATUS_NETWORK_CHAIN_ID,
                "gasless": True,
                "fingerprint": report_hash,
                "scanTimestamp": scan_ts,
                "tokenCount": token_count,
            })

        except Exception as e:
            self._respond({
                "success": False,
                "error": str(e),
                "beacon": {
                    "network": "Status Network Testnet",
                    "chainId": STATUS_NETWORK_CHAIN_ID,
                    "data": calldata_hex,
                    "gasless": True,
                    "fingerprint": report_hash,
                }
            })
