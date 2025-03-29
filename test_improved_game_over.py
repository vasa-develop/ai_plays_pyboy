import os
import sys
import numpy as np
from unittest.mock import MagicMock, patch
from pyboy.utils import WindowEvent

def test_improved_game_over_detection():
    """Test the improved game over detection logic."""
    print("Testing improved game over detection...")
    
    with patch('pyboy.PyBoy') as mock_pyboy_class:
        from gym_wrapper.tetris_env import TetrisPyBoyEnv
        
        mock_pyboy = MagicMock()
        mock_pyboy_class.return_value = mock_pyboy
        
        mock_tetris = MagicMock()
        mock_tetris.game_over = False
        mock_pyboy.game_wrapper = mock_tetris
        
        mock_screen = MagicMock()
        mock_ndarray = MagicMock()
        mock_screen.ndarray = mock_ndarray
        mock_pyboy.screen = mock_screen
        
        env = TetrisPyBoyEnv(rom_path="dummy_path.gb", render_mode="headless")
        env.frame_count = 500  # Set frame count above initialization threshold
        
        mock_tetris.game_over = False
        mock_ndarray.return_value = np.zeros((400, 320, 3), dtype=np.uint8)
        env._get_observation = MagicMock(return_value={'board': np.zeros((18, 10), dtype=np.int8)})
        
        is_game_over = env._is_game_over()
        print(f"Test 1 - No game over conditions: {'PASSED' if not is_game_over else 'FAILED'}")
        
        mock_tetris.game_over = True
        env._get_observation = MagicMock(return_value={'board': np.zeros((18, 10), dtype=np.int8)})
        
        is_game_over = env._is_game_over()
        print(f"Test 2 - Game over via built-in attribute: {'PASSED' if is_game_over else 'FAILED'}")
        
        mock_tetris.game_over = False
        board = np.zeros((18, 10), dtype=np.int8)
        board[0:2, :] = 1  # Fill top 2 rows
        env._get_observation = MagicMock(return_value={'board': board})
        
        is_game_over = env._is_game_over()
        print(f"Test 3 - Game over via top rows filled: {'PASSED' if is_game_over else 'FAILED'}")
        
        mock_tetris.game_over = False
        env._get_observation = MagicMock(return_value={'board': np.zeros((18, 10), dtype=np.int8)})
        
        screen_buffer = np.zeros((400, 320, 3), dtype=np.uint8)
        center_region = screen_buffer[120:300, 80:240]
        center_region[:] = 20  # Dark but not completely black
        
        for i in range(140, 180):
            for j in range(100, 200):
                screen_buffer[i, j] = 255
        
        mock_ndarray.return_value = screen_buffer
        
        env.frame_count = 1200  # Ensure we're past the screen detection threshold
        
        is_game_over = env._is_game_over()
        print(f"Test 4 - Game over via screen analysis: {'PASSED' if is_game_over else 'FAILED'}")
        
        mock_tetris.game_over = False
        env._get_observation = MagicMock(return_value={'board': np.zeros((18, 10), dtype=np.int8)})
        
        screen_buffer = np.zeros((400, 320, 3), dtype=np.uint8)
        screen_buffer[50:350, 50:270] = 255  # Large white area
        mock_ndarray.return_value = screen_buffer
        
        is_game_over = env._is_game_over()
        print(f"Test 5 - Loading screen (should not trigger): {'PASSED' if not is_game_over else 'FAILED'}")
        
        mock_tetris.game_over = False
        env.frame_count = 100  # Below initialization threshold
        
        is_game_over = env._is_game_over()
        print(f"Test 6 - Early frames (should not trigger): {'PASSED' if not is_game_over else 'FAILED'}")
        
        print("Improved game over detection tests completed.")

if __name__ == "__main__":
    test_improved_game_over_detection()
