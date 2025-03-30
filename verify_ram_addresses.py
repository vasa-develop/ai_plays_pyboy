"""
Simple verification script for Zelda: Link's Awakening RAM addresses.

This script compares the old reverse-engineered memory addresses with
the new official RAM map addresses to verify which ones are correct.
"""
from pyboy import PyBoy
from pyboy.utils import WindowEvent
import time

def verify_ram_addresses():
    """Compare old and new memory addresses to verify which are correct."""
    rom_path = "zelda.gbc"
    
    print("Starting Zelda: Link's Awakening RAM Address Verification")
    
    pyboy = PyBoy(rom_path, window="SDL2", scale=3)
    pyboy.set_emulation_speed(1)  # Normal speed
    
    for _ in range(100):
        pyboy.tick()
    pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
    pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
    
    for _ in range(50):
        pyboy.tick()
    
    print("\nComparing old and new memory addresses:")
    
    old_x_pos = 0xC000
    old_y_pos = 0xC001
    new_x_pos = 0xDB00
    new_y_pos = 0xDB01
    
    print("\nPlayer Position:")
    print(f"  Old X position (0x{old_x_pos:04X}): {pyboy.memory[old_x_pos]}")
    print(f"  Old Y position (0x{old_y_pos:04X}): {pyboy.memory[old_y_pos]}")
    print(f"  New X position (0x{new_x_pos:04X}): {pyboy.memory[new_x_pos]}")
    print(f"  New Y position (0x{new_y_pos:04X}): {pyboy.memory[new_y_pos]}")
    
    old_direction = 0xC00B
    new_direction = 0xDB04
    
    print("\nPlayer Direction:")
    print(f"  Old direction (0x{old_direction:04X}): {pyboy.memory[old_direction]}")
    print(f"  New direction (0x{new_direction:04X}): {pyboy.memory[new_direction]}")
    
    old_health = 0xC100
    new_health = 0xDB5A
    
    print("\nPlayer Health:")
    print(f"  Old health (0x{old_health:04X}): {pyboy.memory[old_health]}")
    print(f"  New health (0x{new_health:04X}): {pyboy.memory[new_health]}")
    
    print("\nInventory Items (New Addresses):")
    print(f"  Sword level (0xDB4A): {pyboy.memory[0xDB4A]}")
    print(f"  Shield level (0xDB49): {pyboy.memory[0xDB49]}")
    print(f"  Bombs (0xDB4E): {pyboy.memory[0xDB4E]}")
    print(f"  Arrows (0xDB4D): {pyboy.memory[0xDB4D]}")
    print(f"  Magic powder (0xDB4F): {pyboy.memory[0xDB4F]}")
    
    print("\nGame State (New Addresses):")
    print(f"  Game state (0xDBE0): {pyboy.memory[0xDBE0]}")
    print(f"  Game substate (0xDBE1): {pyboy.memory[0xDBE1]}")
    print(f"  Room ID (0xD800): {pyboy.memory[0xD800]}")
    print(f"  Dungeon ID (0xDBB8): {pyboy.memory[0xDBB8]}")
    
    print("\nMemory Dumps of Key Regions:")
    
    print("\nPlayer Data Region (0xDB00-0xDB10):")
    for addr in range(0xDB00, 0xDB10):
        print(f"  0x{addr:04X}: {pyboy.memory[addr]}")
    
    print("\nHealth Data Region (0xDB5A-0xDB60):")
    for addr in range(0xDB5A, 0xDB60):
        print(f"  0x{addr:04X}: {pyboy.memory[addr]}")
    
    print("\nInventory Region (0xDB40-0xDB50):")
    for addr in range(0xDB40, 0xDB50):
        print(f"  0x{addr:04X}: {pyboy.memory[addr]}")
    
    try:
        input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        pass
    finally:
        pyboy.stop()
        print("Game closed.")

if __name__ == "__main__":
    verify_ram_addresses()
