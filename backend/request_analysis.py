import hashlib
import os
import json
import requests
from datetime import datetime, timezone

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
VENICE_API_KEY = os.environ.get("VENICE_API_KEY", "")

AI_URL = "https://api.venice.ai/api/v1/chat/completions" if VENICE_API_KEY else "https://api.groq.com/openai/v1/chat/completions"
AI_KEY = VENICE_API_KEY if VENICE_API_KEY else GROQ_API_KEY
AI_MODEL = "llama-3.3-70b" if VENICE_API_KEY else "llama-3.3-70b-versatile"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

SYNTHESIS_OUTPUT = "/tmp/aegis-agent/synthesis.json"

FALLBACK_PROMPT = """You are AegisAgent, an autonomous forensic intelligence agent.
Analyze the provided forensic report JSON and produce a structured synthesis with:
- cycle_summary: 1-2 sentence overview
- critical_alerts: list of tokens requiring immediate attention
- token_briefs: per-token risk level and narrative (2-3 sentences each)
- agent_confidence: HIGH/MEDIUM/LOW based on data completeness
Focus on: holder concentration (WCC), liquidity stress (LFI), and price action signals."""

def load_prompt():
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prompt_path = os.path.join(ROOT_DIR, "PROMPT_ANALYSIS.md")
    try:
        with open(prompt_path) as f:
            return f.read()
    except FileNotFoundError:
        return FALLBACK_PROMPT

def load_forensic_reports():
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_dir = os.path.join(ROOT_DIR, "data", "processed")
    files = sorted([f for f in os.listdir(processed_dir) if f.startswith("forensic_")])
    if not files:
        return None, None
    with open(os.path.join(processed_dir, files[-1])) as f:
        current = json.load(f)
    return current, None

def build_synthesis_json(current, analysis, report_hash=None):
    tokens = current.get("tokens", {})
    token_list = []
    for addr, t in tokens.items():
        conv = t.get("convergence", {})
        token_list.append({
            "symbol": t.get("symbol", addr[:8]),
            "address": addr,
            "sai": conv.get("sai", 0),
            "phase": conv.get("phase", ""),
            "tfa": t.get("flows", {}).get("tfa", 0),
            "bpi": t.get("bull_flag", {}).get("bpi", 0)
        })
    synthesis = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "synthesis_table": token_list,
        "raw_report": analysis,
        "seal": {"report_hash": report_hash} if report_hash else None
    }
    return synthesis

def main():
    current, _ = load_forensic_reports()
    if not current:
        return

    prompt = load_prompt()
    payload = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Analyze: {json.dumps(current, indent=None)}"}
        ],
        "max_tokens": 4000
    }

    r = requests.post(
        AI_URL,
        headers={"Authorization": f"Bearer {AI_KEY}", "Content-Type": "application/json"},
        json=payload,
        timeout=120
    )

    if r.status_code != 200:
        print(f"LLM request failed with status code {r.status_code}: {r.text}")
        return

    analysis = r.json()["choices"][0]["message"]["content"]
    if analysis:
        report_hash = hashlib.sha256(analysis.encode()).hexdigest()
        synthesis = build_synthesis_json(current, analysis, report_hash)
        os.makedirs(os.path.dirname(SYNTHESIS_OUTPUT), exist_ok=True)
        with open(SYNTHESIS_OUTPUT, "w") as f:
            json.dump(synthesis, f, indent=2)
        print(f"AI synthesis saved to {SYNTHESIS_OUTPUT}")

        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            try:
                requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={"chat_id": TELEGRAM_CHAT_ID, "text": analysis[:2000]},
                    timeout=10
                )
            except Exception:
                pass

if __name__ == "__main__":
    main()
