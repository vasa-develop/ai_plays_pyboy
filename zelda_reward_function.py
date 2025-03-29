import numpy as np

class ZeldaRewardFunction:
    """
    Reward function for the Zelda: Link's Awakening environment.
    Calculates rewards based on game progress, exploration, combat, and puzzle-solving.
    """
    
    def __init__(self):
        """Initialize the reward function with default weights."""
        self.weights = {
            'health_gain': 2.0,      # Reward for gaining health
            'health_loss': -1.0,     # Penalty for losing health
            'rupee_gain': 0.1,       # Reward for collecting rupees
            'item_collect': 5.0,     # Reward for collecting new items
            'enemy_defeat': 2.0,     # Reward for defeating enemies
            'room_explore': 3.0,     # Reward for exploring new rooms
            'movement': 0.01,        # Small reward for movement
            'time_penalty': -0.001,  # Small penalty for each step
            'death_penalty': -10.0,  # Large penalty for dying
            'progress_reward': 10.0, # Large reward for game progress (dungeons, bosses)
            'puzzle_solve': 5.0      # Reward for solving puzzles
        }
        
        self.prev_state = None
        
    def set_weights(self, weights):
        """
        Set custom weights for the reward function.
        
        Args:
            weights: Dictionary of reward weights
        """
        self.weights.update(weights)
    
    def calculate_reward(self, current_state, prev_state=None):
        """
        Calculate the reward based on the current and previous game states.
        
        Args:
            current_state: Current game state
            prev_state: Previous game state (if None, use stored previous state)
            
        Returns:
            Calculated reward value
        """
        if prev_state is None:
            prev_state = self.prev_state
        
        if prev_state is None:
            self.prev_state = current_state.copy() if hasattr(current_state, 'copy') else current_state
            return 0.0
        
        reward = 0.0
        
        if 'health' in current_state and 'health' in prev_state:
            health_diff = current_state['health'] - prev_state['health']
            if health_diff > 0:
                reward += self.weights['health_gain'] * health_diff
            elif health_diff < 0:
                reward += self.weights['health_loss'] * health_diff
        
        if 'rupees' in current_state and 'rupees' in prev_state:
            rupee_diff = current_state['rupees'] - prev_state['rupees']
            if rupee_diff > 0:
                reward += self.weights['rupee_gain'] * rupee_diff
        
        if 'items' in current_state and 'items' in prev_state:
            if isinstance(current_state['items'], np.ndarray) and isinstance(prev_state['items'], np.ndarray):
                new_items = np.sum((current_state['items'] > 0) & (prev_state['items'] == 0))
                if new_items > 0:
                    reward += self.weights['item_collect'] * new_items
        
        if 'enemies_defeated' in current_state and 'enemies_defeated' in prev_state:
            enemies_diff = current_state['enemies_defeated'] - prev_state['enemies_defeated']
            if enemies_diff > 0:
                reward += self.weights['enemy_defeat'] * enemies_diff
        
        if 'map_position' in current_state and 'map_position' in prev_state:
            if current_state['map_position'] != prev_state['map_position']:
                reward += self.weights['room_explore']
        
        if 'position' in current_state and 'position' in prev_state:
            if current_state['position'] != prev_state['position']:
                if isinstance(current_state['position'], tuple) and isinstance(prev_state['position'], tuple):
                    distance = np.sqrt(
                        (current_state['position'][0] - prev_state['position'][0])**2 +
                        (current_state['position'][1] - prev_state['position'][1])**2
                    )
                    reward += self.weights['movement'] * distance
        
        if 'progress' in current_state and 'progress' in prev_state:
            progress_diff = current_state['progress'] - prev_state['progress']
            if progress_diff > 0:
                reward += self.weights['progress_reward'] * progress_diff
        
        if 'puzzles_solved' in current_state and 'puzzles_solved' in prev_state:
            puzzles_diff = current_state['puzzles_solved'] - prev_state['puzzles_solved']
            if puzzles_diff > 0:
                reward += self.weights['puzzle_solve'] * puzzles_diff
        
        if 'game_over' in current_state and current_state['game_over']:
            reward += self.weights['death_penalty']
        
        reward += self.weights['time_penalty']
        
        self.prev_state = current_state.copy() if hasattr(current_state, 'copy') else current_state
        
        return reward
    
    def calculate_reward_from_progress(self, progress_info):
        """
        Calculate reward from progress information.
        
        Args:
            progress_info: Dictionary of progress indicators
            
        Returns:
            Calculated reward value
        """
        reward = 0.0
        
        if 'health_change' in progress_info:
            health_change = progress_info['health_change']
            if health_change > 0:
                reward += self.weights['health_gain'] * health_change
            elif health_change < 0:
                reward += self.weights['health_loss'] * health_change
        
        if 'rupee_change' in progress_info:
            rupee_change = progress_info['rupee_change']
            if rupee_change > 0:
                reward += self.weights['rupee_gain'] * rupee_change
        
        if 'position_change' in progress_info:
            position_change = progress_info['position_change']
            reward += self.weights['movement'] * position_change
        
        if 'map_change' in progress_info and progress_info['map_change']:
            reward += self.weights['room_explore']
        
        if 'inventory_change' in progress_info:
            inventory_change = progress_info['inventory_change']
            if inventory_change > 0:
                reward += self.weights['item_collect'] * inventory_change
        
        if 'enemies_defeated' in progress_info:
            enemies_defeated = progress_info['enemies_defeated']
            if enemies_defeated > 0:
                reward += self.weights['enemy_defeat'] * enemies_defeated
        
        if 'game_progress' in progress_info:
            game_progress = progress_info['game_progress']
            if game_progress > 0:
                reward += self.weights['progress_reward'] * game_progress
        
        if 'puzzles_solved' in progress_info:
            puzzles_solved = progress_info['puzzles_solved']
            if puzzles_solved > 0:
                reward += self.weights['puzzle_solve'] * puzzles_solved
        
        if 'game_over' in progress_info and progress_info['game_over']:
            reward += self.weights['death_penalty']
        
        reward += self.weights['time_penalty']
        
        return reward
