"""
Memory Dump Tool for Zelda: Link's Awakening

This script runs the game in render mode and captures memory snapshots
when movement keys are pressed. The data is saved to a file for analysis.
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

KEY_MAPPING = {
    WindowEvent.PRESS_ARROW_UP: "UP",
    WindowEvent.PRESS_ARROW_DOWN: "DOWN",
    WindowEvent.PRESS_ARROW_LEFT: "LEFT",
    WindowEvent.PRESS_ARROW_RIGHT: "RIGHT",
    WindowEvent.PRESS_BUTTON_A: "A",
    WindowEvent.PRESS_BUTTON_B: "B",
    WindowEvent.PRESS_BUTTON_START: "START",
    WindowEvent.PRESS_BUTTON_SELECT: "SELECT"
}

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
    """Run the game and capture memory dumps on key presses."""
    rom_path = "zelda.gbc"
    output_file = "zelda_memory_dumps.json"
    
    pyboy = PyBoy(rom_path, window="SDL2", scale=3)
    pyboy.set_emulation_speed(1)  # Normal speed
    
    memory_dumps = []
    
    initial_dump = dump_memory(pyboy, "INITIAL")
    memory_dumps.append(initial_dump)
    
    print("Starting Zelda: Link's Awakening Memory Dump Tool")
    print("Press arrow keys to move Link and capture memory dumps")
    print("Press Ctrl+C to exit and save the memory dumps")
    
    for _ in range(100):
        pyboy.tick()
    
    pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
    pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
    
    for _ in range(60):
        pyboy.tick()
    
    post_title_dump = dump_memory(pyboy, "POST_TITLE")
    memory_dumps.append(post_title_dump)
    
    last_key = None
    last_dump_frame = 0
    
    try:
        while True:
            pyboy.tick()
            
            key_pressed = None
            for key, name in KEY_MAPPING.items():
                if pyboy.get_input().get(key):
                    key_pressed = name
                    break
            
            if key_pressed and (key_pressed != last_key or pyboy.frame_count - last_dump_frame > 30):
                print(f"Key pressed: {key_pressed}, capturing memory dump...")
                memory_dump = dump_memory(pyboy, key_pressed)
                memory_dumps.append(memory_dump)
                last_key = key_pressed
                last_dump_frame = pyboy.frame_count
            
            if not key_pressed:
                last_key = None
            
            if pyboy.frame_count % 300 == 0:
                with open(output_file, 'w') as f:
                    json.dump(memory_dumps, f, indent=2)
                print(f"Saved {len(memory_dumps)} memory dumps to {output_file}")
            
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
