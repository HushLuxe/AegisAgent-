#!/usr/bin/env python3
"""
AegisAgent — Synthesis Hackathon Registration & Submission Script
Correct API flow based on https://synthesis.devfolio.co/skill.md
"""

import json
import os
import sys
import requests

BASE_URL = "https://synthesis.devfolio.co"
KEY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".synthesis_key")
META_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".synthesis_meta.json")

def load_api_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE) as f:
            return f.read().strip()
    key = os.environ.get("SYNTHESIS_API_KEY", "")
    return key

def load_meta():
    if os.path.exists(META_FILE):
        with open(META_FILE) as f:
            return json.load(f)
    return {}

def save_meta(data):
    meta = load_meta()
    meta.update(data)
    with open(META_FILE, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"✅ Metadata saved to {META_FILE}")

def headers(api_key=None):
    k = api_key or load_api_key()
    return {
        "Authorization": f"Bearer {k}",
        "Content-Type": "application/json"
    }

def cmd_status():
    """Check participant status and team info."""
    api_key = load_api_key()
    meta = load_meta()
    team_id = meta.get("teamId") or meta.get("team_id")
    
    if not api_key:
        print("❌ No API key found. Run: python3 scripts/synthesis_register.py register")
        return
    
    print(f"🔑 API Key: {api_key[:20]}...")
    print(f"📋 Local meta: {json.dumps(meta, indent=2)}")
    
    if team_id:
        resp = requests.get(f"{BASE_URL}/teams/{team_id}", headers=headers(api_key))
        print(f"👥 Team info: {resp.text}")

def cmd_register_init(email, name="HushLuxe"):
    """Step 1: Initiate registration and get pendingId."""
    payload = {
        "name": "AegisAgent",
        "description": "Autonomous sovereign forensic intelligence for the Celo L2 ecosystem. Detects adversarial on-chain patterns via 100+ proprietary metrics and Venice AI-powered narratives.",
        "image": "https://aegisagento.vercel.app/logo.svg",
        "agentHarness": "other",
        "agentHarnessOther": "Antigravity (Google Deepmind Agentic Coding)",
        "model": "llama-3.3-70b",
        "humanInfo": {
            "name": name,
            "email": email,
            "socialMediaHandle": "@hushluxe",
            "background": "builder",
            "cryptoExperience": "yes",
            "aiAgentExperience": "yes",
            "codingComfort": 8,
            "problemToSolve": "Real-time autonomous forensic risk intelligence for Celo L2 tokens — detecting whale manipulation and liquidity fragility before they cause harm."
        }
    }
    resp = requests.post(f"{BASE_URL}/register/init", json=payload)
    data = resp.json()
    print(f"📦 Register init response: {json.dumps(data, indent=2)}")
    
    if "pendingId" in data:
        save_meta({"pendingId": data["pendingId"], "email": email})
        print(f"\n✅ Pending ID saved. Now run:")
        print(f"   python3 scripts/synthesis_register.py verify <OTP_CODE>")

def cmd_verify_email():
    """Send OTP to the registered email."""
    meta = load_meta()
    pending_id = meta.get("pendingId")
    if not pending_id:
        print("❌ No pendingId found. Run: python3 scripts/synthesis_register.py init <email>")
        return
    
    resp = requests.post(f"{BASE_URL}/register/verify/email/send",
                         json={"pendingId": pending_id})
    print(f"📧 OTP sent: {resp.text}")
    print(f"   Check your email for the OTP, then run:")
    print(f"   python3 scripts/synthesis_register.py verify <OTP_CODE>")

def cmd_verify_confirm(otp):
    """Confirm OTP and mark as verified."""
    meta = load_meta()
    pending_id = meta.get("pendingId")
    if not pending_id:
        print("❌ No pendingId found.")
        return
    
    resp = requests.post(f"{BASE_URL}/register/verify/email/confirm",
                         json={"pendingId": pending_id, "otp": otp})
    data = resp.json()
    print(f"✅ Verification result: {json.dumps(data, indent=2)}")
    if data.get("verified"):
        print(f"\n   Now run: python3 scripts/synthesis_register.py complete")

