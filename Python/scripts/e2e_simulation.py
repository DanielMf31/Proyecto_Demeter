import sys
import os
import subprocess
import time

# Add python source to path
sys.path.append(os.path.join(os.getcwd(), 'Python', 'python', 'src'))

from proyecto_demeter.protocols.protocol_v2 import DemeterProtocolV2
from proyecto_demeter.protocols.schemas_protocol import SetGpio

def main():
    print("=== DEMETER E2E SIMULATION RUNNER ===")
    
    # 1. Compile C++ Simulator
    print("[1/4] Compiling Native Simulator...")
    compile_cmd = ["/home/danielmf31/.platformio/penv/bin/pio", "run", "-e", "simulator", "-d", "C++"]
    ret = subprocess.call(compile_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    
    if ret != 0:
        print("!!! Compilation Failed.")
        sys.exit(1)
    
    sim_bin = "C++/.pio/build/simulator/program"
    if not os.path.exists(sim_bin):
        print(f"!!! Binary not found: {sim_bin}")
        sys.exit(1)
        
    print("[2/4] Compilation Success. Starting Simulator Process...")
    
    # 2. Launch Simulator Process
    # We pipe stdin (to write bytes) and stdout (to read logs)
    process = subprocess.Popen(
        [sim_bin],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0 # Unbuffered
    )
    
    print("[3/4] Simulator Running. Injecting Commands...")
    
    # 3. Create Commands
    protocol = DemeterProtocolV2()
    
    # CMD 1: Set Pin 4 HIGH
    cmd1 = SetGpio(target_id=1, pin=4, value=1)
    frame1 = protocol.serialize(cmd1)
    
    # CMD 2: Set Pin 5 LOW
    cmd2 = SetGpio(target_id=1, pin=5, value=0)
    frame2 = protocol.serialize(cmd2)
    
    try:
        # Send CMD 1
        print(f" -> Sending: Set GPIO 4=HIGH ({frame1.hex()})")
        process.stdin.write(frame1)
        process.stdin.flush()
        time.sleep(0.1)
        
        # Send CMD 2
        print(f" -> Sending: Set GPIO 5=LOW ({frame2.hex()})")
        process.stdin.write(frame2)
        process.stdin.flush()
        time.sleep(0.1)
        
    except Exception as e:
        print(f"!!! Error writing to process: {e}")
        
    # 4. Verify Output
    print("[4/4] Verifying Output...")
    process.terminate()
    stdout, stderr = process.communicate()
    
    output = stdout.decode('utf-8')
    errors = stderr.decode('utf-8')
    
    print("\n--- SIMULATOR STDOUT ---")
    print(output)
    print("------------------------")
    
    success_count = 0
    if "[GPIO] PIN 4 -> 1" in output:
        print(" SUCCESS: GPIO 4 turned HIGH")
        success_count += 1
    else:
        print(" FAILURE: GPIO 4 did not trigger")
        
    if "[GPIO] PIN 5 -> 0" in output:
        print(" SUCCESS: GPIO 5 turned LOW")
        success_count += 1
    else:
        print(" FAILURE: GPIO 5 did not trigger")
        
    if success_count == 2:
        print("\n E2E SIMULATION PASSED!")
        sys.exit(0)
    else:
        print("\n E2E SIMULATION FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()
