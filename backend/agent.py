#!/usr/bin/env python3
import time
import logging
import subprocess
import os
import glob
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)

class AegisAgent:
    def __init__(self):
        self.workspace = os.path.dirname(os.path.abspath(__file__))
        self.python_bin = "python3"
        logging.info("AegisAgent initialized — SoSoValue pipeline.")

    def run_step(self, script_name):
        script_path = os.path.join(self.workspace, script_name)
        if not os.path.exists(script_path):
            logging.warning("Script %s not found. Skipping.", script_name)
            return False

        logging.info("Executing: %s...", script_name)
        try:
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            result = subprocess.run(
                [self.python_bin, script_path],
                capture_output=True,
                encoding="utf-8",
                env=env,
                timeout=300
            )
            if result.returncode != 0:
                logging.error("Error in %s:\n%s", script_name, result.stderr[-500:] if result.stderr else "no stderr")
                return False
            logging.info("Success: %s completed.", script_name)
            return True
        except subprocess.TimeoutExpired:
            logging.error("Timeout in %s (300s limit exceeded)", script_name)
            return False
        except Exception as e:
            logging.error("Unexpected error in %s: %s", script_name, e)
            return False

    def cleanup_old_data(self, days=7):
        base_dir = os.path.dirname(self.workspace)
        raw_dir = os.path.join(base_dir, "data", "raw")
        processed_dir = os.path.join(base_dir, "data", "processed")
        cutoff = datetime.utcnow() - timedelta(days=days)
        removed = 0

        for directory in [raw_dir, processed_dir]:
            if not os.path.exists(directory):
                continue
            for filepath in glob.glob(os.path.join(directory, "forensic_*.json")) + glob.glob(os.path.join(directory, "snapshot_*.json")):
                try:
                    filename = os.path.basename(filepath)
                    ts_str = filename.replace("forensic_", "").replace("snapshot_", "").replace(".json", "")
                    file_time = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
                    if file_time < cutoff:
                        os.remove(filepath)
                        removed += 1
                except (ValueError, OSError):
                    continue

        if removed:
            logging.info("Cleaned up %d old data files (>%d days)", removed, days)

    def execute_cycle(self):
        logging.info("Starting AegisAgent Execution Cycle...")
        failed_steps = []

        # 1. Collect SoSoValue intelligence (news, market, macro, ETF, treasuries, indices)
        if not self.run_step("sosovalue_collector.py"):
            failed_steps.append("sosovalue_collector")

        # 2. Collect on-chain data
        if not self.run_step("collector.py"):
            failed_steps.append("collector")

        # 3. Run forensic metric computations (SAI, TFA, etc)
        if not self.run_step("report_builder.py"):
            failed_steps.append("report_builder")

        # 4. Signal tracking (compare current vs previous reports)
        self.run_step("signal_tracker.py")

        # 5. Generate AI synthesis with SoSoValue context
        if not self.run_step("request_analysis.py"):
            failed_steps.append("request_analysis")

        # 6. Send autonomous alerts for high-priority signals
        self.run_step("telegram_alerts.py")

        # 7. Export memory state for the frontend Dashboard
        self.run_step("export_memory_json.py")

        # 8. Cleanup old data files
        self.cleanup_old_data()

        if failed_steps:
            logging.warning("Cycle completed with failures: %s", ", ".join(failed_steps))
        else:
            logging.info("Cycle completed successfully. Awaiting next phase.")

    def start_loop(self):
        logging.info("AegisAgent standing by. Running cycle every 1 hour.")
        self.execute_cycle()
        while True:
            time.sleep(3600)
            self.execute_cycle()

if __name__ == "__main__":
    agent = AegisAgent()
    agent.execute_cycle()
