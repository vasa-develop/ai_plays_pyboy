import numpy as np
import os
import sys
from unittest.mock import MagicMock, patch
from pyboy.utils import WindowEvent

def test_game_initialization():
    """Test the game initialization sequence to ensure it skips loading screens."""
    print("Testing game initialization sequence...")
    
    tick_count = 0
    start_game_called = False
    start_button_pressed = False
    start_button_released = False
    
    def mock_tick():
        nonlocal tick_count
        tick_count += 1
        return None
    
    def mock_start_game(timer_div=None):
        nonlocal start_game_called
        start_game_called = True
        print(f"[TEST] start_game called with timer_div={timer_div}")
        return None
    
    def mock_send_input(button):
        nonlocal start_button_pressed, start_button_released
        if button == WindowEvent.PRESS_BUTTON_START:
            start_button_pressed = True
            print("[TEST] START button pressed")
        elif button == WindowEvent.RELEASE_BUTTON_START:
            start_button_released = True
            print("[TEST] START button released")
        return None
    
    mock_pyboy = MagicMock()
    mock_tetris = MagicMock()
    
    mock_pyboy.tick.side_effect = mock_tick
    mock_pyboy.send_input.side_effect = mock_send_input
    mock_tetris.start_game.side_effect = mock_start_game
    mock_pyboy.game_wrapper = mock_tetris
    mock_pyboy.cartridge_title = "TETRIS"
    
    with patch('pyboy.PyBoy', return_value=mock_pyboy):
        from gym_wrapper.tetris_env import TetrisPyBoyEnv
        
        env = TetrisPyBoyEnv(rom_path="dummy_path.gb", render_mode="headless")
        
        env.reset()
        
        print(f"[TEST] Total tick count: {tick_count}")
        print(f"[TEST] start_game called: {start_game_called}")
        print(f"[TEST] START button pressed: {start_button_pressed}")
        print(f"[TEST] START button released: {start_button_released}")
        
        initialization_correct = (
            start_game_called and
            start_button_pressed and
            start_button_released and
            tick_count == 181  # 120 frames + 1 frame for button press + 60 more frames
        )
        
        print(f"[TEST] Initialization sequence correct: {'PASSED' if initialization_correct else 'FAILED'}")
        
        if not start_game_called:
            print("[TEST] FAILED: start_game was not called")
        if not start_button_pressed or not start_button_released:
            print("[TEST] FAILED: START button was not pressed or released")
        if tick_count != 181:
            print(f"[TEST] FAILED: Expected 181 ticks, got {tick_count}")

if __name__ == "__main__":
    test_game_initialization()
