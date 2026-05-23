const hre = require("hardhat");

async function main() {
  const IDENTITY_REGISTRY_ADDRESS = "0x8004A818BFB912233c491871b3d84c89A494BD9e";
  const AGENT_CARD_URI = "https://aegis-agent.vercel.app/agent_card.json"; // Placeholder until hosted

  console.log("🚀 Registering AegisAgent on ERC-8004 Identity Registry...");

  const [deployer] = await hre.ethers.getSigners();
  console.log("Using account:", deployer.address);

  // Simplified ABI for register (ERC-8004 IdentityRegistry)
  const abi = [
    "function register(address owner, string memory tokenURI) public returns (uint256)"
  ];

  const registry = new hre.ethers.Contract(IDENTITY_REGISTRY_ADDRESS, abi, deployer);

  try {
    const tx = await registry.register(deployer.address, AGENT_CARD_URI);
    console.log("⏳ Transaction hash:", tx.hash);
    
    const receipt = await tx.wait();
    console.log("✅ Registration Successful!");
    
    // The AgentID is usually emitted in an event or returned. 
    // For now, we'll let the user know the transaction is complete.
  } catch (error) {
    console.error("❌ Registration Failed:", error.message);
    if (error.message.includes("already registered")) {
      console.log("ℹ️ This agent may already be registered on this registry.");
    }
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
