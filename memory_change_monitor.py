"""
Memory Change Monitor for Zelda: Link's Awakening

This script monitors memory changes with each tick and logs the changing addresses to a file.
It helps identify important game state addresses by tracking which memory locations change
during gameplay.

Usage:
    python memory_change_monitor.py

The script will create a log file named 'memory_changes.log' that records all memory changes.
"""
from pyboy import PyBoy
import time
import os
from datetime import datetime

def monitor_memory_changes():
    """Monitor memory changes in Zelda: Link's Awakening."""
    rom_path = "zelda.gbc"
    log_file = "memory_changes.log"
    
    print(f"Starting Zelda: Link's Awakening Memory Change Monitor")
    print(f"Changes will be logged to {log_file}")
    print("Press Ctrl+C to exit")
    
    pyboy = PyBoy(rom_path, window="SDL2", scale=3)
    pyboy.set_emulation_speed(1)  # Normal speed
    
    with open(log_file, "w") as f:
        f.write(f"Zelda: Link's Awakening Memory Change Monitor\n")
        f.write(f"Started: {datetime.now()}\n\n")
        f.write("Format: [Frame] [Address] [Old Value] -> [New Value]\n\n")
    
    print("\nSkipping title screen...")
    for _ in range(100):
        pyboy.tick()
    
    from pyboy.utils import WindowEvent
    pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
    pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
    
    for _ in range(50):
        pyboy.tick()
    
    print("\nWaiting 30 seconds for manual navigation through loading screens...")
    print("Please navigate through any loading screens during this time.")
    print("Memory monitoring will start after the 30-second delay.")
    
    regions = [
        (0xC000, 0xC100),  # Reverse-engineered player data
        (0xD400, 0xD500),  # Destination coordinates and other data
        (0xDB00, 0xDC00)   # Player stats, inventory, game state
    ]
    
    start_time = time.time()
    while time.time() - start_time < 30:
        pyboy.tick()
        elapsed = int(time.time() - start_time)
        if elapsed % 5 == 0 and elapsed > 0:
            print(f"  {30 - elapsed} seconds remaining...")
    
    print("\nStarting memory monitoring...")
    print("Play the game normally. Memory changes will be logged to the file.")
    
    previous_memory = {}
    for start, end in regions:
        for addr in range(start, end):
            previous_memory[addr] = pyboy.memory[addr]
    
    try:
        while True:
            pyboy.tick()
            
            changes = []
            for start, end in regions:
                for addr in range(start, end):
                    current_value = pyboy.memory[addr]
                    if addr in previous_memory and current_value != previous_memory[addr]:
                        changes.append((addr, previous_memory[addr], current_value))
                        previous_memory[addr] = current_value
            
            if changes:
                with open(log_file, "a") as f:
                    for addr, old_value, new_value in changes:
                        f.write(f"[{pyboy.frame_count}] 0x{addr:04X}: {old_value} -> {new_value}\n")
                
                if pyboy.frame_count % 60 == 0:  # Show summary every ~1 second
                    print(f"\nFrame {pyboy.frame_count}: {len(changes)} memory changes detected")
                    print(f"Changes logged to {log_file}")
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    finally:
        pyboy.stop()
        print("Game closed.")
        print(f"Memory changes have been logged to {log_file}")

if __name__ == "__main__":
    monitor_memory_changes()
