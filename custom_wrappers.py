import gymnasium as gym
import numpy as np
from stable_baselines3.common.vec_env import VecEnvWrapper
from state_preprocessor import TetrisStatePreprocessor

class TetrisFeatureWrapper(gym.Wrapper):
    """
    A wrapper that enhances the Tetris environment with feature extraction.
    Transforms the raw observations into a feature vector using the TetrisStatePreprocessor.
    """
    
    def __init__(self, env):
        """
        Initialize the wrapper.
        
        Args:
            env: The environment to wrap
        """
        super(TetrisFeatureWrapper, self).__init__(env)
        self.state_preprocessor = TetrisStatePreprocessor()
        
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(20,), dtype=np.float32
        )
    
    def reset(self, **kwargs):
        """
        Reset the environment and preprocess the initial observation.
        
        Returns:
            Preprocessed observation
        """
        obs, info = self.env.reset(**kwargs)
        processed_obs = self.state_preprocessor.preprocess(obs)
        return processed_obs, info
    
    def step(self, action):
        """
        Take a step in the environment and preprocess the resulting observation.
        
        Args:
            action: The action to take
            
        Returns:
            Preprocessed observation, reward, terminated, truncated, info
        """
        obs, reward, terminated, truncated, info = self.env.step(action)
        processed_obs = self.state_preprocessor.preprocess(obs)
        return processed_obs, reward, terminated, truncated, info

class TetrisRewardWrapper(gym.Wrapper):
    """
    A wrapper that enhances the reward function for the Tetris environment.
    Uses the TetrisStatePreprocessor to calculate additional reward components.
    """
    
    def __init__(self, env):
        """
        Initialize the wrapper.
        
        Args:
            env: The environment to wrap
        """
        super(TetrisRewardWrapper, self).__init__(env)
        self.state_preprocessor = TetrisStatePreprocessor()
        self.previous_obs = None
    
    def reset(self, **kwargs):
        """
        Reset the environment and store the initial observation.
        
        Returns:
            Observation from the wrapped environment
        """
        obs, info = self.env.reset(**kwargs)
        self.previous_obs = obs
        return obs, info
    
    def step(self, action):
        """
        Take a step in the environment and enhance the reward.
        
        Args:
            action: The action to take
            
        Returns:
            Observation, enhanced reward, terminated, truncated, info
        """
        obs, reward, terminated, truncated, info = self.env.step(action)
        
        if self.previous_obs is not None:
            enhanced_reward = self.state_preprocessor.extract_reward_features(
                self.previous_obs, obs, reward
            )
        else:
            enhanced_reward = reward
        
        self.previous_obs = obs
        
        return obs, enhanced_reward, terminated, truncated, info

class VecTetrisFeatureWrapper(VecEnvWrapper):
    """
    A vectorized environment wrapper that applies feature extraction to observations.
    Compatible with Stable Baselines3 vectorized environments.
    """
    
    def __init__(self, venv):
        """
        Initialize the wrapper.
        
        Args:
            venv: The vectorized environment to wrap
        """
        super(VecTetrisFeatureWrapper, self).__init__(venv)
        self.state_preprocessor = TetrisStatePreprocessor()
        
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(20,), dtype=np.float32
        )
    
    def reset(self):
        """
        Reset the environment and preprocess the initial observation.
        
        Returns:
            Preprocessed observation
        """
        obs = self.venv.reset()
        return self._preprocess_obs(obs)
    
    def step_wait(self):
        """
        Wait for the step to complete and preprocess the resulting observation.
        
        Returns:
            Preprocessed observation, reward, done, info
        """
        obs, reward, done, info = self.venv.step_wait()
        return self._preprocess_obs(obs), reward, done, info
    
    def _preprocess_obs(self, obs):
        """
        Preprocess a batch of observations.
        
        Args:
            obs: Batch of observations from the vectorized environment
            
        Returns:
            Batch of preprocessed observations
        """
        processed_obs = []
        for i in range(len(obs)):
            processed_obs.append(self.state_preprocessor.preprocess(obs[i]))
        
        return np.array(processed_obs, dtype=np.float32)
