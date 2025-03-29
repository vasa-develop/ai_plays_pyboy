import os
import logging
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO, A2C, DQN
from stable_baselines3.common.callbacks import BaseCallback, EvalCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, VecFrameStack
from stable_baselines3.common.env_util import make_vec_env
from gym_wrapper.zelda_env import ZeldaPyBoyEnv
from zelda_state_preprocessor import ZeldaStatePreprocessor
from zelda_reward_function import ZeldaRewardFunction

class ZeldaEvalCallback(BaseCallback):
    """
    Custom callback for evaluating and saving the Zelda RL agent.
    """
    
    def __init__(self, eval_env, log_dir, eval_freq=10000, n_eval_episodes=5, 
                 save_path=None, verbose=1):
        super(ZeldaEvalCallback, self).__init__(verbose)
        self.eval_env = eval_env
        self.log_dir = log_dir
        self.eval_freq = eval_freq
        self.n_eval_episodes = n_eval_episodes
        self.save_path = save_path
        self.best_mean_reward = -np.inf
        self.last_mean_reward = -np.inf
        self.results_dir = os.path.join(log_dir, "results")
        os.makedirs(self.results_dir, exist_ok=True)
        
        self.logger = logging.getLogger("zelda_eval")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            file_handler = logging.FileHandler(os.path.join(log_dir, "evaluation.log"))
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def _on_step(self):
        """
        Called at each step of training.
        """
        if self.n_calls % self.eval_freq == 0:
            episode_rewards = []
            episode_lengths = []
            
            for i in range(self.n_eval_episodes):
                obs, _ = self.eval_env.reset()
                done = False
                truncated = False
                episode_reward = 0
                episode_length = 0
                
                while not (done or truncated):
                    action, _ = self.model.predict(obs, deterministic=True)
                    obs, reward, done, truncated, info = self.eval_env.step(action)
                    episode_reward += reward
                    episode_length += 1
                
                episode_rewards.append(episode_reward)
                episode_lengths.append(episode_length)
                
                self.logger.info(f"Evaluation episode {i+1}/{self.n_eval_episodes}: "
                                f"reward={episode_reward:.2f}, length={episode_length}")
            
            mean_reward = np.mean(episode_rewards)
            std_reward = np.std(episode_rewards)
            mean_length = np.mean(episode_lengths)
            
            self.logger.info(f"Evaluation at step {self.n_calls}: "
                            f"mean_reward={mean_reward:.2f} +/- {std_reward:.2f}, "
                            f"mean_length={mean_length:.1f}")
            
            if mean_reward > self.best_mean_reward:
                self.best_mean_reward = mean_reward
                if self.save_path is not None:
                    self.logger.info(f"Saving new best model to {self.save_path}")
                    self.model.save(self.save_path)
            
            self.last_mean_reward = mean_reward
            self._plot_results(episode_rewards, episode_lengths)
            
        return True
    
    def _plot_results(self, rewards, lengths):
        """
        Plot the evaluation results.
        """
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        plt.plot(range(1, len(rewards) + 1), rewards, marker='o')
        plt.axhline(y=np.mean(rewards), color='r', linestyle='-', 
                   label=f'Mean: {np.mean(rewards):.2f}')
        plt.fill_between(
            range(1, len(rewards) + 1),
            np.mean(rewards) - np.std(rewards),
            np.mean(rewards) + np.std(rewards),
            alpha=0.2,
            color='r',
            label=f'Std Dev: {np.std(rewards):.2f}'
        )
        plt.xlabel('Episode')
        plt.ylabel('Reward')
        plt.title('Zelda RL Agent Evaluation - Rewards')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(1, 2, 2)
        plt.plot(range(1, len(lengths) + 1), lengths, marker='o', color='g')
        plt.axhline(y=np.mean(lengths), color='r', linestyle='-', 
                   label=f'Mean: {np.mean(lengths):.2f}')
        plt.fill_between(
            range(1, len(lengths) + 1),
            np.mean(lengths) - np.std(lengths),
            np.mean(lengths) + np.std(lengths),
            alpha=0.2,
            color='r',
            label=f'Std Dev: {np.std(lengths):.2f}'
        )
        plt.xlabel('Episode')
        plt.ylabel('Length')
        plt.title('Zelda RL Agent Evaluation - Episode Lengths')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, f"eval_step_{self.n_calls}.png"))
        plt.close()

def create_zelda_env(rom_path, render_mode="headless"):
    """
    Create a Zelda environment with appropriate wrappers.
    
    Args:
        rom_path: Path to the Zelda ROM file
        render_mode: Whether to render the game (human) or not (headless)
        
    Returns:
        Vectorized environment for training
    """
    def make_env():
        env = ZeldaPyBoyEnv(rom_path=rom_path, render_mode=render_mode)
        env = Monitor(env)
        return env
    
    env = DummyVecEnv([make_env])
    env = VecFrameStack(env, n_stack=4)
    
    return env

