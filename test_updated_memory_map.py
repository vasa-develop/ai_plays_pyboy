"""
Test script for the updated Zelda: Link's Awakening memory map.

This script tests the updated memory addresses and direction mapping
based on the analysis of test results.
"""
from pyboy import PyBoy
from zelda_game_wrapper import ZeldaGameWrapper
import memory_map_zelda as mem
import time

def test_memory_map():
    """Test the updated memory map with a focus on direction and position."""
    rom_path = "zelda.gbc"
    
    print("Starting Zelda: Link's Awakening Memory Map Test")
    
    pyboy = PyBoy(rom_path, window="SDL2", scale=3)
    pyboy.set_emulation_speed(1)  # Normal speed
    
    zelda = ZeldaGameWrapper(pyboy)
    
    print("\nSkipping title screen...")
    zelda.start_game()
    
    print("\nWaiting 30 seconds for manual navigation through loading screens...")
    print("Please navigate through any loading screens during this time.")
    start_time = time.time()
    while time.time() - start_time < 30:
        pyboy.tick()
        elapsed = int(time.time() - start_time)
        if elapsed % 5 == 0 and elapsed > 0:
            print(f"  {30 - elapsed} seconds remaining...")
    
    print("\nStarting memory map tests...")
    
    print("\nTesting position memory addresses:")
    position = zelda.get_player_position()
    print(f"  Player position: {position}")
    print(f"  Raw memory values:")
    print(f"    LINK_X_POS (0x{mem.LINK_X_POS:04X}): {pyboy.memory[mem.LINK_X_POS]}")
    print(f"    LINK_Y_POS (0x{mem.LINK_Y_POS:04X}): {pyboy.memory[mem.LINK_Y_POS]}")
    print(f"    LINK_SPRITE_X (0x{mem.LINK_SPRITE_X:04X}): {pyboy.memory[mem.LINK_SPRITE_X]}")
    print(f"    LINK_SPRITE_Y (0x{mem.LINK_SPRITE_Y:04X}): {pyboy.memory[mem.LINK_SPRITE_Y]}")
    
    print("\nTesting direction memory addresses:")
    direction = zelda.get_player_direction()
    print(f"  Player direction: {direction}")
    print(f"  Raw memory values:")
    print(f"    LINK_DIRECTION_FLAGS (0x{mem.LINK_DIRECTION_FLAGS:04X}): {pyboy.memory[mem.LINK_DIRECTION_FLAGS]}")
    print(f"    LINK_DIRECTION_FLAGS2 (0x{mem.LINK_DIRECTION_FLAGS2:04X}): {pyboy.memory[mem.LINK_DIRECTION_FLAGS2]}")
    
    print("\nTesting direction changes:")
    directions = ['up', 'right', 'down', 'left']
    
    for direction in directions:
        print(f"\n  Pressing {direction.upper()}:")
        
        initial_dir_flags = pyboy.memory[mem.LINK_DIRECTION_FLAGS]
        initial_dir_flags2 = pyboy.memory[mem.LINK_DIRECTION_FLAGS2]
        initial_dir = zelda.get_player_direction()
        
        print(f"    Initial direction: {initial_dir}")
        print(f"    Initial DIRECTION_FLAGS: {initial_dir_flags}")
        print(f"    Initial DIRECTION_FLAGS2: {initial_dir_flags2}")
        
        zelda.move_player(direction, steps=1)
        
        new_dir_flags = pyboy.memory[mem.LINK_DIRECTION_FLAGS]
        new_dir_flags2 = pyboy.memory[mem.LINK_DIRECTION_FLAGS2]
        new_dir = zelda.get_player_direction()
        
        print(f"    New direction: {new_dir}")
        print(f"    New DIRECTION_FLAGS: {new_dir_flags}")
        print(f"    New DIRECTION_FLAGS2: {new_dir_flags2}")
        
        for _ in range(30):
            pyboy.tick()
    
    print("\nMemory map tests completed!")
    
    try:
        input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        pass
    finally:
        pyboy.stop()
        print("Game closed.")

if __name__ == "__main__":
    test_memory_map()
