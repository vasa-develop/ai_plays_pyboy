import gymnasium as gym
from gymnasium import spaces
import numpy as np
import os
import datetime
from pyboy import PyBoy
from pyboy.utils import WindowEvent

class TetrisPyBoyEnv(gym.Env):
    """
    PyBoy Tetris environment that follows the Gymnasium interface.
    This environment provides a standardized way to train reinforcement learning
    agents to play Tetris on the Game Boy emulator.
    """
    metadata = {'render_modes': ['human']}
    
    ACTIONS = [
        WindowEvent.PRESS_ARROW_UP,    # Rotate
        WindowEvent.PRESS_ARROW_RIGHT, # Move right
        WindowEvent.PRESS_ARROW_LEFT,  # Move left
        WindowEvent.PRESS_ARROW_DOWN,  # Move down
        WindowEvent.PRESS_BUTTON_A,    # A button (alternative rotate)
        WindowEvent.PRESS_BUTTON_B,    # B button (unused in Tetris)
        None,                          # No action
    ]
    
    RELEASE_ACTIONS = [
        WindowEvent.RELEASE_ARROW_UP,
        WindowEvent.RELEASE_ARROW_RIGHT,
        WindowEvent.RELEASE_ARROW_LEFT,
        WindowEvent.RELEASE_ARROW_DOWN,
        WindowEvent.RELEASE_BUTTON_A,
        WindowEvent.RELEASE_BUTTON_B,
        None,
    ]
    
    def __init__(self, rom_path="tetris.gb", render_mode="human", turn_based=True):
        super(TetrisPyBoyEnv, self).__init__()
        
        self.rom_path = rom_path
        self.render_mode = render_mode
        self.turn_based = turn_based  # Turn-based mode flag
        self.pyboy = None
        self.tetris = None
        self.prev_score = 0
        self.prev_lines = 0
        self.frame_count = 0
        self.max_frames_per_episode = 10000  # Limit episode length
        self.piece_locked = False  # Flag to track if the current piece has locked in place
        
        self.action_space = spaces.Discrete(len(self.ACTIONS))
        
        self.observation_space = spaces.Dict({
            'board': spaces.Box(low=0, high=1, shape=(18, 10), dtype=np.int8),
            'current_piece': spaces.Box(low=0, high=1, shape=(7,), dtype=np.int8),
            'next_piece': spaces.Box(low=0, high=1, shape=(7,), dtype=np.int8),
        })
        
    def _get_observation(self):
        """Extract the current game state as an observation."""
        board = np.zeros((18, 10), dtype=np.int8)
        try:
            for y in range(18):
                for x in range(10):
                    if self.tetris.game_area()[y][x]:
                        board[y][x] = 1
        except (AttributeError, IndexError) as e:
            print(f"Warning: Error accessing game area: {e}")
        
        current_piece = np.zeros(7, dtype=np.int8)
        current_piece[0] = 1
        
        next_piece = np.zeros(7, dtype=np.int8)
        try:
            if hasattr(self.tetris, 'next_tetromino'):
                next_piece_id = self._tetromino_to_id(self.tetris.next_tetromino())
                if next_piece_id is not None:
                    next_piece[next_piece_id] = 1
            else:
                import random
                next_piece[random.randint(0, 6)] = 1
        except Exception as e:
            print(f"Warning: Error getting next piece: {e}")
        
        return {
            'board': board,
            'current_piece': current_piece,
            'next_piece': next_piece,
        }
    
    def _tetromino_to_id(self, tetromino):
        """Convert tetromino name to ID (0-6)."""
        if tetromino is None:
            return None
            
        tetrominos = ["I", "J", "L", "O", "S", "T", "Z"]
        try:
            return tetrominos.index(tetromino)
        except ValueError:
            return None
    
    def _calculate_reward(self):
        """Calculate the reward based on score and lines cleared."""
        try:
            current_score = self.tetris.score
            current_lines = self.tetris.lines
            
            score_diff = current_score - self.prev_score
            lines_diff = current_lines - self.prev_lines
            
            self.prev_score = current_score
            self.prev_lines = current_lines
            
            reward = score_diff / 100.0  # Normalize score
            
            if lines_diff > 0:
                reward += 2 ** lines_diff
            
            reward -= 0.01
            
            if self._is_game_over():
                reward -= 10
            
            return reward
        except Exception as e:
            print(f"Warning: Error calculating reward: {e}")
            return -0.01
    
    def _is_game_over(self):
        """Check if the game is over."""
        
        if self.frame_count < 30:
            return False
            
        game_over = ((hasattr(self.tetris, 'game_over') and self.tetris.game_over) or 
                     (self.tetris.score == 0 and self.tetris.level == 0 and self.frame_count > 120))
        
        if game_over and self.render_mode == "human" and self.pyboy is not None:
            self._save_game_over_screenshot()
            
        return game_over
        
    def _save_game_over_screenshot(self):
        """Save a screenshot when game over is detected for debugging."""
        try:
            os.makedirs("game_over_screenshots", exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"game_over_screenshots/game_over_{timestamp}_frame{self.frame_count}.png"
            
            self.pyboy.screen_image().save(filename)
            print(f"Game over screenshot saved to {filename}")
        except Exception as e:
            print(f"Failed to save game over screenshot: {e}")
    
    def _is_piece_locked(self):
        """Check if the current piece has locked in place."""
        try:
            board_before = self._get_observation()['board'].copy()
            
            self.pyboy.send_input(WindowEvent.PRESS_ARROW_DOWN)
            self.pyboy.tick()
            self.pyboy.send_input(WindowEvent.RELEASE_ARROW_DOWN)
            
            for _ in range(3):
                self.pyboy.tick()
            
            board_after = self._get_observation()['board'].copy()
            
            return np.array_equal(board_before, board_after)
        except Exception as e:
            print(f"Warning: Error checking if piece is locked: {e}")
            return True
    
    def step(self, action):
        """
        Execute one time step within the environment.
        
        In turn-based mode, each step represents a complete piece placement,
        from spawn to lock. In continuous mode, each step is a single action.
        
        Args:
            action: An integer representing the action to take
            
        Returns:
            observation: The current state of the game
            reward: The reward for taking the action
            terminated: Whether the episode has ended
            truncated: Whether the episode was truncated (e.g., due to time limit)
            info: Additional information
        """
        if self.pyboy is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")
        
        action_name = "None" if action == 6 else str(self.ACTIONS[action]).split('.')[-1]
        print(f"Frame {self.frame_count}: Taking action {action_name}")
        
        if self.ACTIONS[action] is not None:
            self.pyboy.send_input(self.ACTIONS[action])
            self.pyboy.tick()
            self.pyboy.send_input(self.RELEASE_ACTIONS[action])
            self.frame_count += 1
        
        if self.turn_based:
            piece_locked = False
            max_frames_per_piece = 100  # Safety limit to prevent infinite loops
            frames_since_action = 0
            
            while not piece_locked and frames_since_action < max_frames_per_piece:
                for _ in range(3):
                    self.pyboy.tick()
                    self.frame_count += 1
                
                frames_since_action += 3
                
                piece_locked = self._is_piece_locked()
                
                if frames_since_action > 50 and frames_since_action % 10 == 0:
                    self.pyboy.send_input(WindowEvent.PRESS_ARROW_DOWN)
                    self.pyboy.tick()
                    self.pyboy.send_input(WindowEvent.RELEASE_ARROW_DOWN)
                    self.frame_count += 1
            
            print(f"Piece locked after {frames_since_action} frames")
        else:
            for _ in range(5):
                self.pyboy.tick()
                self.frame_count += 1
        
        observation = self._get_observation()
        reward = self._calculate_reward()
        
        terminated = self._is_game_over()
        truncated = self.frame_count >= self.max_frames_per_episode
        
        info = {
            'score': getattr(self.tetris, 'score', 0),
            'lines': getattr(self.tetris, 'lines', 0),
            'level': getattr(self.tetris, 'level', 0),
            'frame_count': self.frame_count,
            'turn_based': self.turn_based
        }
        
        print(f"Frame {self.frame_count}: Score={info['score']}, Lines={info['lines']}, Reward={reward:.2f}")
        
        if terminated:
            print(f"Episode terminated at frame {self.frame_count}. Game over detected.")
            print(f"Final score: {info['score']}, Lines cleared: {info['lines']}")
        
        if truncated:
            print(f"Episode truncated at frame {self.frame_count} (max frames reached).")
        
        return observation, reward, terminated, truncated, info
    
    def reset(self, seed=None, options=None):
        """
        Reset the environment to an initial state.
        
        Args:
            seed: Random seed for reproducibility
            options: Additional options for reset. Can include:
                - turn_based: Override the default turn-based setting
            
        Returns:
            observation: The initial state of the game
            info: Additional information
        """
        super().reset(seed=seed)
        
        if options is not None:
            if 'turn_based' in options:
                self.turn_based = options['turn_based']
        
        if self.pyboy is not None:
            self.pyboy.stop()
        
        window = "SDL2" if self.render_mode == "human" else "null"
        self.pyboy = PyBoy(self.rom_path, window=window, scale=3)
        
        if self.turn_based:
            self.pyboy.set_emulation_speed(0)
        else:
            self.pyboy.set_emulation_speed(4)
        
        if not self.pyboy.cartridge_title or "TETRIS" not in self.pyboy.cartridge_title.upper():
            print(f"Warning: ROM title '{self.pyboy.cartridge_title}' may not be Tetris, but continuing anyway")
        
        self.tetris = self.pyboy.game_wrapper
        
        self.tetris.start_game(timer_div=0x00)
        
        for _ in range(60):
            self.pyboy.tick()
        
        self.prev_score = 0
        self.prev_lines = 0
        self.frame_count = 0
        self.piece_locked = False
        
        observation = self._get_observation()
        
        info = {
            'score': getattr(self.tetris, 'score', 0),
            'lines': getattr(self.tetris, 'lines', 0),
            'level': getattr(self.tetris, 'level', 0),
            'frame_count': self.frame_count,
            'turn_based': self.turn_based
        }
        
        return observation, info
    
    def render(self):
        """
        Render the environment.
        
        For PyBoy, rendering is handled automatically if window_type is set to SDL2.
        This method is included for compatibility with the Gym interface.
        """
        pass
    
    def close(self):
        """Clean up resources."""
        if self.pyboy is not None:
            self.pyboy.stop()
            self.pyboy = None
