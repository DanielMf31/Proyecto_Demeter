import serial
import time
import sys

def check_uart_loopback(port='/dev/serial0', baudrate=115200):
    print(f"Opening {port} at {baudrate} baud...")
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
    except serial.SerialException as e:
        print(f"ERROR: Could not open port {port}: {e}")
        print("Hint: Check permissions (add user to dialout) or if port is busy.")
        sys.exit(1)

    print("Port opened successfully.")
    
    msg = b"Hello UART Loopback\n"
    print(f"Sending: {msg}")
    ser.write(msg)
    time.sleep(0.1)
    
    if ser.in_waiting > 0:
        received = ser.read(ser.in_waiting)
        print(f"Received: {received}")
        if received == msg:
            print("SUCCESS: Loopback test passed!")
        else:
            print("WARNING: Received data does not match sent data.")
    else:
        print("TIMEOUT: No data received. (Is TX connected to RX?)")
        # For a non-loopback scenario (just checking RX from Gateway), we might just listen
        print("Entering Listen Mode (Press Ctrl+C to exit)...")
        try:
            while True:
                if ser.in_waiting > 0:
                     data = ser.read(ser.in_waiting)
                     print(f"RX: {data}")
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nExiting.")

    ser.close()

if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/serial0'
    check_uart_loopback(port)
