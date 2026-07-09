import json
import logging
import os
import sys
from datetime import datetime, timezone

from forensic_engine_v5 import ForensicEngineV5

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base_dir, "data", "raw")
    processed_dir = os.path.join(base_dir, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    snapshots = sorted([f for f in os.listdir(raw_dir) if f.startswith("snapshot_")])
    if not snapshots:
        print("Aucun snapshot trouvé")
        return
    
    latest = snapshots[-1]
    filepath = os.path.join(raw_dir, latest)
    print(f"Analyse de {latest}...")
    
    with open(filepath) as f:
        data = json.load(f)
    
    engine = ForensicEngineV5()
    results = {
        "timestamp": data.get("timestamp"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tokens_count": len(data["tokens"]),
        "tokens": {}
    }
    
    for addr, token_data in data["tokens"].items():
        report = engine.analyze(token_data)
        report_dict = report.to_dict()
        
        # Ajouter les données holders brutes (top 20)
        holders_raw = token_data.get("holders", [])
        if isinstance(holders_raw, list):
            report_dict["top20_holders"] = []
            for h in holders_raw[:20]:
                report_dict["top20_holders"].append({
                    "address": h.get("owner_address", ""),
                    "usd_value": float(h.get("usd_value", 0)),
                    "pct_supply": float(h.get("percentage_relative_to_total_supply", 0)),
                    "is_contract": h.get("is_contract", False),
                    "entity": h.get("entity"),
                    "label": h.get("owner_address_label")
                })
        
        # Ajouter prix et market data
        pool = token_data.get("pool", {})
        report_dict["market_data"] = {
            "price_usd": float(pool.get("priceUsd", 0)),
            "price_change_24h": float(pool.get("priceChange", {}).get("h24", 0)),
            "volume_24h": float(pool.get("volume", {}).get("h24", 0)),
            "liquidity_usd": float(pool.get("liquidity", {}).get("usd", 0)),
            "fdv": float(pool.get("fdv", 0)),
            "mcap": float(pool.get("marketCap", 0)),
            "buys_24h": int(pool.get("txns", {}).get("h24", {}).get("buys", 0)),
            "sells_24h": int(pool.get("txns", {}).get("h24", {}).get("sells", 0))
        }
        
        results["tokens"][addr] = report_dict
        print(f"  ✅ {report.symbol}: SAI={report.convergence.sai}/10, Phase={report.convergence.phase}")
    
    timestamp_str = latest.replace("snapshot_", "").replace(".json", "")
    output_file = os.path.join(processed_dir, f"forensic_{timestamp_str}.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Rapport sauvegardé: {output_file}")
    print(f"📊 {len(results['tokens'])} tokens analysés")

if __name__ == "__main__":
    main()
