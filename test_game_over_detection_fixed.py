import numpy as np
import os
import sys
from gym_wrapper.tetris_env import TetrisPyBoyEnv
from unittest.mock import MagicMock, patch

def create_mock_screen_buffer(white_pixels=0, black_pixels=5000):
    """Create a mock screen buffer with specified number of white pixels."""
    buffer = np.zeros((400, 320, 3), dtype=np.uint8)
    
    if white_pixels > 0:
        center_region = buffer[120:300, 80:240]
        pixels_to_set = min(white_pixels, center_region.shape[0] * center_region.shape[1])
        center_region.reshape(-1, 3)[:pixels_to_set] = 255
    
    if black_pixels > 0:
        center_region = buffer[120:300, 80:240]
        black_indices = np.where(np.all(center_region == 0, axis=2))
        pixels_to_set = min(black_pixels, len(black_indices[0]))
        for i in range(pixels_to_set):
            if i < len(black_indices[0]):
                center_region[black_indices[0][i], black_indices[1][i]] = 20  # Dark but not completely black
    
    return buffer

def test_game_over_detection():
    """Test the game over detection logic."""
    print("Testing game over detection logic...")
    
    env = TetrisPyBoyEnv(rom_path="dummy_path.gb", render_mode="headless")
    env.frame_count = 400  # Set frame count above the initialization threshold (300)
    
    env.tetris = MagicMock()
    env.tetris.game_over = False
    env.tetris.score = 100
    env.tetris.level = 1
    
    env._get_observation = MagicMock(return_value={
        'board': np.zeros((18, 10), dtype=np.int8)
    })
    
    with patch.object(env, 'pyboy') as mock_pyboy:
        mock_screen = MagicMock()
        mock_ndarray = MagicMock()
        mock_ndarray.return_value = create_mock_screen_buffer(white_pixels=0)
        mock_screen.ndarray = mock_ndarray
        mock_pyboy.screen = mock_screen
        
        is_game_over = env._is_game_over()
        print(f"Test 1 - No game over conditions: {'PASSED' if not is_game_over else 'FAILED'}")
    
    with patch.object(env, 'pyboy') as mock_pyboy:
        mock_screen = MagicMock()
        mock_ndarray = MagicMock()
        mock_ndarray.return_value = create_mock_screen_buffer(white_pixels=1000, black_pixels=8000)
        mock_screen.ndarray = mock_ndarray
        mock_pyboy.screen = mock_screen
        
        is_game_over = env._is_game_over()
        print(f"Test 2 - Game over screen detected: {'PASSED' if is_game_over else 'FAILED'}")
    
    env.tetris.game_over = True
    
    with patch.object(env, 'pyboy') as mock_pyboy:
        mock_screen = MagicMock()
        mock_ndarray = MagicMock()
        mock_ndarray.return_value = create_mock_screen_buffer(white_pixels=0)
        mock_screen.ndarray = mock_ndarray
        mock_pyboy.screen = mock_screen
        
        is_game_over = env._is_game_over()
        print(f"Test 3 - Explicit game over flag: {'PASSED' if is_game_over else 'FAILED'}")
    
    env.tetris.game_over = False
    
    board = np.zeros((18, 10), dtype=np.int8)
    board[0:2, :] = 1  # Fill top 2 rows
    
    env._get_observation = MagicMock(return_value={
        'board': board
    })
    
    with patch.object(env, 'pyboy') as mock_pyboy:
        mock_screen = MagicMock()
        mock_ndarray = MagicMock()
        mock_ndarray.return_value = create_mock_screen_buffer(white_pixels=0)
        mock_screen.ndarray = mock_ndarray
        mock_pyboy.screen = mock_screen
        
        is_game_over = env._is_game_over()
        print(f"Test 4 - Top rows filled: {'PASSED' if is_game_over else 'FAILED'}")

if __name__ == "__main__":
    test_game_over_detection()
