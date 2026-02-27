import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from proyecto_demeter.Hardware.management.device_manager import DeviceManager

def test_device_manager():
    print("--- Testing DeviceManager ---")
    dm = DeviceManager()
    
    # Test Pump 1 -> Node 1, Pin 4
    print("Testing logical pin 1 (Pump 1)...")
    target, pin = dm.translate_pin(1)
    print(f"Result: Node {target}, Pin {pin} (Expected: Node 1, Pin 4)")
    assert target == 1 and pin == 4

    # Test Valve 1 -> Logical Pin 5 -> Node 2, Pin 10
    print("\nTesting logical pin 5 (Valve 1)...")
    target, pin = dm.translate_pin(5)
    print(f"Result: Node {target}, Pin {pin} (Expected: Node 1, Pin 10)")
    assert target == 1 and pin == 10

    # Test invalid pin
    print("\nTesting logical pin 99 (Invalid)...")
    target, pin = dm.translate_pin(99)
    print(f"Result: Node {target}, Pin {pin} (Expected: Node 1, Pin 99 as fallback)")
    assert target == 1 and pin == 99

    print("\n--- All tests passed! ---")

if __name__ == "__main__":
    test_device_manager()
