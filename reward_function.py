import numpy as np
from state_preprocessor import TetrisStatePreprocessor

class TetrisRewardFunction:
    """
    Reward function for the Tetris environment.
    Calculates rewards based on game state changes and Tetris-specific metrics.
    """
    
    def __init__(self):
        """Initialize the reward function."""
        self.state_preprocessor = TetrisStatePreprocessor()
        self.prev_score = 0
        self.prev_lines = 0
        self.prev_level = 0
        
        self.weights = {
            'score': 2.0,        # Increased weight for score increase (was 1.0)
            'lines': 15.0,       # Increased weight for lines cleared (was 10.0)
            'tetris': 30.0,      # Increased reward for clearing 4 lines at once (was 20.0)
            'holes': -0.3,       # Reduced penalty for creating holes (was -0.5)
            'bumpiness': -0.1,   # Reduced penalty for uneven surface (was -0.2)
            'height': -0.05,     # Reduced penalty for increasing height (was -0.1)
            'game_over': -5.0,   # Further reduced penalty for game over (was -10.0)
            'survival': 0.2      # Increased reward for surviving each step (was 0.1)
        }
    
    def calculate_reward(self, prev_obs, obs, info, done):
        """
        Calculate the reward based on the current and previous observations.
        
        Args:
            prev_obs: Previous observation
            obs: Current observation
            info: Additional information from the environment
            done: Whether the episode is done
            
        Returns:
            Calculated reward
        """
        current_score = info.get('score', 0)
        current_lines = info.get('lines', 0)
        current_level = info.get('level', 0)
        
        score_reward = (current_score - self.prev_score) * self.weights['score']
        
        lines_cleared = current_lines - self.prev_lines
        lines_reward = 0
        if lines_cleared > 0:
            lines_reward = lines_cleared * self.weights['lines']
            
            if lines_cleared == 4:
                lines_reward += self.weights['tetris']
        
        level_reward = (current_level - self.prev_level) * 20.0
        
        board_reward = self._calculate_board_reward(prev_obs, obs)
        
        game_over_penalty = self.weights['game_over'] if done else 0
        
        survival_reward = self.weights['survival']
        
        self.prev_score = current_score
        self.prev_lines = current_lines
        self.prev_level = current_level
        
        total_reward = (
            score_reward +
            lines_reward +
            level_reward +
            board_reward +
            game_over_penalty +
            survival_reward
        )
        
        return total_reward
    
    def _calculate_board_reward(self, prev_obs, obs):
        """
        Calculate rewards based on changes in the board state.
        
        Args:
            prev_obs: Previous observation
            obs: Current observation
            
        Returns:
            Board state reward
        """
        if prev_obs is None or 'board' not in prev_obs or 'board' not in obs:
            return 0
        
        prev_board = prev_obs['board']
        current_board = obs['board']
        
        prev_height_profile = self.state_preprocessor._get_height_profile(prev_board)
        current_height_profile = self.state_preprocessor._get_height_profile(current_board)
        
        prev_holes = self.state_preprocessor._count_holes(prev_board, prev_height_profile)
        current_holes = self.state_preprocessor._count_holes(current_board, current_height_profile)
        
        prev_bumpiness = self.state_preprocessor._calculate_bumpiness(prev_height_profile)
        current_bumpiness = self.state_preprocessor._calculate_bumpiness(current_height_profile)
        
        prev_height = sum(prev_height_profile)
        current_height = sum(current_height_profile)
        
        holes_reward = (prev_holes - current_holes) * self.weights['holes']
        bumpiness_reward = (prev_bumpiness - current_bumpiness) * self.weights['bumpiness']
        height_reward = (prev_height - current_height) * self.weights['height']
        
        board_reward = holes_reward + bumpiness_reward + height_reward
        
        return board_reward
    
    def reset(self):
        """Reset the reward function state."""
        self.prev_score = 0
        self.prev_lines = 0
        self.prev_level = 0

class AdaptiveRewardFunction(TetrisRewardFunction):
    """
    Adaptive reward function that adjusts weights based on game progress.
    Extends the base TetrisRewardFunction with dynamic weight adjustment.
    """
    
    def __init__(self):
        """Initialize the adaptive reward function."""
        super(AdaptiveRewardFunction, self).__init__()
        self.episode_steps = 0
        self.max_steps = 10000
        
        self.initial_weights = self.weights.copy()
        self.final_weights = {
            'score': 0.5,        # Reduced focus on score
            'lines': 15.0,       # Increased focus on lines
            'tetris': 30.0,      # Increased focus on Tetris
            'holes': -1.0,       # Increased penalty for holes
            'bumpiness': -0.5,   # Increased penalty for bumpiness
            'height': -0.2,      # Increased penalty for height
            'game_over': -50.0,  # Same penalty for game over
            'survival': 0.005    # Reduced survival reward
        }
    
    def calculate_reward(self, prev_obs, obs, info, done):
        """
        Calculate reward with adaptive weights based on game progress.
        
        Args:
            prev_obs: Previous observation
            obs: Current observation
            info: Additional information from the environment
            done: Whether the episode is done
            
        Returns:
            Calculated reward
        """
        self.episode_steps += 1
        
        progress = min(1.0, self.episode_steps / self.max_steps)
        self._adapt_weights(progress)
        
        reward = super().calculate_reward(prev_obs, obs, info, done)
        
        if done:
            self.episode_steps = 0
        
        return reward
    
    def _adapt_weights(self, progress):
        """
        Adapt weights based on episode progress.
        
        Args:
            progress: Episode progress (0.0 to 1.0)
        """
        for key in self.weights:
            self.weights[key] = (
                self.initial_weights[key] * (1 - progress) +
                self.final_weights[key] * progress
            )
    
    def reset(self):
        """Reset the reward function state."""
        super().reset()
        self.episode_steps = 0
        self.weights = self.initial_weights.copy()
