import logging
import os
import sys
import time
import subprocess
import glob

# Ensure src is in path for imports if needed, but we are testing via subprocess mainly
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

def test_logging_rotation_and_sanity():
    print("--- [TEST] Starting Logging Test ---")
    
    # 1. Clear existing logs to be sure? No, we check new file.
    log_dir = os.path.join(BASE_DIR, "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    initial_log_count = len(glob.glob(os.path.join(log_dir, "session_*.log")))
    print(f"Initial log files: {initial_log_count}")
    
    # 2. Run Main Async in MOCK mode
    env = os.environ.copy()
    env["DEMETER_MOCK"] = "True"
    
    print("Launching Backend...")
    proc = subprocess.Popen(
        [sys.executable, "main_async.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.path.join(BASE_DIR),
        env=env,
        text=True
    )
    
    # Let it run for 3 seconds
    time.sleep(3)
    
    # Terminate
    print("Terminating Backend...")
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        proc.kill()
        
    # 3. Verify Log File Created
    final_logs = glob.glob(os.path.join(log_dir, "session_*.log"))
    final_log_count = len(final_logs)
    
    if final_log_count <= initial_log_count:
        print("[FAIL] No new log file created.")
        sys.exit(1)
        
    # Get latest log file
    latest_log = max(final_logs, key=os.path.getctime)
    print(f"Latest Log File: {latest_log}")
    
    with open(latest_log, "r") as f:
        content = f.read()
        
    # 4. Check for Emojis
    # Simple check: scan for common emojis or non-ascii?
    # Actually just checking for the ones we removed is good enough.
    forbidden = ["🚀", "✅", "⚠️", "❌", "🔌", "⚙️", "📡", "🎞️", "💡", "➕", "➖"]
    
    found_emojis = []
    for char in forbidden:
        if char in content:
            found_emojis.append(char)
            
    if found_emojis:
        print(f"[FAIL] Emojis found in log: {found_emojis}")
        print("Log Snippet:")
        print(content[:500])
        sys.exit(1)
    else:
        print("[PASS] No forbidden emojis found.")
        
    # 5. Check ContentSanity
    if "[START]" not in content:
        print("[FAIL] Missing [START] tag.")
        sys.exit(1)
        
    if "[WARN] RUNNING IN MOCK MODE" not in content:
        print("[FAIL] Missing Mock Warning.")
        print("--- LOG CONTENT START ---")
        print(content)
        print("--- LOG CONTENT END ---")
        sys.exit(1)

    print("[PASS] Logging Test Complete.")

if __name__ == "__main__":
    test_logging_rotation_and_sanity()
