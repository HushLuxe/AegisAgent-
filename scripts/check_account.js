const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("💳 Active Account:", deployer.address);
  
  const balance = await deployer.getBalance();
  console.log("💰 Balance:", hre.ethers.utils.formatEther(balance), "CELO");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
