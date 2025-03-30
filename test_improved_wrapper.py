"""
Test script for the improved Zelda: Link's Awakening game wrapper.

This script tests the enhanced game wrapper with:
1. Better direction detection
2. Delays between key presses
3. Direction name reporting
"""
from pyboy import PyBoy
from zelda_game_wrapper import ZeldaGameWrapper
import memory_map_zelda as mem
import time

def test_improved_wrapper():
    """Test the improved game wrapper features."""
    rom_path = "zelda.gbc"
    
    print("Starting Zelda: Link's Awakening Improved Wrapper Test")
    
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
    
    print("\nStarting improved wrapper tests...")
    
    print("\nTesting direction tracking:")
    directions = ['up', 'right', 'down', 'left']
    
    for direction in directions:
        print(f"\n  Testing {direction.upper()} direction:")
        
        initial_pos = zelda.get_player_position()
        initial_dir = zelda.get_player_direction()
        initial_dir_name = zelda.get_player_direction_name()
        
        print(f"    Initial position: {initial_pos}")
        print(f"    Initial direction: {initial_dir} ({initial_dir_name})")
        
        print(f"    Pressing {direction} to change direction...")
        zelda.move_player(direction, steps=1, delay_frames=20)
        
        new_dir = zelda.get_player_direction()
        new_dir_name = zelda.get_player_direction_name()
        new_pos = zelda.get_player_position()
        
        print(f"    New direction: {new_dir} ({new_dir_name})")
        print(f"    New position: {new_pos}")
        
        print(f"    Pressing {direction} again to move...")
        zelda.move_player(direction, steps=1, delay_frames=20)
        
        final_pos = zelda.get_player_position()
        print(f"    Final position: {final_pos}")
        
        if final_pos != initial_pos:
            print(f"    Position changed! Movement successful.")
        else:
            print(f"    Position unchanged. Movement may be restricted.")
        
        for _ in range(30):
            pyboy.tick()
    
    print("\nTesting multiple consecutive moves:")
    
    for direction in directions:
        print(f"\n  Moving {direction.upper()} three times with delays:")
        
        initial_pos = zelda.get_player_position()
        print(f"    Initial position: {initial_pos}")
        
        zelda.move_player(direction, steps=3, delay_frames=30)
        
        final_pos = zelda.get_player_position()
        print(f"    Final position: {final_pos}")
        
        if final_pos != initial_pos:
            print(f"    Position changed! Movement successful.")
            print(f"    Change: ({final_pos[0] - initial_pos[0]}, {final_pos[1] - initial_pos[1]})")
        else:
            print(f"    Position unchanged. Movement may be restricted.")
        
        for _ in range(60):
            pyboy.tick()
    
    print("\nImproved wrapper tests completed!")
    
    try:
        input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        pass
    finally:
        pyboy.stop()
        print("Game closed.")

if __name__ == "__main__":
    test_improved_wrapper()
