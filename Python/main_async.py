import subprocess
import sys
import os
import signal
import logging
import time
import argparse

# Deferred logging setup until main to establish log file
logger = logging.getLogger("DemeterLauncher")

# Add src to path if needed (though running as module is better, we keep script compat)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from proyecto_demeter.shared.config.provider import settings

def main():
    # Parse CLI Arguments (Overrides Settings)
    parser = argparse.ArgumentParser(description="Demeter V2 Backend Launcher")
    parser.add_argument("--port", default=settings.PORT, help="UART Port")
    parser.add_argument("--host", default=settings.HOST, help="Socket Host")
    parser.add_argument("--socket-port", default=settings.SOCKET_PORT, type=int, help="Socket Port")
    
    args = parser.parse_args()

    # Determine paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SERVICE_SCRIPT = os.path.join(BASE_DIR, "src", "proyecto_demeter", "server", "core", "async_service.py")
    
    
    # 1. Setup Logging using Settings
    log_file = settings.LOG_FILE_PATH
    log_dir = os.path.dirname(log_file)
    os.makedirs(log_dir, exist_ok=True) # Ensure dir exists
    
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
    logger.info(f"Configuration: PORT={args.port}, HOST={args.host}:{args.socket_port}")

    # Verify Environment
    # If running in Github Actions or specific venv, sys.executable is usually correct
    VENV_PYTHON = sys.executable 
    
    # Optional: Check explicitly for .venv only if NOT already in a venv
    potential_venv = os.path.join(BASE_DIR, ".venv", "bin", "python")
    if os.path.exists(potential_venv) and sys.prefix == sys.base_prefix:
        VENV_PYTHON = potential_venv

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
        check_and_kill_port(args.socket_port)

        # Start Backend Service
        logger.info(f"[EXEC] Executing: {VENV_PYTHON} {SERVICE_SCRIPT}")
        
        # Pass environment variables including CLI overrides
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1" # Ensure logs flow immediately
        env["DEMETER_LOG_FILE"] = log_file # Pass log file path to service
        env["DEMETER_PORT"] = args.port
        env["DEMETER_HOST"] = args.host
        env["DEMETER_SOCKET_PORT"] = str(args.socket_port)
        
        # Explicitly set PYTHONPATH to include src
        src_path = os.path.join(BASE_DIR, "src")
        env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")

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
