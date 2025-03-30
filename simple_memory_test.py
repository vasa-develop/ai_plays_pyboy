"""
Simple test script for the updated Zelda game wrapper with corrected memory addresses.

This script tests the updated game wrapper that uses the correct memory addresses
from the official RAM map for Zelda: Link's Awakening without requiring manual navigation.
"""
from pyboy import PyBoy
import time

def test_memory_addresses():
    """Test the memory addresses from the RAM map."""
    rom_path = "zelda.gbc"
    
    print("Starting Zelda: Link's Awakening Memory Address Test")
    
    pyboy = PyBoy(rom_path, window="SDL2", scale=3)
    pyboy.set_emulation_speed(1)  # Normal speed
    
    for _ in range(100):
        pyboy.tick()
    
    from pyboy.utils import WindowEvent
    pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
    pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
    
    for _ in range(50):
        pyboy.tick()
    
    print("\nComparing memory addresses:")
    
    old_x_pos = 0xC000
    old_y_pos = 0xC001
    held_item_a = 0xDB00
    held_item_b = 0xDB01
    
    print("\nPlayer Position vs Held Items:")
    print(f"  Old X position (0x{old_x_pos:04X}): {pyboy.memory[old_x_pos]}")
    print(f"  Old Y position (0x{old_y_pos:04X}): {pyboy.memory[old_y_pos]}")
    print(f"  Held Item A (0x{held_item_a:04X}): {pyboy.memory[held_item_a]}")
    print(f"  Held Item B (0x{held_item_b:04X}): {pyboy.memory[held_item_b]}")
    
    old_direction = 0xC00B
    
    print("\nPlayer Direction:")
    print(f"  Old direction (0x{old_direction:04X}): {pyboy.memory[old_direction]}")
    
    health_addr = 0xDB5A
    max_health_addr = 0xDB5B
    
    print("\nHealth:")
    print(f"  Health (0x{health_addr:04X}): {pyboy.memory[health_addr]}")
    print(f"  Max Health (0x{max_health_addr:04X}): {pyboy.memory[max_health_addr]}")
    
    inventory_start = 0xDB02
    inventory_end = 0xDB0B
    
    print("\nInventory (0xDB02-0xDB0B):")
    for addr in range(inventory_start, inventory_end + 1):
        print(f"  0x{addr:04X}: {pyboy.memory[addr]}")
    
    dest_x = 0xD404
    dest_y = 0xD405
    
    print("\nDestination Coordinates:")
    print(f"  Destination X (0x{dest_x:04X}): {pyboy.memory[dest_x]}")
    print(f"  Destination Y (0x{dest_y:04X}): {pyboy.memory[dest_y]}")
    
    dungeon_pos = 0xDBAE
    
    print("\nDungeon Position:")
    print(f"  Position on 8x8 grid (0x{dungeon_pos:04X}): {pyboy.memory[dungeon_pos]}")
    
    game_state = 0xDBE0
    game_substate = 0xDBE1
    
    print("\nGame State:")
    print(f"  Game state (0x{game_state:04X}): {pyboy.memory[game_state]}")
    print(f"  Game substate (0x{game_substate:04X}): {pyboy.memory[game_substate]}")
    
    print("\nMemory Dumps of Key Regions:")
    
    print("\nPlayer Data Region (0xC000-0xC010):")
    for addr in range(0xC000, 0xC010):
        print(f"  0x{addr:04X}: {pyboy.memory[addr]}")
    
    try:
        input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        pass
    finally:
        pyboy.stop()
        print("Game closed.")

if __name__ == "__main__":
    test_memory_addresses()
