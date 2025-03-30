"""
Manual Memory Dump Tool for Zelda: Link's Awakening

This script allows manual control of Link while capturing memory dumps
when specific keys are pressed. This helps with accurate position tracking
and direction detection.
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

def dump_memory(pyboy, key_pressed=None, last_position=None):
    """Dump memory regions to a dictionary with position tracking.
    
    Args:
        pyboy: PyBoy instance
        key_pressed: Name of the key being pressed
        last_position: Previous position for comparison
    """
    current_position = (pyboy.memory[mem.LINK_X_POS], pyboy.memory[mem.LINK_Y_POS])
    
    memory_dump = {
        "timestamp": datetime.now().isoformat(),
        "frame": pyboy.frame_count,
        "key_pressed": key_pressed,
        "position": {
            "current": current_position,
            "previous": last_position,
            "changed": last_position is not None and current_position != last_position
        },
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

def run_manual_memory_dump():
    """Run the game in manual mode and capture memory dumps on key presses."""
    rom_path = "zelda.gbc"
    output_file = "zelda_manual_dumps.json"
    
    print("Starting Zelda: Link's Awakening Manual Memory Dump Tool")
    print("You can control Link manually and memory dumps will be captured")
    print("Press the following keys to control Link:")
    print("  Arrow keys: Move Link")
    print("  A/B: Action buttons")
    print("  START: Start button")
    print("  SELECT: Select button")
    print("Press Ctrl+C to exit and save the memory dumps")
    
    pyboy = PyBoy(rom_path, window="SDL2", scale=3)
    pyboy.set_emulation_speed(1)  # Normal speed
    
    memory_dumps = []
    last_position = None
    last_key_pressed = None
    
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
    
    print("\nManual control active! Press keys to move Link and capture memory dumps.")
    print("Position and direction changes will be tracked.")
    
    try:
        while True:
            current_position = (pyboy.memory[mem.LINK_X_POS], pyboy.memory[mem.LINK_Y_POS])
            
            key_pressed = None
            for key, name in KEY_MAPPING.items():
                if pyboy.get_input().get(key):
                    key_pressed = name
                    break
            
            if key_pressed or (last_position is not None and current_position != last_position):
                for _ in range(5):
                    pyboy.tick()
                
                memory_dump = dump_memory(pyboy, key_pressed, last_position)
                memory_dumps.append(memory_dump)
                
                print(f"\nKey pressed: {key_pressed}")
                print(f"Position: {current_position}")
                print(f"Direction flags: {pyboy.memory[mem.LINK_DIRECTION_FLAGS]}")
                
                if memory_dump["position"]["changed"]:
                    print(f"Position changed from {last_position} to {current_position}")
                
                if len(memory_dumps) % 5 == 0:
                    with open(output_file, 'w') as f:
                        json.dump(memory_dumps, f, indent=2)
                    print(f"Saved {len(memory_dumps)} memory dumps to {output_file}")
                
                last_key_pressed = key_pressed
            
            last_position = current_position
            
            pyboy.tick()
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        with open(output_file, 'w') as f:
            json.dump(memory_dumps, f, indent=2)
        print(f"Saved {len(memory_dumps)} memory dumps to {output_file}")
        
        pyboy.stop()
        print("Game closed.")

if __name__ == "__main__":
    run_manual_memory_dump()