def cmd_complete():
    """Step 3: Complete registration, get apiKey + teamId. Saves everything."""
    meta = load_meta()
    pending_id = meta.get("pendingId")
    if not pending_id:
        print("❌ No pendingId found.")
        return
    
    resp = requests.post(f"{BASE_URL}/register/complete",
                         json={"pendingId": pending_id})
    data = resp.json()
    print(f"🎉 Registration complete: {json.dumps(data, indent=2)}")
    
    if "apiKey" in data:
        # Save API key
        with open(KEY_FILE, "w") as f:
            f.write(data["apiKey"])
        print(f"✅ API key saved to {KEY_FILE}")
        
        # Save all metadata
        save_meta({
            "participantId": data.get("participantId"),
            "teamId": data.get("teamId"),
            "name": data.get("name"),
            "apiKey": data["apiKey"],
            "registrationTxn": data.get("registrationTxn")
        })
        print(f"\n🏆 Registration complete!")
        print(f"   Team ID: {data.get('teamId')}")
        print(f"   Now run: python3 scripts/synthesis_register.py submit")

def cmd_get_tracks():
    """Browse available tracks to find Venice AI and Celo track UUIDs."""
    api_key = load_api_key()
    resp = requests.get(f"{BASE_URL}/catalog?page=1&limit=50", headers=headers(api_key))
    data = resp.json()
    print(f"🏆 Available tracks:")
    for item in data.get("items", []):
        print(f"  - [{item.get('uuid')}] {item.get('name')} ({item.get('company', '')})")

def cmd_submit(repo_url="https://github.com/hushluxe/aegisagent"):
    """Submit the project using the correct POST /projects endpoint."""
    api_key = load_api_key()
    meta = load_meta()
    team_id = meta.get("teamId") or meta.get("team_id")
    
    if not team_id:
        print("❌ No teamId found. Run: python3 scripts/synthesis_register.py status")
        return
    
    # First, get track UUIDs
    tracks_resp = requests.get(f"{BASE_URL}/catalog?page=1&limit=50", headers=headers(api_key))
    tracks_data = tracks_resp.json()
    
    # Find Venice AI and Celo tracks
    track_uuids = []
    for item in tracks_data.get("items", []):
        name = item.get("name", "").lower()
        company = item.get("company", "").lower()
        if "venice" in name or "private" in name or "venice" in company:
            track_uuids.append(item["uuid"])
            print(f"✅ Found Venice track: {item['name']} ({item['uuid']})")
        if "celo" in name or "celo" in company:
            track_uuids.append(item["uuid"])
            print(f"✅ Found Celo track: {item['name']} ({item['uuid']})")
    
    # Always include the Open Track
    for item in tracks_data.get("items", []):
        if "open" in item.get("name", "").lower() or "open" in item.get("slug", "").lower():
            if item["uuid"] not in track_uuids:
                track_uuids.append(item["uuid"])
                print(f"✅ Found Open track: {item['name']} ({item['uuid']})")
    
    if not track_uuids:
        # Fallback: use first 2 tracks
        track_uuids = [item["uuid"] for item in tracks_data.get("items", [])[:2]]
        print(f"⚠️  No specific tracks found, using: {track_uuids}")
    
    payload = {
        "teamUUID": team_id,
        "name": "AegisAgent",
        "description": "AegisAgent is a fully autonomous AI forensic agent running natively on Celo L2. Every 60 minutes, it ingests live on-chain data across monitored Celo tokens and computes 100+ proprietary metrics through ForensicEngineV5. A sovereign LLM (Venice.ai) synthesizes all signals into a structured forensic narrative with zero human input. Full per-token intelligence is monetized via a non-custodial x402 micropayment subscription (0.1 CELO / 24h).",
        "problemStatement": "The Celo ecosystem lacks real-time, autonomous on-chain risk intelligence. Traders, protocols, and investors have no systematic way to detect liquidity fragility, whale manipulation, or adversarial patterns in Celo-native tokens before they cause harm. Existing tools are reactive, manual, and do not model the full on-chain signal surface.",
        "repoURL": repo_url,
        "trackUUIDs": track_uuids,
        "conversationLog": "Human-agent collaborative build. The human (HushLuxe) designed the forensic metric architecture and x402 subscription model. The agent (AegisAgent via Antigravity/Deepmind) implemented ForensicEngineV5, Celo on-chain integrations, Venice AI narrative generation, and the Vercel deployment pipeline.",
        "submissionMetadata": {
            "agentFramework": "other",
            "agentFrameworkOther": "Custom ForensicEngineV5 pipeline",
            "agentHarness": "other",
            "agentHarnessOther": "Antigravity (Google Deepmind Agentic Coding)",
            "model": "llama-3.3-70b",
            "skills": ["celo-forensics", "on-chain-analysis", "venice-ai", "x402-payments"],
            "tools": ["Venice.ai", "Moralis", "Celo L2", "Vercel", "Nanobot"],
            "helpfulResources": [
                "https://docs.venice.ai",
                "https://docs.moralis.io",
                "https://docs.celo.org"
            ],
            "intention": "continuing",
            "intentionNotes": "Planning to deploy AegisAgent commercially as a premier Celo risk intelligence platform."
        },
        "deployedURL": "https://aegisagento.vercel.app",
        "videoURL": "https://www.loom.com/share/511cc349479841839e2bb760fff0ca71"
    }
    
    print(f"\n📦 Submitting project with payload:")
    print(json.dumps({k: v for k, v in payload.items() if k != "conversationLog"}, indent=2))
    
    resp = requests.post(f"{BASE_URL}/projects", json=payload, headers=headers(api_key))
    data = resp.json()
    print(f"\n🎉 Submission response ({resp.status_code}): {json.dumps(data, indent=2)}")
    
    if "uuid" in data:
        save_meta({"projectUUID": data["uuid"], "projectStatus": data.get("status")})
        print(f"\n✅ PROJECT SUBMITTED! UUID: {data['uuid']}")
        print(f"   Next step: python3 scripts/synthesis_register.py publish")

