"""
Simple script to print all game state values from the Zelda game wrapper.

This script runs the game and continuously prints the current game state
values using the updated memory addresses from the official RAM map.
"""
from pyboy import PyBoy
from zelda_game_wrapper import ZeldaGameWrapper
import time
import os

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def run_game_state_printer():
    """Run the game and continuously print game state values."""
    rom_path = "zelda.gbc"
    
    print("Starting Zelda: Link's Awakening Game State Printer")
    print("Using official memory addresses from RAM map")
    print("Press Ctrl+C to exit")
    
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
    
    print("\nStarting continuous game state printing...")
    print("Use keyboard to control Link and observe memory values changing")
    print("Press Ctrl+C to exit")
    
    try:
        while True:
            pyboy.tick()
            
            clear_screen()
            print_game_state(zelda)
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        pyboy.stop()
        print("Game closed.")

def print_game_state(zelda):
    """Print the current game state in a readable format."""
    position = zelda.get_player_position()
    direction = zelda.get_player_direction()
    direction_name = zelda.get_player_direction_name()
    animation_state = zelda.get_player_animation_state()
    health = zelda.get_health()
    max_health = zelda.get_max_health()
    rupees = zelda.get_rupees()
    items = zelda.get_items()
    game_state = zelda.get_game_state()
    enemies = zelda.get_enemy_states()
    progress_flags = zelda.get_game_progress()
    
    print("=== ZELDA: LINK'S AWAKENING GAME STATE ===")
    print(f"Position: ({position[0]}, {position[1]})")
    print(f"Direction: {direction_name} (value: {direction})")
    print(f"Animation State: {animation_state}")
    print(f"Health: {health}/{max_health}")
    print(f"Rupees: {rupees}")
    
    print("\nItems:")
    for item, value in items.items():
        print(f"  {item}: {value}")
    
    print("\nGame State:")
    for key, value in game_state.items():
        print(f"  {key}: {value}")
    
    print(f"\nEnemies: {len(enemies)}")
    for i, enemy in enumerate(enemies):
        if i < 3:  # Limit to first 3 enemies to avoid cluttering the screen
            print(f"  Enemy {i+1}: Type {enemy.get('type', 'N/A')}, " +
                  f"Position ({enemy.get('x', 'N/A')}, {enemy.get('y', 'N/A')})")
    
    print("\nProgress Flags (first 5):")
    for i in range(min(5, len(progress_flags))):
        print(f"  Flag {i}: {progress_flags[i]}")
    
    print("\nControls:")
    print("  Arrow keys: Move Link")
    print("  Z: A button")
    print("  X: B button")
    print("  Enter: Start button")
    print("  Backspace: Select button")
    print("  Ctrl+C: Exit")

if __name__ == "__main__":
    run_game_state_printer()
