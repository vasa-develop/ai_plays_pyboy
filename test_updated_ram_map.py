"""
Test script for the updated Zelda: Link's Awakening RAM map.

This script tests the updated memory addresses from the official RAM map:
https://datacrystal.tcrf.net/wiki/The_Legend_of_Zelda:_Link%27s_Awakening_(Game_Boy)/RAM_map
"""
from pyboy import PyBoy
from zelda_game_wrapper import ZeldaGameWrapper
import memory_map_zelda as mem
import time
import json

def test_ram_map():
    """Test the updated RAM map with official memory addresses."""
    rom_path = "zelda.gbc"
    
    print("Starting Zelda: Link's Awakening RAM Map Test")
    print("Using official memory addresses from RAM map")
    
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
    
    print("\nStarting RAM map tests...")
    
    initial_state = capture_game_state(pyboy, zelda)
    print_game_state(initial_state)
    
    print("\nTesting button presses...")
    buttons = ['up', 'right', 'down', 'left', 'a', 'b', 'start', 'select']
    
    for button in buttons:
        print(f"\n  Pressing {button.upper()}...")
        if button in ['up', 'right', 'down', 'left']:
            zelda.move_player(button, steps=1, delay_frames=30)
        else:
            zelda.press_button(button, hold_frames=30)
        
        button_state = capture_game_state(pyboy, zelda)
        print_state_changes(initial_state, button_state)
        
        for _ in range(30):
            pyboy.tick()
    
    print("\nSaving complete game state to file...")
    full_state = capture_game_state(pyboy, zelda, include_memory_dump=True)
    
    with open("zelda_ram_map_test.json", "w") as f:
        json.dump(full_state, f, indent=2)
    
    print("\nRAM map tests completed!")
    print("Data saved to zelda_ram_map_test.json")
    
    try:
        input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        pass
    finally:
        pyboy.stop()
        print("Game closed.")

def capture_game_state(pyboy, zelda, include_memory_dump=False):
    """Capture the current game state using the wrapper."""
    state = {
        "timestamp": time.time(),
        "position": zelda.get_player_position(),
        "direction": {
            "value": zelda.get_player_direction(),
            "name": zelda.get_player_direction_name()
        },
        "animation_state": zelda.get_player_animation_state(),
        "health": {
            "current": zelda.get_health(),
            "max": zelda.get_max_health()
        },
        "items": zelda.get_items(),
        "rupees": zelda.get_rupees(),
        "game_state": zelda.get_game_state(),
        "enemies": zelda.get_enemy_states(),
        "progress_flags": zelda.get_game_progress()
    }
    
    if include_memory_dump:
        memory_dump = {
            "player_data": {f"0x{addr:04X}": pyboy.memory[addr] for addr in range(0xDB00, 0xDB10)},
            "health_data": {f"0x{addr:04X}": pyboy.memory[addr] for addr in range(0xDB5A, 0xDB60)},
            "inventory": {f"0x{addr:04X}": pyboy.memory[addr] for addr in range(0xDB40, 0xDB50)},
            "game_state": {f"0x{addr:04X}": pyboy.memory[addr] for addr in range(0xDBE0, 0xDBF0)},
            "progress_flags": {f"0x{addr:04X}": pyboy.memory[addr] for addr in range(0xDBA0, 0xDBB0)}
        }
        state["memory_dump"] = memory_dump
    
    return state

def print_game_state(state):
    """Print the game state in a readable format."""
    print("\nCurrent Game State:")
    print(f"  Position: ({state['position'][0]}, {state['position'][1]})")
    print(f"  Direction: {state['direction']['name']} (value: {state['direction']['value']})")
    print(f"  Animation State: {state['animation_state']}")
    print(f"  Health: {state['health']['current']}/{state['health']['max']}")
    print(f"  Rupees: {state['rupees']}")
    
    print("\n  Items:")
    for item, value in state['items'].items():
        print(f"    {item}: {value}")
    
    print("\n  Game State:")
    for key, value in state['game_state'].items():
        print(f"    {key}: {value}")
    
    print(f"\n  Enemies: {len(state['enemies'])}")
    for i, enemy in enumerate(state['enemies']):
        print(f"    Enemy {i+1}: Type {enemy['type']}, Position ({enemy['x']}, {enemy['y']})")
    
    print("\n  Progress Flags (first 5):")
    for i in range(min(5, len(state['progress_flags']))):
        print(f"    Flag {i}: {state['progress_flags'][i]}")

def print_state_changes(old_state, new_state):
    """Print changes between two game states."""
    print("  State changes:")
    
    if old_state['position'] != new_state['position']:
        print(f"    Position: {old_state['position']} -> {new_state['position']}")
    
    if old_state['direction']['value'] != new_state['direction']['value']:
        print(f"    Direction: {old_state['direction']['name']} -> {new_state['direction']['name']}")
    
    if old_state['animation_state'] != new_state['animation_state']:
        print(f"    Animation: {old_state['animation_state']} -> {new_state['animation_state']}")
    
    if old_state['health']['current'] != new_state['health']['current']:
        print(f"    Health: {old_state['health']['current']} -> {new_state['health']['current']}")
    
    if old_state['rupees'] != new_state['rupees']:
        print(f"    Rupees: {old_state['rupees']} -> {new_state['rupees']}")
    
    for item in old_state['items']:
        if old_state['items'][item] != new_state['items'][item]:
            print(f"    {item}: {old_state['items'][item]} -> {new_state['items'][item]}")
    
    for key in old_state['game_state']:
        if old_state['game_state'][key] != new_state['game_state'][key]:
            print(f"    {key}: {old_state['game_state'][key]} -> {new_state['game_state'][key]}")

if __name__ == "__main__":
    test_ram_map()
