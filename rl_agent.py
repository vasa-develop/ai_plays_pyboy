import os
import logging
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from stable_baselines3 import PPO, A2C, DQN
from stable_baselines3.common.callbacks import BaseCallback, CheckpointCallback
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, VecMonitor
from gym_wrapper import TetrisPyBoyEnv
from custom_wrappers import TetrisFeatureWrapper, TetrisRewardWrapper, VecTetrisFeatureWrapper

class TetrisRLAgent:
    """
    Reinforcement Learning agent for playing Tetris on PyBoy emulator.
    Supports multiple RL algorithms including PPO, A2C, and DQN.
    """
    
    ALGORITHMS = {
        'ppo': PPO,
        'a2c': A2C,
        'dqn': DQN
    }
    
    def __init__(self, env=None, algorithm='ppo', model_path=None, log_dir='./logs'):
        """
        Initialize the RL agent.
        
        Args:
            env: The environment to use (if None, must be set later)
            algorithm: The RL algorithm to use ('ppo', 'a2c', or 'dqn')
            model_path: Path to a pre-trained model (if available)
            log_dir: Directory to save logs
        """
        self.logger = logging.getLogger(__name__)
        self.env = env
        self.algorithm = algorithm.lower()
        self.model_path = model_path
        self.log_dir = log_dir
        self.model = None
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def set_environment(self, env):
        """
        Set the environment for the agent.
        
        Args:
            env: The environment to use
        """
        self.env = env
    
    def create_model(self):
        """
        Create or load a reinforcement learning model.
        
        Returns:
            The created or loaded model
        """
        if self.env is None:
            self.logger.error("Environment not set. Call set_environment() first.")
            raise ValueError("Environment not set")
        
        if self.algorithm not in self.ALGORITHMS:
            self.logger.error(f"Unsupported algorithm: {self.algorithm}")
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
        algorithm_class = self.ALGORITHMS[self.algorithm]
        
        if self.model_path and os.path.exists(self.model_path):
            self.logger.info(f"Loading model from {self.model_path}")
            self.model = algorithm_class.load(self.model_path, env=self.env)
        else:
            self.logger.info(f"Creating new {self.algorithm.upper()} model")
            
            if self.algorithm == 'ppo':
                self.model = algorithm_class(
                    "MlpPolicy",
                    self.env,
                    verbose=1,
                    learning_rate=0.003,  # Increased from 0.0003 to accelerate learning
                    n_steps=1024,         # Reduced from 2048 for more frequent updates
                    batch_size=64,
                    n_epochs=10,
                    gamma=0.99,
                    gae_lambda=0.95,
                    clip_range=0.2,
                    ent_coef=0.05,        # Increased entropy coefficient to strongly encourage exploration
                    vf_coef=0.5,          # Value function coefficient
                    policy_kwargs=dict(net_arch=[64, 64]),  # Simpler network architecture
                    tensorboard_log=os.path.join(self.log_dir, 'tensorboard')
                )
            elif self.algorithm == 'a2c':
                self.model = algorithm_class(
                    "MlpPolicy",
                    self.env,
                    verbose=1,
                    learning_rate=0.0007,
                    n_steps=5,
                    gamma=0.99,
                    tensorboard_log=os.path.join(self.log_dir, 'tensorboard')
                )
            elif self.algorithm == 'dqn':
                self.model = algorithm_class(
                    "MlpPolicy",
                    self.env,
                    verbose=1,
                    learning_rate=0.0001,
                    buffer_size=100000,
                    learning_starts=1000,
                    batch_size=32,
                    gamma=0.99,
                    target_update_interval=500,
                    exploration_fraction=0.1,
                    exploration_initial_eps=1.0,
                    exploration_final_eps=0.05,
                    tensorboard_log=os.path.join(self.log_dir, 'tensorboard')
                )
        
        return self.model
    
    def train(self, total_timesteps=100000, checkpoint_freq=10000, eval_freq=10000):
        """
        Train the reinforcement learning model.
        
        Args:
            total_timesteps: Number of timesteps to train for
            checkpoint_freq: Frequency (in timesteps) to save model checkpoints
            eval_freq: Frequency (in timesteps) to evaluate the model
            
        Returns:
            The trained model
        """
        if self.model is None:
            self.create_model()
        
        checkpoint_callback = CheckpointCallback(
            save_freq=checkpoint_freq,
            save_path=os.path.join(self.log_dir, 'checkpoints'),
            name_prefix=f"tetris_{self.algorithm}"
        )
        
        eval_callback = TetrisEvalCallback(
            self.env,
            eval_freq=eval_freq,
            log_path=os.path.join(self.log_dir, 'evaluations'),
            verbose=1
        )
        
        self.logger.info(f"Training {self.algorithm.upper()} model for {total_timesteps} timesteps")
        self.model.learn(
            total_timesteps=total_timesteps,
            callback=[checkpoint_callback, eval_callback]
        )
        
        model_save_path = os.path.join(self.log_dir, f"tetris_{self.algorithm}_final")
        self.model.save(model_save_path)
        self.logger.info(f"Final model saved to {model_save_path}")
        
        return self.model
    
    def play(self, episodes=1, deterministic=True, delay=0.0):
        """
        Play Tetris using the trained model.
        
        Args:
            episodes: Number of episodes to play
            deterministic: Whether to use deterministic actions
            delay: Delay between moves in seconds (for streaming)
            
        Returns:
            List of episode rewards
        """
        if self.model is None:
            self.create_model()
        
        self.logger.info(f"Playing {episodes} episodes of Tetris with {delay}s delay between moves")
        
        episode_rewards = []
        
        for episode in range(episodes):
            obs = self.env.reset()
            done = False
            total_reward = 0
            steps = 0
            
            while not done:
                action, _ = self.model.predict(obs, deterministic=deterministic)
                
                if delay > 0:
                    import time
                    time.sleep(delay)
                
                obs, reward, done, info = self.env.step(action)
                
                total_reward += reward[0]
                steps += 1
                
                if steps % 100 == 0:
                    self.logger.info(f"Episode {episode+1}, Step {steps}, Score: {info[0]['score']}")
                
                if done[0]:
                    self.logger.info(f"Episode {episode+1} finished after {steps} steps")
                    self.logger.info(f"Final score: {info[0]['score']}, Lines cleared: {info[0]['lines']}")
                    episode_rewards.append(total_reward)
                    break
        
        return episode_rewards
    
    def evaluate(self, n_eval_episodes=5):
        """
        Evaluate the trained model.
        
        Args:
            n_eval_episodes: Number of episodes to evaluate
            
        Returns:
            Mean reward and standard deviation
        """
        if self.model is None:
            self.create_model()
        
        self.logger.info(f"Evaluating model over {n_eval_episodes} episodes")
        
        mean_reward, std_reward = evaluate_policy(
            self.model,
            self.env,
            n_eval_episodes=n_eval_episodes,
            deterministic=True
        )
        
        self.logger.info(f"Mean reward: {mean_reward:.2f} +/- {std_reward:.2f}")
        
        return mean_reward, std_reward
    
    def save(self, path=None):
        """
        Save the trained model.
        
        Args:
            path: Path to save the model (if None, use default path)
            
        Returns:
            Path where the model was saved
        """
        if self.model is None:
            self.logger.error("No model to save. Create or train a model first.")
            raise ValueError("No model to save")
        
        if path is None:
            path = os.path.join(self.log_dir, f"tetris_{self.algorithm}")
        
        self.model.save(path)
        self.logger.info(f"Model saved to {path}")
        
        return path
    
    def load(self, path):
        """
        Load a trained model.
        
        Args:
            path: Path to the saved model
            
        Returns:
            The loaded model
        """
        if not os.path.exists(path):
            self.logger.error(f"Model file not found: {path}")
            raise FileNotFoundError(f"Model file not found: {path}")
        
        if self.algorithm not in self.ALGORITHMS:
            self.logger.error(f"Unsupported algorithm: {self.algorithm}")
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
        algorithm_class = self.ALGORITHMS[self.algorithm]
        
        self.logger.info(f"Loading model from {path}")
        self.model = algorithm_class.load(path, env=self.env)
        
        return self.model

