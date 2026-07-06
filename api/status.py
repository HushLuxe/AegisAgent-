import os
import json
import time
from http.server import BaseHTTPRequestHandler
from pathlib import Path


class handler(BaseHTTPRequestHandler):
    """Lightweight health check endpoint for AegisAgent."""

    def log_message(self, format, *args):
        pass

    def _respond(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        project_root = Path(__file__).parent.parent
        memory_path = project_root / "frontend" / "public" / "memory.json"

        last_scan = None
        token_count = 0
        avg_sai = 0

        if memory_path.exists():
            try:
                with open(memory_path) as f:
                    data = json.load(f)
                tokens = data.get("tokens", [])
                token_count = len(tokens)
                if tokens:
                    sais = [t.get("sai", 0) for t in tokens if t.get("sai")]
                    avg_sai = round(sum(sais) / len(sais), 2) if sais else 0
                last_scan = data.get("updated_at") or data.get("timestamp")
            except (json.JSONDecodeError, OSError):
                pass

        env_status = {
            "soso_api_key": bool(os.environ.get("SOSO_API_KEY")),
            "venice_api_key": bool(os.environ.get("VENICE_API_KEY")),
            "groq_api_key": bool(os.environ.get("GROQ_API_KEY")),
            "moralis_api_key": bool(os.environ.get("MORALIS_API_KEY")),
            "private_key": bool(os.environ.get("PRIVATE_KEY")),
            "telegram_bot_token": bool(os.environ.get("TELEGRAM_BOT_TOKEN")),
        }

        ai_providers = []
        if env_status["venice_api_key"]:
            ai_providers.append("venice")
        if env_status["groq_api_key"]:
            ai_providers.append("groq")

        self._respond({
            "status": "operational",
            "agent_id": "AegisAgent",
            "version": "5.1.0",
            "last_scan": last_scan,
            "tokens_monitored": token_count,
            "avg_sai": avg_sai,
            "ai_providers": ai_providers,
            "api_keys_configured": env_status,
            "uptime": "active",
        })
