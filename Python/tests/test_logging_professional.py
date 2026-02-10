import logging
import os
import sys
import time
import subprocess
import glob

# Ensure src is in path for imports if needed, but we are testing via subprocess mainly
# Ensure src is in path for imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, 'src'))
from proyecto_demeter.config import settings

def test_logging_rotation_and_sanity():
    print("--- [TEST] Starting Logging Test ---")
    
    # 1. Clear existing logs to be sure? No, we check new file.
    # 1. Use Settings for Log Dir
    log_dir = str(settings.LOG_DIR)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Check for specific log file
    log_file = os.path.join(log_dir, settings.LOG_FILE)
    initial_size = 0
    if os.path.exists(log_file):
        initial_size = os.path.getsize(log_file)
        
    print(f"Initial log size: {initial_size} bytes for {log_file}")
    
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
        
    # 3. Verify Log File Created/Grown
    if not os.path.exists(log_file):
         print(f"[FAIL] Log file {log_file} does not exist.")
         sys.exit(1)
         
    final_size = os.path.getsize(log_file)
    print(f"Final log size: {final_size} bytes")
    
    if final_size <= initial_size:
        print("[FAIL] Log file did not grow.")
        out, err = proc.communicate()
        print("STDOUT:", out)
        print("STDERR:", err)
        sys.exit(1)
        
    # Get latest log file
    latest_log = log_file
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