class TetrisEvalCallback(BaseCallback):
    """
    Callback for evaluating the agent during training.
    """
    
    def __init__(self, eval_env, eval_freq=10000, n_eval_episodes=5, log_path=None, verbose=1):
        """
        Initialize the callback.
        
        Args:
            eval_env: Environment to evaluate on
            eval_freq: Frequency of evaluation (in timesteps)
            n_eval_episodes: Number of episodes to evaluate
            log_path: Path to save evaluation logs
            verbose: Verbosity level
        """
        super(TetrisEvalCallback, self).__init__(verbose)
        self.eval_env = eval_env
        self.eval_freq = eval_freq
        self.n_eval_episodes = n_eval_episodes
        self.log_path = log_path
        self.best_mean_reward = -np.inf
        self.evaluations_results = []
        self.evaluations_timesteps = []
        
        if log_path is not None:
            os.makedirs(log_path, exist_ok=True)
    
    def _on_step(self):
        """
        Called at each step of training.
        
        Returns:
            Whether to continue training
        """
        if self.eval_freq > 0 and self.n_calls % self.eval_freq == 0:
            mean_reward, std_reward = evaluate_policy(
                self.model,
                self.eval_env,
                n_eval_episodes=self.n_eval_episodes,
                deterministic=True
            )
            
            if self.verbose > 0:
                print(f"Evaluation at timestep {self.n_calls}")
                print(f"Mean reward: {mean_reward:.2f} +/- {std_reward:.2f}")
            
            self.evaluations_results.append(mean_reward)
            self.evaluations_timesteps.append(self.n_calls)
            
            if mean_reward > self.best_mean_reward:
                self.best_mean_reward = mean_reward
                if self.verbose > 0:
                    print(f"New best mean reward: {mean_reward:.2f}")
                
                if self.log_path is not None:
                    self.model.save(os.path.join(self.log_path, "best_model"))
            
            if self.log_path is not None:
                np.savez(
                    os.path.join(self.log_path, "evaluations"),
                    timesteps=self.evaluations_timesteps,
                    results=self.evaluations_results
                )
        
        return True

def create_tetris_env(rom_path, render_mode="human", adaptive_reward=True, turn_based=True):
    """
    Create a Tetris environment with all necessary wrappers.
    
    Args:
        rom_path: Path to the Tetris ROM file
        render_mode: Whether to render the game visually
        adaptive_reward: Whether to use the adaptive reward function
        turn_based: Whether to use turn-based gameplay mode
        
    Returns:
        Vectorized environment ready for RL training
    """
    base_env = TetrisPyBoyEnv(rom_path=rom_path, render_mode=render_mode, turn_based=turn_based)
    
    feature_env = TetrisFeatureWrapper(base_env)
    enhanced_env = TetrisRewardWrapper(feature_env, adaptive=adaptive_reward)
    
    monitor_env = Monitor(enhanced_env)
    
    vec_env = DummyVecEnv([lambda: monitor_env])
    
    monitored_env = VecMonitor(vec_env)
    
    final_env = VecTetrisFeatureWrapper(monitored_env)
    
    return final_env
