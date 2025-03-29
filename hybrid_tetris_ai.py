import os
import logging
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from gym_wrapper import TetrisPyBoyEnv
from state_preprocessor import TetrisStatePreprocessor
from custom_wrappers import TetrisFeatureWrapper, TetrisRewardWrapper, VecTetrisFeatureWrapper
from reward_function import TetrisRewardFunction, AdaptiveRewardFunction
from rl_agent import TetrisRLAgent, create_tetris_env

class TetrisHybridAI:
    """
    Hybrid AI for playing Tetris on PyBoy emulator.
    Combines game wrapper direct access with reinforcement learning.
    """
    
    def __init__(self, rom_path="tetris.gb", model_path=None, render_mode="human", algorithm="ppo"):
        """
        Initialize the Tetris Hybrid AI.
        
        Args:
            rom_path: Path to the Tetris ROM file
            model_path: Path to a pre-trained model (if available)
            render_mode: Whether to render the game visually
            algorithm: RL algorithm to use ('ppo', 'a2c', or 'dqn')
        """
        self.logger = logging.getLogger(__name__)
        self.rom_path = rom_path
        self.model_path = model_path
        self.render_mode = render_mode
        self.algorithm = algorithm
        self.env = None
        self.model = None
        self.state_preprocessor = TetrisStatePreprocessor()
        self.rl_agent = None
        
    def create_environment(self):
        """Create and initialize the Tetris environment."""
        if not os.path.exists(self.rom_path):
            self.logger.error(f"ROM file not found: {self.rom_path}")
            raise FileNotFoundError(f"ROM file not found: {self.rom_path}")
        
        self.env = create_tetris_env(self.rom_path, self.render_mode)
        
        self.logger.info("Tetris environment with feature extraction created successfully")
        
    def create_model(self):
        """Create or load a reinforcement learning model."""
        if self.env is None:
            self.create_environment()
        
        if self.rl_agent is None:
            self.rl_agent = TetrisRLAgent(
                env=self.env,
                algorithm=self.algorithm,
                model_path=self.model_path,
                log_dir="./tetris_logs"
            )
        
        self.model = self.rl_agent.create_model()
        
        return self.model
        
    def train(self, total_timesteps=100000, save_path="tetris_model"):
        """
        Train the reinforcement learning model.
        
        Args:
            total_timesteps: Number of timesteps to train for
            save_path: Path to save the trained model
        """
        if self.model is None:
            self.create_model()
        
        self.logger.info(f"Training model for {total_timesteps} timesteps")
        
        self.rl_agent.train(
            total_timesteps=total_timesteps,
            checkpoint_freq=10000,
            eval_freq=10000
        )
        
        self.rl_agent.save(save_path)
        self.logger.info(f"Model saved to {save_path}")
        
    def play(self, episodes=1):
        """
        Play Tetris using the trained model.
        
        Args:
            episodes: Number of episodes to play
        """
        if self.model is None:
            self.create_model()
        
        self.logger.info(f"Playing {episodes} episodes of Tetris")
        
        episode_rewards = self.rl_agent.play(episodes=episodes, deterministic=True)
        
        mean_reward = np.mean(episode_rewards) if episode_rewards else 0
        self.logger.info(f"Mean reward over {episodes} episodes: {mean_reward:.2f}")
        
        return episode_rewards
        
    def close(self):
        """Clean up resources."""
        if self.env:
            self.env.close()

def play_tetris_hybrid_ai(rom_path="tetris.gb", model_path=None, mode="play", timesteps=100000):
    """
    Run the Tetris Hybrid AI with the specified ROM.
    
    Args:
        rom_path: Path to the Tetris ROM file
        model_path: Path to a pre-trained model (if available)
        mode: 'train' to train the model, 'play' to play using the model
        timesteps: Number of timesteps to train for (if mode is 'train')
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting Tetris Hybrid AI in {mode} mode")
    
    if not os.path.exists(rom_path):
        logger.error(f"ROM file not found: {rom_path}")
        logger.info("Please download a Tetris ROM and place it in the project directory")
        return
    
    try:
        ai = TetrisHybridAI(rom_path=rom_path, model_path=model_path)
        
        if mode == "train":
            ai.train(total_timesteps=timesteps)
        else:
            ai.play(episodes=5)
        
        ai.close()
        
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    play_tetris_hybrid_ai()
