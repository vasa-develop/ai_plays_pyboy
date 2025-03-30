"""
Position-Focused Memory Dump Tool for Zelda: Link's Awakening

This script runs the game in render mode and captures memory snapshots
with a focus on position tracking. It performs consecutive key presses
in the same direction to better identify position-related memory addresses.
"""
from pyboy import PyBoy
from pyboy.utils import WindowEvent
import time
import json
import os
from datetime import datetime
import memory_map_zelda as mem

MEMORY_REGIONS = [
    (0xC000, 0xC010, "Player Position"),        # Player position (focused)
    (0xC010, 0xC020, "Player State"),           # Player state
    (0xC100, 0xC110, "Health/Status"),          # Health and status
    (0xD300, 0xD350, "Enemy States")            # Enemy states
]

POSITION_ADDRESSES = [
    mem.LINK_X_POS,
    mem.LINK_Y_POS,
    mem.LINK_SPRITE_X,
    mem.LINK_SPRITE_Y,
    mem.LINK_DIRECTION_FLAGS,
    mem.LINK_DIRECTION_FLAGS2
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

def dump_memory(pyboy, key_pressed=None, consecutive_count=0):
    """Dump memory regions to a dictionary with position tracking.
    
    Args:
        pyboy: PyBoy instance
        key_pressed: Name of the key being pressed
        consecutive_count: Number of consecutive presses of the same key
    """
    memory_dump = {
        "timestamp": datetime.now().isoformat(),
        "frame": pyboy.frame_count,
        "key_pressed": key_pressed,
        "consecutive_count": consecutive_count,
        "regions": {},
        "position_data": {}
    }
    
    for start, end, name in MEMORY_REGIONS:
        region_data = {}
        for addr in range(start, end):
            value = pyboy.memory[addr]
            region_data[f"0x{addr:04X}"] = value
        memory_dump["regions"][name] = region_data
    
    for addr in POSITION_ADDRESSES:
        addr_hex = f"0x{addr:04X}"
        memory_dump["position_data"][addr_hex] = pyboy.memory[addr]
    
    return memory_dump

def run_memory_dump_tool():
    """Run the game and capture memory dumps with focus on position tracking."""
    rom_path = "zelda.gbc"
    output_file = "zelda_position_dumps.json"
    
    print("Starting Zelda: Link's Awakening Position-Focused Memory Dump Tool")
    print("This tool will automatically press keys in sequence to track position changes")
    print("Press Ctrl+C to exit and save the memory dumps")
    
    pyboy = PyBoy(rom_path, window="SDL2", scale=3)
    pyboy.set_emulation_speed(1)  # Normal speed
    
    memory_dumps = []
    
    initial_dump = dump_memory(pyboy, "INITIAL")
    memory_dumps.append(initial_dump)
    
    for _ in range(100):
        pyboy.tick()
    
    pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
    pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
    
    for _ in range(60):
        pyboy.tick()
    
    post_title_dump = dump_memory(pyboy, "POST_TITLE")
    memory_dumps.append(post_title_dump)
    
    print("\nWaiting 30 seconds for manual navigation through loading screens...")
    print("Please navigate through any loading screens during this time.")
    start_time = time.time()
    while time.time() - start_time < 30:
        pyboy.tick()
        elapsed = int(time.time() - start_time)
        if elapsed % 5 == 0 and elapsed > 0:
            print(f"  {30 - elapsed} seconds remaining...")
    
    print("\nStarting position tracking tests!")
    
    manual_nav_dump = dump_memory(pyboy, "AFTER_MANUAL_NAVIGATION")
    memory_dumps.append(manual_nav_dump)
    
    directions = [
        {"key": WindowEvent.PRESS_ARROW_UP, "release": WindowEvent.RELEASE_ARROW_UP, "name": "UP"},
        {"key": WindowEvent.PRESS_ARROW_DOWN, "release": WindowEvent.RELEASE_ARROW_DOWN, "name": "DOWN"},
        {"key": WindowEvent.PRESS_ARROW_LEFT, "release": WindowEvent.RELEASE_ARROW_LEFT, "name": "LEFT"},
        {"key": WindowEvent.PRESS_ARROW_RIGHT, "release": WindowEvent.RELEASE_ARROW_RIGHT, "name": "RIGHT"}
    ]
    
    try:
        for direction in directions:
            print(f"\nTesting {direction['name']} direction with consecutive presses...")
            
            print(f"  First press (direction change)...")
            pyboy.send_input(direction["key"])
            pyboy.tick()
            pyboy.send_input(direction["release"])
            
            direction_dump = dump_memory(pyboy, direction["name"], consecutive_count=1)
            memory_dumps.append(direction_dump)
            
            for _ in range(10):
                pyboy.tick()
            
            for i in range(2, 6):  # 4 more presses (5 total)
                print(f"  Press #{i} (movement)...")
                pyboy.send_input(direction["key"])
                pyboy.tick()
                pyboy.send_input(direction["release"])
                
                movement_dump = dump_memory(pyboy, direction["name"], consecutive_count=i)
                memory_dumps.append(movement_dump)
                
                for _ in range(10):
                    pyboy.tick()
            
            for _ in range(30):
                pyboy.tick()
            
            with open(output_file, 'w') as f:
                json.dump(memory_dumps, f, indent=2)
            print(f"  Saved {len(memory_dumps)} memory dumps to {output_file}")
        
        print("\nPosition tracking tests completed!")
        
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
