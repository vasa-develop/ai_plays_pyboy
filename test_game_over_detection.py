import numpy as np
import os
import sys
from gym_wrapper.tetris_env import TetrisPyBoyEnv
from unittest.mock import MagicMock, patch

def create_mock_screen_buffer(has_game_over=False):
    """Create a mock screen buffer with or without a game over pattern."""
    screen = np.zeros((256, 320, 3), dtype=np.uint8)
    
    if has_game_over:
        center_y_start, center_y_end = 120, 300
        center_x_start, center_x_end = 80, 240
        
        screen[center_y_start:center_y_end, center_x_start:center_x_end] = 255
    
    return screen

def test_game_over_detection():
    """Test the game over detection logic with mock data."""
    print("Testing game over detection logic...")
    
    env = TetrisPyBoyEnv(rom_path="dummy_path.gb", render_mode="headless")
    
    env.frame_count = 200  # Past the initial 120 frames check
    env.tetris = MagicMock()
    env.tetris.game_over = False
    env.tetris.score = 100
    env.tetris.level = 1
    
    env._get_observation = MagicMock(return_value={'board': np.zeros((18, 10), dtype=np.int8)})
    
    with patch.object(env, 'pyboy') as mock_pyboy:
        mock_pyboy.screen_ndarray.return_value = create_mock_screen_buffer(has_game_over=False)
        result = env._is_game_over()
        print(f"Test 1 - No game over conditions: {'PASSED' if not result else 'FAILED'}")
    
    with patch.object(env, 'pyboy') as mock_pyboy:
        mock_pyboy.screen_ndarray.return_value = create_mock_screen_buffer(has_game_over=True)
        result = env._is_game_over()
        print(f"Test 2 - Game over screen detected: {'PASSED' if result else 'FAILED'}")
    
    with patch.object(env, 'pyboy') as mock_pyboy:
        mock_pyboy.screen_ndarray.return_value = create_mock_screen_buffer(has_game_over=False)
        env.tetris.game_over = True
        result = env._is_game_over()
        print(f"Test 3 - Explicit game over flag: {'PASSED' if result else 'FAILED'}")
    
    with patch.object(env, 'pyboy') as mock_pyboy:
        mock_pyboy.screen_ndarray.return_value = create_mock_screen_buffer(has_game_over=False)
        env.tetris.game_over = False
        board = np.zeros((18, 10), dtype=np.int8)
        board[0:2, :] = 1  # Fill top 2 rows
        env._get_observation = MagicMock(return_value={'board': board})
        result = env._is_game_over()
        print(f"Test 4 - Top rows filled: {'PASSED' if result else 'FAILED'}")

if __name__ == "__main__":
    test_game_over_detection()
