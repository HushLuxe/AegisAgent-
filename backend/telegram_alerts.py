#!/usr/bin/env python3
import os
import json
import requests
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')

load_dotenv()

def send_telegram_alert(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        logging.warning("⚠️ Telegram credentials missing. Skipping alert.")
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        logging.error(f"❌ Telegram API Error: {e}")
        return False

def check_for_alerts():
    memory_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "public", "memory.json")
    
    if not os.path.exists(memory_path):
        logging.error("Memory file not found. Run agent.py first.")
        return

    with open(memory_path, "r") as f:
        data = json.load(f)

    tokens = data.get("tokens", [])
    alerts_triggered = []

    for t in tokens:
        symbol = t.get("symbol", "UNT")
        sai = t.get("sai", 0)
        phase = t.get("phase", "STABLE")
        rsi = t.get("rsi_1h", 50)
        
        # 1. Breakout Alert (Aegis RUPTURE)
        if sai >= 9.0:
            msg = f"🛡️ *AegisAgent RUPTURE DETECTED*\n\n🔥 *${symbol}* is showing extreme breakout momentum!\n📈 SAI Score: {sai}/10\n📊 Phase: {phase}\n\n[View Dashboard](http://localhost:5173/dashboard)"
            alerts_triggered.append(msg)
            
        # 2. Risk Alert (High Volatility/Risk)
        elif sai <= 2.5 and sai > 0:
            msg = f"⚠️ *AegisAgent RISK WARNING*\n\n📉 *${symbol}* is showing high fragility cluster!\n📉 SAI Score: {sai}/10\n📊 Status: HIGH RISK\n\n[Analyze on Celo L2](http://localhost:5173/dashboard)"
            alerts_triggered.append(msg)

    if alerts_triggered:
        logging.info(f"🚀 Sending {len(alerts_triggered)} alerts to Telegram...")
        for a in alerts_triggered:
            send_telegram_alert(a)
    else:
        logging.info("✅ No high-priority alerts found this cycle.")

if __name__ == "__main__":
    check_for_alerts()