class ZeldaRLAgent:
    """
    Reinforcement learning agent for playing Zelda: Link's Awakening.
    """
    
    def __init__(self, env=None, algorithm="ppo", model_path=None, log_dir="./zelda_logs"):
        """
        Initialize the Zelda RL agent.
        
        Args:
            env: Zelda environment
            algorithm: RL algorithm to use (ppo, a2c, or dqn)
            model_path: Path to pre-trained model
            log_dir: Directory to save logs and models
        """
        self.env = env
        self.algorithm = algorithm.lower()
        self.model_path = model_path
        self.log_dir = log_dir
        self.model = None
        
        os.makedirs(log_dir, exist_ok=True)
        
        self.logger = logging.getLogger("zelda_agent")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            file_handler = logging.FileHandler(os.path.join(log_dir, "training.log"))
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        if self.env is not None:
            self._create_model()
    
    def _create_model(self):
        """Create the RL model based on the selected algorithm."""
        policy = "CnnPolicy"  # Use CNN policy for image-based observations
        
        if self.algorithm == "ppo":
            self.model = PPO(
                policy,
                self.env,
                verbose=1,
                tensorboard_log=os.path.join(self.log_dir, "tensorboard"),
                learning_rate=0.0003,
                n_steps=2048,
                batch_size=64,
                n_epochs=10,
                gamma=0.99,
                gae_lambda=0.95,
                clip_range=0.2,
                ent_coef=0.01
            )
        elif self.algorithm == "a2c":
            self.model = A2C(
                policy,
                self.env,
                verbose=1,
                tensorboard_log=os.path.join(self.log_dir, "tensorboard"),
                learning_rate=0.0007,
                n_steps=5,
                gamma=0.99,
                ent_coef=0.01
            )
        elif self.algorithm == "dqn":
            self.model = DQN(
                policy,
                self.env,
                verbose=1,
                tensorboard_log=os.path.join(self.log_dir, "tensorboard"),
                learning_rate=0.0001,
                buffer_size=100000,
                learning_starts=1000,
                batch_size=32,
                gamma=0.99,
                exploration_fraction=0.1,
                exploration_final_eps=0.05
            )
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
        self.logger.info(f"Created {self.algorithm.upper()} model with {policy}")
    
    def train(self, total_timesteps=100000, eval_freq=10000, save_freq=10000, 
              n_eval_episodes=5, save_path=None):
        """
        Train the RL agent.
        
        Args:
            total_timesteps: Total number of timesteps to train for
            eval_freq: Frequency of evaluation during training
            save_freq: Frequency of saving model checkpoints
            n_eval_episodes: Number of episodes to evaluate on
            save_path: Path to save the final model
            
        Returns:
            Trained model
        """
        if self.model is None:
            raise ValueError("Model not initialized. Call set_env() first.")
        
        self.logger.info(f"Starting training for {total_timesteps} timesteps")
        self.logger.info(f"  Algorithm: {self.algorithm}")
        self.logger.info(f"  Evaluation frequency: {eval_freq}")
        self.logger.info(f"  Save frequency: {save_freq}")
        
        eval_env = create_zelda_env(self.env.get_attr("rom_path")[0], render_mode="headless")
        
        if save_path is None:
            save_path = os.path.join(self.log_dir, f"zelda_{self.algorithm}_final.zip")
        
        checkpoint_path = os.path.join(self.log_dir, f"zelda_{self.algorithm}")
        
        eval_callback = ZeldaEvalCallback(
            eval_env=eval_env,
            log_dir=self.log_dir,
            eval_freq=eval_freq,
            n_eval_episodes=n_eval_episodes,
            save_path=save_path,
            verbose=1
        )
        
        self.model.learn(
            total_timesteps=total_timesteps,
            callback=eval_callback,
            tb_log_name=f"zelda_{self.algorithm}"
        )
        
        self.model.save(save_path)
        self.logger.info(f"Training completed. Final model saved to {save_path}")
        
        return self.model
    
    def load(self, model_path):
        """
        Load a pre-trained model.
        
        Args:
            model_path: Path to the model file
            
        Returns:
            Loaded model
        """
        if not os.path.exists(model_path):
            raise ValueError(f"Model file not found: {model_path}")
        
        self.logger.info(f"Loading model from {model_path}")
        
        if self.algorithm == "ppo":
            self.model = PPO.load(model_path, env=self.env)
        elif self.algorithm == "a2c":
            self.model = A2C.load(model_path, env=self.env)
        elif self.algorithm == "dqn":
            self.model = DQN.load(model_path, env=self.env)
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
        self.logger.info(f"Model loaded successfully")
        
        return self.model
    
    def set_env(self, env):
        """
        Set the environment for the agent.
        
        Args:
            env: Zelda environment
        """
        self.env = env
        self._create_model()
    
    def play(self, episodes=1, deterministic=True, delay=0.0):
        """
        Play Zelda using the trained model.
        
        Args:
            episodes: Number of episodes to play
            deterministic: Whether to use deterministic actions
            delay: Delay between moves in seconds (for visualization)
            
        Returns:
            List of episode rewards
        """
        if self.model is None:
            raise ValueError("Model not initialized. Call set_env() or load() first.")
        
        self.logger.info(f"Playing {episodes} episodes with delay={delay}s")
        
        episode_rewards = []
        
        for i in range(episodes):
            obs, _ = self.env.reset()
            done = False
            truncated = False
            episode_reward = 0
            step = 0
            
            self.logger.info(f"Starting episode {i+1}/{episodes}")
            
            while not (done or truncated):
                action, _ = self.model.predict(obs, deterministic=deterministic)
                obs, reward, done, truncated, info = self.env.step(action)
                
                episode_reward += reward
                step += 1
                
                if step % 100 == 0:
                    self.logger.info(f"Episode {i+1}, Step {step}, Reward: {episode_reward:.2f}")
                
                if delay > 0:
                    import time
                    time.sleep(delay)
            
            episode_rewards.append(episode_reward)
            self.logger.info(f"Episode {i+1} completed with reward {episode_reward:.2f}")
        
        return episode_rewards
    
    def close(self):
        """Close the environment."""
        if self.env is not None:
            self.env.close()
