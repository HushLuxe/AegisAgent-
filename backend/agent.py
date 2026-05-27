#!/usr/bin/env python3
import time
import logging
import subprocess
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)

class AegisAgent:
    def __init__(self):
        self.workspace = os.path.dirname(os.path.abspath(__file__))
        self.python_bin = "python3"
        logging.info("AegisAgent initialized — SoSoValue + Celo L2 pipeline.")

    def run_step(self, script_name):
        script_path = os.path.join(self.workspace, script_name)
        if not os.path.exists(script_path):
            logging.warning(f"Script {script_name} not found. Skipping.")
            return

        logging.info(f"Executing: {script_name}...")
        result = subprocess.run([self.python_bin, script_path], capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"Error in {script_name}:\n{result.stderr}")
        else:
            logging.info(f"Success: {script_name} completed.")

    def execute_cycle(self):
        logging.info("Starting AegisAgent Execution Cycle...")
        
        # 1. Collect SoSoValue intelligence (news, market, macro, ETF, treasuries, indices)
        self.run_step("sosovalue_collector.py")
        
        # 2. Collect on-chain data for Celo ecosystem tokens
        self.run_step("collector.py")
        
        # 3. Run forensic metric computations (SAI, TFA, etc)
        self.run_step("report_builder.py")
        
        # 4. Generate AI synthesis with SoSoValue context
        self.run_step("request_analysis.py")
        
        # 5. Send autonomous alerts for high-priority signals (Rupture/Risk)
        self.run_step("telegram_alerts.py")
        
        # 6. Export memory state for the frontend Dashboard
        self.run_step("export_memory_json.py")
        
        logging.info("Cycle completed. Awaiting next phase.")
        
    def start_loop(self):
        logging.info("AegisAgent standing by. Running cycle every 1 hour.")
        self.execute_cycle()
        while True:
            time.sleep(3600)
            self.execute_cycle()

if __name__ == "__main__":
    agent = AegisAgent()
    agent.execute_cycle()
