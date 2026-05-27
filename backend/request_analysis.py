from web3 import Web3
from eth_account import Account
import hashlib
import os
import time
from datetime import datetime, timezone
import requests
import json
import re
import subprocess

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
VENICE_API_KEY = os.environ.get("VENICE_API_KEY", "")

# LLM Config - Prefer Venice
AI_URL   = "https://api.venice.ai/api/v1/chat/completions" if VENICE_API_KEY else "https://api.groq.com/openai/v1/chat/completions"
AI_KEY   = VENICE_API_KEY if VENICE_API_KEY else GROQ_API_KEY
AI_MODEL = "llama-3.3-70b" if VENICE_API_KEY else "llama-3.3-70b-versatile"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
MOLTBOOK_API_KEY = os.environ.get("MOLTBOOK_API_KEY", "")
MOLTBOOK_URL = "https://www.moltbook.com/api/v1/posts"

# RPC & Account
CELO_RPC = "https://alfajores-forno.celo-testnet.org"
PRIVATE_KEY = os.environ.get("PRIVATE_KEY", "")
AGENT_WALLET = os.environ.get("AGENT_WALLET", "0xE32A943635107CA464a2c1328EFf34AE0bFa8247")

SYNTHESIS_OUTPUT = "/tmp/aegis-agent/synthesis.json"
POSITION_FILE = "/tmp/aegis-agent/mind/position.json"

def load_prompt():
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(ROOT_DIR, "PROMPT_ANALYSIS.md")) as f:
        return f.read()

def load_forensic_reports():
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_dir = os.path.join(ROOT_DIR, "data", "processed")
    files = sorted([f for f in os.listdir(processed_dir) if f.startswith("forensic_")])
    if not files: return None, None
    with open(os.path.join(processed_dir, files[-1])) as f: current = json.load(f)
    previous = None
    if len(files) > 1:
        with open(os.path.join(processed_dir, files[-2])) as f: previous = json.load(f)
    return current, previous

def build_synthesis_json(current, analysis, seal_hash=None, tx_hash=None):
    tokens = current.get("tokens", {})
    token_list = []
    for addr, t in tokens.items():
        conv = t.get("convergence", {})
        token_list.append({
            "symbol": t.get("symbol", addr[:8]),
            "address": addr,
            "sai": conv.get("sai", 0),
            "ces": conv.get("ces", 0),
            "phase": conv.get("phase", ""),
            "tfa": t.get("flows", {}).get("tfa", 0),
            "bpi": t.get("bull_flag", {}).get("bpi", 0)
        })
    synthesis = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "synthesis_table": token_list,
        "raw_report": analysis,
        "seal": {"report_hash": seal_hash, "tx_hash": tx_hash} if seal_hash else None
    }
    return synthesis

def check_and_exit_position():
    if not os.path.exists(POSITION_FILE): return
    try:
        with open(POSITION_FILE, 'r') as f: pos = json.load(f)
        if pos.get("status") == "OPEN" and (time.time() - pos.get("entry_time", 0)) >= 5400:
            print(f"⏳ TIMEOUT (90min) pour {pos['symbol']}. Exit...")
            print(f"[CELO TOOL MOCK] Sell 100% of my {pos['symbol']} ({pos['address']}) for CELO on Celo Sepolia")
            with open(POSITION_FILE, 'w') as f: json.dump({"status": "CLOSED", "last_symbol": pos['symbol']}, f)
    except: pass

def seal_report_onchain(text):
    report_hash = hashlib.sha256(text.encode()).hexdigest()
    
    if not PRIVATE_KEY:
        print("⚠️ No PRIVATE_KEY found. Skipping real on-chain seal.")
        return report_hash, f"mock_hash_{report_hash[:16]}"

    try:
        w3 = Web3(Web3.HTTPProvider(CELO_RPC))
        account = Account.from_key(PRIVATE_KEY)
        
        # Zero-value transaction to self with the hash in data
        tx = {
            'to': account.address,
            'value': 0,
            'gas': 100000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
            'data': f"0x{report_hash}",
            'chainId': 44787 # Celo Sepolia (Alfajores)
        }
        
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_id = w3.to_hex(tx_hash)
        
        print(f"🔗 Sealed on Celo: {tx_id}")
        return report_hash, tx_id
        
    except Exception as e:
        print(f"❌ Failed to seal on Celo: {e}")
        return report_hash, None

def enter_new_position(text, current_data):
    if os.path.exists(POSITION_FILE):
        with open(POSITION_FILE, 'r') as f:
            if json.load(f).get("status") == "OPEN": return
    match = re.search(r'\$([a-zA-Z0-9]{2,10})', text)
    if match:
        symbol = match.group(1).upper()
        addr = next((a for a, i in current_data.get("tokens", {}).items() if i.get("symbol") == symbol), None)
        if addr:
            print(f"[CELO TOOL MOCK] Swap 75% of my CELO balance for {symbol} ({addr}) on Celo Sepolia")
            os.makedirs(os.path.dirname(POSITION_FILE), exist_ok=True)
            with open(POSITION_FILE, 'w') as f: json.dump({"symbol": symbol, "address": addr, "entry_time": time.time(), "status": "OPEN"}, f)

def main():
    check_and_exit_position()
    current, _ = load_forensic_reports()
    if not current: return
    prompt = load_prompt()
    payload = {"model": AI_MODEL, "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": f"Analyze: {json.dumps(current, indent=None)}"}], "max_tokens": 4000}
    r = requests.post(AI_URL, headers={"Authorization": f"Bearer {AI_KEY}", "Content-Type": "application/json"}, json=payload, timeout=120)
    analysis = r.json()["choices"][0]["message"]["content"] if r.status_code == 200 else None
    if analysis:
        h, tx = seal_report_onchain(analysis)
        analysis += f"\n\n🔐 **SEALED ON CELO**: 0x{h[:16]}... (TX: {tx if tx else 'Pending'})"
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json={"chat_id": TELEGRAM_CHAT_ID, "text": analysis})
        synthesis = build_synthesis_json(current, analysis, h, tx)
        os.makedirs(os.path.dirname(SYNTHESIS_OUTPUT), exist_ok=True)
        with open(SYNTHESIS_OUTPUT, "w") as f: json.dump(synthesis, f, indent=2)
        subprocess.run(["curl", "-s", "-X", "POST", MOLTBOOK_URL, "-H", f"Authorization: Bearer {MOLTBOOK_API_KEY}", "-H", "Content-Type: application/json", "-d", json.dumps({"submolt_name":"trading", "title":"Pulse Report", "content": analysis[:400]})])
        enter_new_position(analysis, current)

if __name__ == "__main__": main()
