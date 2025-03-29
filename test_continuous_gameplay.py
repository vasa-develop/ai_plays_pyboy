import numpy as np
import os
import sys
from gym_wrapper.tetris_env import TetrisPyBoyEnv
from unittest.mock import MagicMock, patch

def test_continuous_gameplay_logic():
    """Test the continuous gameplay logic without requiring the ROM file."""
    print("Testing continuous gameplay logic...")
    
    env = TetrisPyBoyEnv(rom_path="dummy_path.gb", render_mode="headless", turn_based=False)
    
    env.frame_count = 200
    env.tetris = MagicMock()
    env.tetris.score = 100
    env.tetris.lines = 2
    env.prev_score = 100
    env.prev_lines = 2
    
    env._get_observation = MagicMock(return_value={
        'board': np.zeros((18, 10), dtype=np.int8),
        'current_piece': np.zeros(7, dtype=np.int8),
        'next_piece': np.zeros(7, dtype=np.int8)
    })
    
    env._is_game_over = MagicMock(return_value=False)
    
    env._is_piece_locked = MagicMock(return_value=False)
    
    with patch.object(env, 'pyboy') as mock_pyboy:
        frames_advanced = 0
        
        def mock_tick():
            nonlocal frames_advanced
            frames_advanced += 1
        
        mock_pyboy.tick = mock_tick
        mock_pyboy.send_input = MagicMock()
        
        action = 0
        observation, reward, terminated, truncated, info = env.step(action)
        
        print(f"Test 1 - Frames advanced: {frames_advanced}")
        print(f"Test 1 - Expected 5 frames in continuous mode: {'PASSED' if frames_advanced == 5 else 'FAILED'}")
    
    with patch.object(env, 'pyboy') as mock_pyboy:
        env.frame_count = 15  # Divisible by 15 to trigger piece lock check
        
        mock_pyboy.tick = MagicMock()
        mock_pyboy.send_input = MagicMock()
        
        env._is_piece_locked = MagicMock(return_value=True)
        
        action = 0
        observation, reward, terminated, truncated, info = env.step(action)
        
        print(f"Test 2 - Reward when piece is locked: {reward}")
        print(f"Test 2 - Reward includes placement bonus: {'PASSED' if reward > 0 else 'FAILED'}")
    
    with patch.object(env, 'pyboy') as mock_pyboy:
        env.frame_delay = 0.01
        
        mock_pyboy.tick = MagicMock()
        mock_pyboy.send_input = MagicMock()
        
        with patch('time.sleep') as mock_sleep:
            action = 0
            observation, reward, terminated, truncated, info = env.step(action)
            
            print(f"Test 3 - Sleep calls: {mock_sleep.call_count}")
            print(f"Test 3 - Frame delay applied: {'PASSED' if mock_sleep.call_count > 0 else 'FAILED'}")
    
    print("Continuous gameplay logic tests completed.")

if __name__ == "__main__":
    test_continuous_gameplay_logic()
