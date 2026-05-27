import asyncio
import os
import sys
from web3 import Web3
from dotenv import load_dotenv

# ERC-8004 IdentityRegistry on Celo L2 Sepolia
IDENTITY_REGISTRY_ADDRESS = "0x8004A818BFB912233c491871b3d84c89A494BD9e"
RPC_URL = "https://11142220.rpc.thirdweb.com" # Verified Celo L2 Sepolia

# Minimal ABI — specifically for AegisAgent registration
IDENTITY_REGISTRY_ABI = [
    {
        "name": "register",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "agentURI", "type": "string"}
        ],
        "outputs": [
            {"name": "agentId", "type": "uint256"}
        ]
    }
]

# AegisAgent metadata live production link
AGENT_URI = "https://aegisagento.vercel.app/agent_card.json"

async def run():
    load_dotenv()
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    private_key = os.getenv("PRIVATE_KEY")

    if not w3.is_connected():
        print("❌ Error: Could not connect to Celo L2 Sepolia RPC.")
        return

    account = w3.eth.account.from_key(private_key)

    print(f"🔑 Registering from account: {account.address}")
    print(f"📡 Network: {w3.eth.chain_id} (Celo L2 Sepolia)")
    print(f"🔗 Agent URI: {AGENT_URI}")

    registry = w3.eth.contract(
        address=Web3.to_checksum_address(IDENTITY_REGISTRY_ADDRESS),
        abi=IDENTITY_REGISTRY_ABI
    )

    # 🧪 Simulation
    try:
        sim_result = registry.functions.register(AGENT_URI).call({"from": account.address})
        print(f"🧪 Simulation passed! Expected agentId: {sim_result}")
    except Exception as e:
        print(f"❌ Simulation FAILED: {e}")
        return

    # 🚀 Build & send transaction
    try:
        nonce = w3.eth.get_transaction_count(account.address)
        tx = registry.functions.register(AGENT_URI).build_transaction({
            "from": account.address,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": w3.eth.gas_price,
            "chainId": w3.eth.chain_id,
        })

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        print(f"🚀 Transaction sent! Hash: {tx_hash.hex()}")
        print("⏳ Waiting for confirmation...")

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            print("✅ SUCCESS! AegisAgent is now ERC-8004 registered!")
            print(f"   Tx: https://explorer.celo.org/sepolia/tx/{tx_hash.hex()}")
            print("\n🏆 You are now eligible for the Track 3 ERC-8004 bonus prize!")
        else:
            print("❌ Transaction reverted.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(run())
