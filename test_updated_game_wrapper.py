"""
Test script for the updated Zelda game wrapper with corrected memory addresses.

This script tests the updated game wrapper that uses the correct memory addresses
from the official RAM map for Zelda: Link's Awakening.
"""
from pyboy import PyBoy
from zelda_game_wrapper import ZeldaGameWrapper
import time

def test_game_wrapper():
    """Test the updated game wrapper with corrected memory addresses."""
    rom_path = "zelda.gbc"
    
    print("Starting Zelda: Link's Awakening Game Wrapper Test")
    print("Using corrected memory addresses from RAM map")
    
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
    
    print("\nTesting game wrapper methods...")
    
    print("\nPosition Information:")
    print(f"  Player position (old addresses): {zelda.get_player_position()}")
    print(f"  Destination position: {zelda.get_destination_position()}")
    print(f"  Dungeon position: {zelda.get_dungeon_position()}")
    
    print("\nDirection Information:")
    print(f"  Player direction: {zelda.get_player_direction()} ({zelda.get_player_direction_name()})")
    
    print("\nHealth Information:")
    print(f"  Current health: {zelda.get_health()}")
    print(f"  Maximum health: {zelda.get_max_health()}")
    
    print("\nHeld Items:")
    held_items = zelda.get_held_items()
    print(f"  Item A: {held_items['item_a_name']} (ID: {held_items['item_a']})")
    print(f"  Item B: {held_items['item_b_name']} (ID: {held_items['item_b']})")
    
    print("\nInventory Items:")
    items = zelda.get_items()
    for item, value in items.items():
        print(f"  {item}: {value}")
    
    print("\nInventory Slots:")
    inventory = zelda.get_inventory()
    for i, item_id in enumerate(inventory):
        print(f"  Slot {i+1}: {item_id}")
    
    print("\nMax Capacities:")
    capacities = zelda.get_max_capacities()
    for item, value in capacities.items():
        print(f"  {item}: {value}")
    
    print("\nGame State:")
    game_state = zelda.get_game_state()
    for key, value in game_state.items():
        print(f"  {key}: {value}")
    
    print("\nGame Progress Flags (first 5):")
    progress_flags = zelda.get_game_progress()
    for i in range(min(5, len(progress_flags))):
        print(f"  Flag {i}: {progress_flags[i]}")
    
    print("\nRupees:")
    print(f"  Current rupees: {zelda.get_rupees()}")
    
    print("\nString Representation:")
    print(zelda)
    
    print("\nTesting movement methods...")
    print("  Moving player up...")
    initial_pos = zelda.get_player_position()
    initial_dir = zelda.get_player_direction()
    
    zelda.move_player('up', steps=1, delay_frames=30)
    
    new_pos = zelda.get_player_position()
    new_dir = zelda.get_player_direction()
    
    print(f"  Initial position: {initial_pos}, direction: {initial_dir}")
    print(f"  New position: {new_pos}, direction: {new_dir}")
    
    print("\nTesting button press methods...")
    print("  Pressing A button...")
    zelda.press_button('a', hold_frames=30)
    
    print("\nComparing old and new memory addresses:")
    
    old_x_pos = 0xC000
    old_y_pos = 0xC001
    new_x_pos = 0xDB00
    new_y_pos = 0xDB01
    
    print("\nPlayer Position vs Held Items:")
    print(f"  Old X position (0x{old_x_pos:04X}): {pyboy.memory[old_x_pos]}")
    print(f"  Old Y position (0x{old_y_pos:04X}): {pyboy.memory[old_y_pos]}")
    print(f"  Held Item A (0x{new_x_pos:04X}): {pyboy.memory[new_x_pos]}")
    print(f"  Held Item B (0x{new_y_pos:04X}): {pyboy.memory[new_y_pos]}")
    
    old_direction = 0xC00B
    
    print("\nPlayer Direction:")
    print(f"  Old direction (0x{old_direction:04X}): {pyboy.memory[old_direction]}")
    
    health_addr = 0xDB5A
    max_health_addr = 0xDB5B
    
    print("\nHealth:")
    print(f"  Health (0x{health_addr:04X}): {pyboy.memory[health_addr]}")
    print(f"  Max Health (0x{max_health_addr:04X}): {pyboy.memory[max_health_addr]}")
    
    try:
        input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        pass
    finally:
        pyboy.stop()
        print("Game closed.")

if __name__ == "__main__":
    test_game_wrapper()
