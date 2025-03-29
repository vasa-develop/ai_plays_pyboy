import os
import logging
import numpy as np
from gym_wrapper import TetrisPyBoyEnv

def test_tetris_env():
    """Test the Tetris PyBoy Gym environment."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    rom_path = "tetris.gb"
    if not os.path.exists(rom_path):
        logger.error(f"ROM file not found: {rom_path}")
        logger.info("Please download a Tetris ROM and place it in the project directory")
        return
    
    logger.info("Creating Tetris environment...")
    env = TetrisPyBoyEnv(rom_path=rom_path)
    
    logger.info("Resetting environment...")
    obs, info = env.reset()
    
    logger.info(f"Observation shape: board={obs['board'].shape}, "
                f"current_piece={obs['current_piece'].shape}, "
                f"next_piece={obs['next_piece'].shape}")
    
    logger.info(f"Initial info: {info}")
    
    total_reward = 0
    n_steps = 100
    
    logger.info(f"Taking {n_steps} random actions...")
    for i in range(n_steps):
        action = env.action_space.sample()  # Random action
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        
        if i % 10 == 0:
            logger.info(f"Step {i}, Action: {action}, Reward: {reward:.2f}, "
                        f"Score: {info['score']}, Lines: {info['lines']}")
        
        if terminated or truncated:
            logger.info(f"Episode ended after {i+1} steps")
            break
    
    logger.info(f"Total reward: {total_reward:.2f}")
    logger.info(f"Final score: {info['score']}")
    logger.info(f"Final lines cleared: {info['lines']}")
    
    env.close()
    logger.info("Environment closed")

if __name__ == "__main__":
    test_tetris_env()
