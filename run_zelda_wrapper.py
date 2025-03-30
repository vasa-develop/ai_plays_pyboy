"""
Simple test script to run Zelda: Link's Awakening and continuously print game state values.
This allows for manual verification of the memory addresses and wrapper functionality.
"""
from pyboy import PyBoy
from pyboy.utils import WindowEvent
from zelda_game_wrapper import ZeldaGameWrapper
import time

def run_zelda_wrapper():
    """Run Zelda with the game wrapper and continuously print state values."""
    rom_path = "zelda.gbc"
    
    print("Starting Zelda: Link's Awakening...")
    print("Press Ctrl+C to exit")
    
    pyboy = PyBoy(rom_path, window="SDL2", scale=3)
    pyboy.set_emulation_speed(1)  # Normal speed
    
    zelda = ZeldaGameWrapper(pyboy)
    
    print("\nSkipping title screen...")
    zelda.start_game()
    
    print("\nGame started! Use arrow keys to move Link and verify memory values.")
    print("Press B for sword, A for action/interaction.")
    
    try:
        while True:
            pyboy.tick()
            
            if pyboy.frame_count % 30 == 0:
                print("\n" + "="*50)
                print(f"Frame: {pyboy.frame_count}")
                print(f"Health: {zelda.get_health()}/{zelda.get_max_health()}")
                print(f"Position: {zelda.get_player_position()}")
                print(f"Direction: {zelda.get_player_direction()}")
                
                enemies = zelda.get_enemy_states()
                print(f"Enemies on screen: {len(enemies)}")
                for i, enemy in enumerate(enemies):
                    print(f"  Enemy {i+1}: Type={enemy['type']}, Pos=({enemy['x']},{enemy['y']}), State={enemy['state']}")
                
                print("="*50)
            
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        pyboy.stop()
        print("Game closed.")

if __name__ == "__main__":
    run_zelda_wrapper()
