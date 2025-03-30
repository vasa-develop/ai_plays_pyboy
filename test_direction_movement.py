"""
Test script for Zelda: Link's Awakening direction and movement mechanics.

This script tests the updated game wrapper's ability to handle Link's direction changes
and movement based on the memory dump analysis.
"""
from pyboy import PyBoy
from zelda_game_wrapper import ZeldaGameWrapper
import memory_map_zelda as mem
import time

def test_direction_movement():
    """Test Link's direction changes and movement mechanics."""
    rom_path = "zelda.gbc"
    
    print("Starting Zelda: Link's Awakening Direction/Movement Test")
    
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
    
    print("\nStarting direction and movement tests...")
    
    directions = ['up', 'right', 'down', 'left']
    
    try:
        for direction in directions:
            print(f"\nTesting {direction.upper()} direction:")
            
            initial_pos = zelda.get_player_position()
            initial_dir = zelda.get_player_direction()
            
            print(f"  Initial position: {initial_pos}")
            print(f"  Initial direction: {initial_dir}")
            
            print(f"  Pressing {direction} to change direction...")
            zelda.move_player(direction, steps=1)
            
            new_dir = zelda.get_player_direction()
            new_pos = zelda.get_player_position()
            
            print(f"  New direction: {new_dir}")
            print(f"  New position: {new_pos}")
            
            print(f"  Pressing {direction} again to move...")
            zelda.move_player(direction, steps=1)
            
            final_pos = zelda.get_player_position()
            print(f"  Final position: {final_pos}")
            
            for _ in range(30):
                pyboy.tick()
        
        print("\nDirection and movement tests completed!")
        
    except KeyboardInterrupt:
        print("\nTests interrupted by user.")
    finally:
        pyboy.stop()
        print("Game closed.")

if __name__ == "__main__":
    test_direction_movement()
