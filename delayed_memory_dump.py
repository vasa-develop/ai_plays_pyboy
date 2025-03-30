"""
Delayed Memory Dump Tool for Zelda: Link's Awakening

This script adds significant delays between key presses to give the game
more time to process movement and update memory values.
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

def dump_memory(pyboy, key_pressed=None, consecutive_count=0):
    """Dump memory regions to a dictionary.
    
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

def run_delayed_memory_dump():
    """Run the game with delayed key presses and capture memory dumps."""
    rom_path = "zelda.gbc"
    output_file = "zelda_delayed_dumps.json"
    
    print("Starting Zelda: Link's Awakening Delayed Memory Dump Tool")
    print("Testing movement with significant delays between key presses")
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
    
    print("\nStarting automated movement tests with delays...")
    
    test_sequence = [
        ("UP", WindowEvent.PRESS_ARROW_UP, WindowEvent.RELEASE_ARROW_UP, 3, 60),
        ("RIGHT", WindowEvent.PRESS_ARROW_RIGHT, WindowEvent.RELEASE_ARROW_RIGHT, 3, 60),
        ("DOWN", WindowEvent.PRESS_ARROW_DOWN, WindowEvent.RELEASE_ARROW_DOWN, 3, 60),
        ("LEFT", WindowEvent.PRESS_ARROW_LEFT, WindowEvent.RELEASE_ARROW_LEFT, 3, 60),
    ]
    
    try:
        for direction, key_event, release_event, presses, delay_frames in test_sequence:
            print(f"\nTesting {direction} direction with {delay_frames} frame delays:")
            
            for i in range(presses):
                print(f"  Press #{i+1}...")
                
                pyboy.send_input(key_event)
                
                for _ in range(delay_frames // 2):
                    pyboy.tick()
                
                key_pressed_dump = dump_memory(pyboy, f"{direction}_PRESSED", i)
                memory_dumps.append(key_pressed_dump)
                
                for _ in range(delay_frames // 2):
                    pyboy.tick()
                
                pyboy.send_input(release_event)
                
                for _ in range(delay_frames):
                    pyboy.tick()
                
                key_released_dump = dump_memory(pyboy, f"{direction}_RELEASED", i)
                memory_dumps.append(key_released_dump)
                
                print(f"    Position: {pyboy.memory[mem.LINK_X_POS]}, {pyboy.memory[mem.LINK_Y_POS]}")
                print(f"    Direction flags: {pyboy.memory[mem.LINK_DIRECTION_FLAGS]}")
            
            for _ in range(delay_frames * 2):
                pyboy.tick()
        
        print("\nDelayed movement tests completed!")
        
    except KeyboardInterrupt:
        print("\nTests interrupted by user.")
    finally:
        with open(output_file, 'w') as f:
            json.dump(memory_dumps, f, indent=2)
        print(f"Saved {len(memory_dumps)} memory dumps to {output_file}")
        
        pyboy.stop()
        print("Game closed.")

if __name__ == "__main__":
    run_delayed_memory_dump()
