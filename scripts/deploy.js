const hre = require("hardhat");

async function main() {
  console.log("🚀 Deploying AegisAgent to Celo L2 Sepolia...");

  const AegisAgent = await hre.ethers.getContractFactory("AegisAgent");
  const aegis = await AegisAgent.deploy();

  await aegis.waitForDeployment();

  const address = await aegis.getAddress();
  console.log(`✅ AegisAgent deployed to: ${address}`);
  console.log("\nNext steps:");
  console.log(`1. Update Dashboard.jsx with AEGIS_CONTRACT_ADDRESS: ${address}`);
  console.log("2. Verify contract: npx hardhat verify --network celo-sepolia " + address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
