import gymnasium as gym
from gymnasium import spaces
import numpy as np
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
    
    def __init__(self, rom_path="tetris.gb", render_mode="human"):
        super(TetrisPyBoyEnv, self).__init__()
        
        self.rom_path = rom_path
        self.render_mode = render_mode
        self.pyboy = None
        self.tetris = None
        self.prev_score = 0
        self.prev_lines = 0
        self.frame_count = 0
        self.max_frames_per_episode = 10000  # Limit episode length
        
        self.action_space = spaces.Discrete(len(self.ACTIONS))
        
        self.observation_space = spaces.Dict({
            'board': spaces.Box(low=0, high=1, shape=(18, 10), dtype=np.int8),
            'current_piece': spaces.Box(low=0, high=1, shape=(7,), dtype=np.int8),
            'next_piece': spaces.Box(low=0, high=1, shape=(7,), dtype=np.int8),
        })
        
    def _get_observation(self):
        """Extract the current game state as an observation."""
        board = np.zeros((18, 10), dtype=np.int8)
        for y in range(18):
            for x in range(10):
                if self.tetris.game_area()[y][x]:
                    board[y][x] = 1
        
        current_piece = np.zeros(7, dtype=np.int8)
        current_piece_id = self._tetromino_to_id(self.tetris.current_tetromino())
        if current_piece_id is not None:
            current_piece[current_piece_id] = 1
        
        next_piece = np.zeros(7, dtype=np.int8)
        next_piece_id = self._tetromino_to_id(self.tetris.next_tetromino())
        if next_piece_id is not None:
            next_piece[next_piece_id] = 1
        
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
    
    def _is_game_over(self):
        """Check if the game is over."""
        
        return ((hasattr(self.tetris, 'game_over') and self.tetris.game_over) or 
                (self.tetris.score == 0 and self.tetris.level == 0 and self.frame_count > 120))
    
    def step(self, action):
        """
        Execute one time step within the environment.
        
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
        
        for _ in range(5):
            self.pyboy.tick()
            self.frame_count += 1
        
        observation = self._get_observation()
        
        reward = self._calculate_reward()
        
        terminated = self._is_game_over()
        truncated = self.frame_count >= self.max_frames_per_episode
        
        info = {
            'score': self.tetris.score,
            'lines': self.tetris.lines,
            'level': self.tetris.level,
            'frame_count': self.frame_count
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
            options: Additional options for reset
            
        Returns:
            observation: The initial state of the game
            info: Additional information
        """
        super().reset(seed=seed)
        
        if self.pyboy is not None:
            self.pyboy.stop()
        
        window = "SDL2" if self.render_mode == "human" else "null"
        self.pyboy = PyBoy(self.rom_path, window=window, scale=3)
        
        self.pyboy.set_emulation_speed(0)
        
        if self.pyboy.cartridge_title != "TETRIS":
            self.pyboy.stop()
            raise ValueError("The provided ROM is not Tetris")
        
        self.tetris = self.pyboy.game_wrapper
        
        self.tetris.start_game(timer_div=0x00)
        
        for _ in range(60):
            self.pyboy.tick()
        
        self.prev_score = 0
        self.prev_lines = 0
        self.frame_count = 0
        
        observation = self._get_observation()
        
        info = {
            'score': self.tetris.score,
            'lines': self.tetris.lines,
            'level': self.tetris.level,
            'frame_count': self.frame_count
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
