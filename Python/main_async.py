import subprocess
import sys
import os
import signal
import logging
import time

# Deferred logging setup until main to establish log file
logger = logging.getLogger("DemeterLauncher")

def main():
    # Determine paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SERVICE_SCRIPT = os.path.join(BASE_DIR, "src", "proyecto_demeter", "core", "async_service.py")
    
    # 1. Setup Logging
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(LOG_DIR, f"session_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger.info("--- [START] Demeter V2 Backend Launcher ---")
    logger.info(f"Logging to: {log_file}")

    # Verify Environment
    # Try to find venv python or use system one if suitable
    VENV_PYTHON = os.path.join(BASE_DIR, ".venv", "bin", "python")
    
    if not os.path.exists(VENV_PYTHON):
        # Fallback for when running inside venv already or if venv structure differs
        if sys.prefix != sys.base_prefix:
            VENV_PYTHON = sys.executable
        else:
            logger.error(f"[ERR] Virtual environment not found at {VENV_PYTHON}")
            logger.info("Please run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt")
            sys.exit(1)

    if not os.path.exists(SERVICE_SCRIPT):
        logger.error(f"[ERR] Service script not found at {SERVICE_SCRIPT}")
        sys.exit(1)

    service_process = None

    def signal_handler(sig, frame):
        logger.info("[SHUTDOWN] Signal Received. Terminating Service...")
        if service_process:
            service_process.terminate()
            try:
                service_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                service_process.kill()
        logger.info("[EXIT] Goodbye.")
        sys.exit(0)

    # Register Signal Handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    def check_and_kill_port(port=8888):
        """Check if port is in use and kill the process using it."""
        try:
            # Find PID using port
            result = subprocess.run(
                ["lsof", "-t", "-i", f":{port}"], 
                capture_output=True, 
                text=True
            )
            pids = result.stdout.strip().split('\n')
            
            for pid in pids:
                if pid:
                    pid = int(pid)
                    logger.warning(f"[WARN] Port {port} is busy. Killing PID {pid}...")
                    os.kill(pid, signal.SIGKILL)
                    time.sleep(1) # Give it a moment to die
        except Exception as e:
            logger.warning(f"Could not check/kill port {port}: {e}")

    try:
        # Pre-flight check: Ensure port 8888 is free
        check_and_kill_port(8888)

        # Start Backend Service
        logger.info(f"[EXEC] Executing: {VENV_PYTHON} {SERVICE_SCRIPT}")
        
        # Pass environment variables if needed
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1" # Ensure logs flow immediately
        env["DEMETER_LOG_FILE"] = log_file # Pass log file path to service

        service_process = subprocess.Popen(
            [VENV_PYTHON, SERVICE_SCRIPT],
            stdout=sys.stdout,
            stderr=sys.stderr,
            env=env,
            cwd=BASE_DIR 
        )
        
        logger.info(f"[OK] Service Started (PID: {service_process.pid})")
        
        # Monitor Process
        while True:
            ret_code = service_process.poll()
            if ret_code is not None:
                logger.warning(f"[WARN] Service exited unexpectedly with code {ret_code}")
                break
            time.sleep(1)

    except Exception as e:
        logger.error(f"[ERR] Execution Error: {e}")
        if service_process:
            service_process.kill()
        sys.exit(1)

if __name__ == "__main__":
    main()
