import serial
import time
import struct
import argparse
import sys

# Protocol V2 Constants
SYNC_BYTE = 0xFE
HEADER_SIZE = 6

def calculate_crc(data):
    return sum(data) % 256

def parse_and_print(buffer):
    """Try to find and parse frames in a chunk of bytes"""
    if not buffer: return buffer
    
    # Simple search for SYNC
    while len(buffer) >= HEADER_SIZE + 1: # Header + CRC min
        try:
            # Find Sync
            idx = buffer.index(bytes([SYNC_BYTE]))
            if idx > 0:
                print(f"  [GARBAGE] {buffer[:idx].hex()}")
                buffer = buffer[idx:]
            
            if len(buffer) < HEADER_SIZE:
                break
                
            # Parse Header
            # [SYNC] [LEN] [FLAGS] [SRC] [DST] [CMD]
            length = buffer[1]
            total_len = HEADER_SIZE + length + 1
            
            if len(buffer) < total_len:
                break # Wait for more data
            
            frame = buffer[:total_len]
            rx_crc = frame[-1]
            data_to_hash = frame[1:-1]
            calc_crc = calculate_crc(data_to_hash)
            
            src = frame[3]
            dst = frame[4]
            cmd = frame[5]
            
            status = "OK" if calc_crc == rx_crc else "CRC_ERR"
            
            cmd_name = "UNKNOWN"
            if cmd == 0x04: cmd_name = "PING"
            if cmd == 0x0B: cmd_name = "DATA_REPORT"
            if cmd == 0x06: cmd_name = "ACK"
            
            print(f"RX FRAME [{status}]: {frame.hex().upper()}")
            print(f"  -> Cmd: {cmd_name} ({cmd}), Src: {src}, Dst: {dst}, Len: {length}")
            
            if cmd_name == "DATA_REPORT" and status == "OK":
                payload = frame[6:-1]
                t_int, h_int = struct.unpack('<hh', payload)
                print(f"  -> Temp: {t_int/100.0:.2f}C, Hum: {h_int/100.0:.2f}%")
            
            buffer = buffer[total_len:]
            
        except ValueError:
            # No sync found
            print(f"  [NO SYNC] {buffer.hex()}")
            buffer = b''
            break
            
    return buffer

def main():
    parser = argparse.ArgumentParser(description="Demeter UART Monitor")
    parser.add_argument("port", help="Serial Port (e.g., /dev/serial0)")
    parser.add_argument("--baud", type=int, default=115200)
    args = parser.parse_args()

    print(f"--- Opening {args.port} @ {args.baud} ---")
    try:
        ser = serial.Serial(args.port, args.baud, timeout=0.1)
        ser.flushInput()
    except Exception as e:
        print(f"Error opening port: {e}")
        return

    buffer = b''
    
    try:
        while True:
            if ser.in_waiting:
                chunk = ser.read(ser.in_waiting)
                # print(f"RAW: {chunk.hex()}") 
                buffer += chunk
                buffer = parse_and_print(buffer)
            else:
                time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nExiting...")
        ser.close()

if __name__ == "__main__":
    main()
