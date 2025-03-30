from pyboy import PyBoy
from zelda_wrapper import ZeldaGameWrapper
import time

def test_zelda_wrapper():
    """Test the Zelda game wrapper implementation."""
    rom_path = "zelda.gbc"
    pyboy = PyBoy(rom_path, window="SDL2")
    pyboy.set_emulation_speed(1)
    
    zelda = ZeldaGameWrapper(pyboy)
    
    print("Starting game...")
    zelda.start_game()
    
    print("\nInitial game state:")
    print(f"Player position: {zelda._get_player_position()}")
    print(f"Player health: {zelda._get_health()}")
    print(f"Player max health: {zelda._get_max_health()}")
    print(f"Player direction: {zelda._get_player_direction()}")
    print(f"Enemy states: {zelda._get_enemy_states()}")
    print(f"Game progress: {zelda._get_game_progress()}")
    
    print("\nTesting movement...")
    directions = ['right', 'down', 'left', 'up']
    
    for direction in directions:
        print(f"\nMoving {direction}...")
        zelda.move_player(direction, steps=10)
        print(f"New position: {zelda._get_player_position()}")
        print(f"New direction: {zelda._get_player_direction()}")
        print(f"Enemy states: {zelda._get_enemy_states()}")
    
    print("\nTesting button presses...")
    buttons = ['a', 'b']
    
    for button in buttons:
        print(f"\nPressing {button}...")
        zelda.press_button(button)
        print(f"Player position: {zelda._get_player_position()}")
        print(f"Player health: {zelda._get_health()}")
    
    print("\nTest complete!")
    pyboy.stop()

if __name__ == "__main__":
    test_zelda_wrapper()