def cmd_publish():
    """Publish the submitted draft project."""
    api_key = load_api_key()
    meta = load_meta()
    project_uuid = meta.get("projectUUID")
    
    if not project_uuid:
        print("❌ No projectUUID found. Run submit first.")
        return
    
    resp = requests.post(f"{BASE_URL}/projects/{project_uuid}/publish",
                         headers=headers(api_key))
    print(f"🚀 Publish response ({resp.status_code}): {resp.text}")

def print_usage():
    print("""
Usage: python3 scripts/synthesis_register.py <command> [args]

Commands:
  status                 - Check current registration status
  tracks                 - List available tracks with UUIDs
  init <email> [name]    - Step 1: Initiate registration
  send-otp               - Step 2a: Send OTP to registered email
  verify <OTP_CODE>      - Step 2b: Confirm OTP
  complete               - Step 3: Complete registration, get API key + teamId
  submit [repo_url]      - Submit project to Synthesis
  publish                - Publish the submitted project
""")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if cmd == "status":
        cmd_status()
    elif cmd == "tracks":
        cmd_get_tracks()
    elif cmd == "init":
        email = sys.argv[2] if len(sys.argv) > 2 else input("Enter your email: ")
        name = sys.argv[3] if len(sys.argv) > 3 else "HushLuxe"
        cmd_register_init(email, name)
    elif cmd == "send-otp":
        cmd_verify_email()
    elif cmd == "verify":
        otp = sys.argv[2] if len(sys.argv) > 2 else input("Enter OTP: ")
        cmd_verify_confirm(otp)
    elif cmd == "complete":
        cmd_complete()
    elif cmd == "reset-confirm":
        reset_id = sys.argv[2] if len(sys.argv) > 2 else input("Enter resetId: ")
        otp = sys.argv[3] if len(sys.argv) > 3 else input("Enter OTP: ")
        resp = requests.post(f"{BASE_URL}/reset/confirm", json={"resetId": reset_id, "otp": otp})
        data = resp.json()
        print(f"🔑 Reset response: {json.dumps(data, indent=2)}")
        if "apiKey" in data:
            with open(KEY_FILE, "w") as f:
                f.write(data["apiKey"])
            save_meta({
                "participantId": data.get("participantId"),
                "name": data.get("name"),
                "apiKey": data["apiKey"]
            })
            print(f"\n✅ New API key saved to {KEY_FILE}")
            print(f"   Now get your teamId: python3 scripts/synthesis_register.py get-team")
    elif cmd == "get-team":
        # Try to get team info using the participant endpoint
        api_key = load_api_key()
        for endpoint in ["/me", "/participants/me", "/participant/me", "/participant"]:
            r = requests.get(f"{BASE_URL}{endpoint}", headers=headers(api_key))
            if r.status_code == 200:
                data = r.json()
                print(f"✅ Got participant: {json.dumps(data, indent=2)}")
                team_id = data.get("teamId") or data.get("team", {}).get("uuid")
                if team_id:
                    save_meta({"teamId": team_id})
                break
            print(f"   {endpoint}: {r.status_code}")
    elif cmd == "submit":
        repo_url = sys.argv[2] if len(sys.argv) > 2 else "https://github.com/hushluxe/aegisagent"
        cmd_submit(repo_url)
    elif cmd == "publish":
        cmd_publish()
    else:
        print_usage()
