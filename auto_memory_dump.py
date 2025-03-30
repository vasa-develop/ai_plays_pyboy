"""
Automatic Memory Dump Tool for Zelda: Link's Awakening

This script runs the game in render mode and automatically captures memory snapshots
after pressing different keys in sequence. The data is saved to a file for analysis.
"""
from pyboy import PyBoy
from pyboy.utils import WindowEvent
import time
import json
import os
from datetime import datetime

MEMORY_REGIONS = [
    (0xC000, 0xC020, "Player Position/State"),  # Player position and state
    (0xC100, 0xC110, "Health/Status"),          # Health and status
    (0xD300, 0xD350, "Enemy States")            # Enemy states
]

KEY_SEQUENCES = [
    {"key": WindowEvent.PRESS_ARROW_UP, "release": WindowEvent.RELEASE_ARROW_UP, "name": "UP", "frames": 10},
    {"key": WindowEvent.PRESS_ARROW_DOWN, "release": WindowEvent.RELEASE_ARROW_DOWN, "name": "DOWN", "frames": 10},
    {"key": WindowEvent.PRESS_ARROW_LEFT, "release": WindowEvent.RELEASE_ARROW_LEFT, "name": "LEFT", "frames": 10},
    {"key": WindowEvent.PRESS_ARROW_RIGHT, "release": WindowEvent.RELEASE_ARROW_RIGHT, "name": "RIGHT", "frames": 10},
    {"key": WindowEvent.PRESS_BUTTON_A, "release": WindowEvent.RELEASE_BUTTON_A, "name": "A", "frames": 5},
    {"key": WindowEvent.PRESS_BUTTON_B, "release": WindowEvent.RELEASE_BUTTON_B, "name": "B", "frames": 5},
    {"key": WindowEvent.PRESS_BUTTON_START, "release": WindowEvent.RELEASE_BUTTON_START, "name": "START", "frames": 5},
    {"key": WindowEvent.PRESS_BUTTON_SELECT, "release": WindowEvent.RELEASE_BUTTON_SELECT, "name": "SELECT", "frames": 5}
]

def dump_memory(pyboy, key_pressed=None):
    """Dump memory regions to a dictionary."""
    memory_dump = {
        "timestamp": datetime.now().isoformat(),
        "frame": pyboy.frame_count,
        "key_pressed": key_pressed,
        "regions": {}
    }
    
    for start, end, name in MEMORY_REGIONS:
        region_data = {}
        for addr in range(start, end):
            value = pyboy.memory[addr]
            region_data[f"0x{addr:04X}"] = value
        memory_dump["regions"][name] = region_data
    
    return memory_dump

def run_memory_dump_tool():
    """Run the game and automatically capture memory dumps after key presses."""
    rom_path = "zelda.gbc"
    output_file = "zelda_memory_dumps.json"
    
    print("Starting Zelda: Link's Awakening Memory Dump Tool")
    print("The tool will automatically press keys and capture memory dumps")
    print("Press Ctrl+C to exit and save the memory dumps")
    
    pyboy = PyBoy(rom_path, window="SDL2", scale=3)
    pyboy.set_emulation_speed(1)  # Normal speed
    
    memory_dumps = []
    
    initial_dump = dump_memory(pyboy, "INITIAL")
    memory_dumps.append(initial_dump)
    print("Captured initial memory dump")
    
    print("Skipping title screen...")
    for _ in range(100):
        pyboy.tick()
    
    pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
    pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
    
    for _ in range(60):
        pyboy.tick()
    
    post_title_dump = dump_memory(pyboy, "POST_TITLE")
    memory_dumps.append(post_title_dump)
    print("Captured post-title screen memory dump")
    
    try:
        print("\nStarting automatic key sequence testing...")
        
        for cycle in range(5):  # 5 cycles through all keys
            print(f"\nCycle {cycle+1}/5:")
            
            for key_info in KEY_SEQUENCES:
                before_dump = dump_memory(pyboy, f"BEFORE_{key_info['name']}")
                memory_dumps.append(before_dump)
                
                print(f"Pressing {key_info['name']} key...")
                pyboy.send_input(key_info['key'])
                
                for _ in range(key_info['frames']):
                    pyboy.tick()
                
                during_dump = dump_memory(pyboy, key_info['name'])
                memory_dumps.append(during_dump)
                
                pyboy.send_input(key_info['release'])
                pyboy.tick()
                
                after_dump = dump_memory(pyboy, f"AFTER_{key_info['name']}")
                memory_dumps.append(after_dump)
                
                for _ in range(30):
                    pyboy.tick()
                
                with open(output_file, 'w') as f:
                    json.dump(memory_dumps, f, indent=2)
                print(f"  Saved {len(memory_dumps)} memory dumps to {output_file}")
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        with open(output_file, 'w') as f:
            json.dump(memory_dumps, f, indent=2)
        print(f"Saved {len(memory_dumps)} memory dumps to {output_file}")
        
        pyboy.stop()
        print("Game closed.")

if __name__ == "__main__":
    run_memory_dump_tool()
