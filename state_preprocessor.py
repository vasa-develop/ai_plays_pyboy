import numpy as np

class TetrisStatePreprocessor:
    """
    Preprocesses the Tetris game state for reinforcement learning.
    Extracts meaningful features from the raw game state to help the agent learn more efficiently.
    """
    
    def __init__(self):
        """Initialize the state preprocessor."""
        pass
    
    def preprocess(self, observation):
        """
        Preprocess the raw observation from the environment.
        
        Args:
            observation: Dictionary containing 'board', 'current_piece', and 'next_piece'
            
        Returns:
            Processed observation with additional features
        """
        board = observation['board']
        next_piece = observation['next_piece']
        
        height_profile = self._get_height_profile(board)
        holes = self._count_holes(board, height_profile)
        bumpiness = self._calculate_bumpiness(height_profile)
        aggregated_height = sum(height_profile)
        
        features = np.concatenate([
            height_profile,                # Column heights (10 features)
            [holes],                       # Number of holes
            [bumpiness],                   # Bumpiness of the profile
            [aggregated_height],           # Sum of all column heights
            next_piece                     # One-hot encoded next piece (7 features)
        ])
        
        return features
    
    def _get_height_profile(self, board):
        """
        Calculate the height of each column in the board.
        
        Args:
            board: 2D numpy array representing the game board (18x10)
            
        Returns:
            Array of heights for each column
        """
        height_profile = np.zeros(10, dtype=np.int8)
        
        for col in range(10):
            for row in range(18):
                if board[row][col] == 1:
                    height_profile[col] = 18 - row
                    break
        
        return height_profile
    
    def _count_holes(self, board, height_profile):
        """
        Count the number of holes in the board.
        A hole is an empty cell with at least one filled cell above it in the same column.
        
        Args:
            board: 2D numpy array representing the game board (18x10)
            height_profile: Array of heights for each column
            
        Returns:
            Number of holes
        """
        holes = 0
        
        for col in range(10):
            if height_profile[col] == 0:
                continue
                
            for row in range(18 - height_profile[col], 18):
                if board[row][col] == 0:
                    holes += 1
        
        return holes
    
    def _calculate_bumpiness(self, height_profile):
        """
        Calculate the bumpiness of the board.
        Bumpiness is the sum of absolute differences between adjacent column heights.
        
        Args:
            height_profile: Array of heights for each column
            
        Returns:
            Bumpiness value
        """
        bumpiness = 0
        
        for i in range(9):
            bumpiness += abs(height_profile[i] - height_profile[i+1])
        
        return bumpiness
    
    def extract_reward_features(self, observation, next_observation, reward):
        """
        Extract additional reward features based on state transitions.
        
        Args:
            observation: Previous observation
            next_observation: Current observation
            reward: Raw reward from the environment
            
        Returns:
            Enhanced reward based on state features
        """
        prev_board = observation['board']
        next_board = next_observation['board']
        
        prev_height_profile = self._get_height_profile(prev_board)
        next_height_profile = self._get_height_profile(next_board)
        
        prev_holes = self._count_holes(prev_board, prev_height_profile)
        next_holes = self._count_holes(next_board, next_height_profile)
        
        prev_bumpiness = self._calculate_bumpiness(prev_height_profile)
        next_bumpiness = self._calculate_bumpiness(next_height_profile)
        
        prev_agg_height = sum(prev_height_profile)
        next_agg_height = sum(next_height_profile)
        
        hole_diff = prev_holes - next_holes
        bumpiness_diff = prev_bumpiness - next_bumpiness
        height_diff = prev_agg_height - next_agg_height
        
        adjusted_reward = reward
        adjusted_reward += hole_diff * 0.5       # Reward for reducing holes
        adjusted_reward += bumpiness_diff * 0.2  # Reward for reducing bumpiness
        adjusted_reward += height_diff * 0.1     # Reward for reducing height
        
        return adjusted_reward
