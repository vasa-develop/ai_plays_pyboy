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
    
    def __init__(self, rom_path="tetris.gb", render_mode="human", turn_based=True, emulation_speed=0, frame_delay=0.0):
        super(TetrisPyBoyEnv, self).__init__()
        
        self.rom_path = rom_path
        self.render_mode = render_mode
        self.turn_based = turn_based  # Turn-based mode flag
        self.emulation_speed = emulation_speed  # Control emulation speed (0 = unlimited, 1 = normal, 2 = 2x, etc.)
        self.frame_delay = frame_delay  # Additional delay between frames in seconds
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
        """Calculate the reward based on score, lines cleared, and game state."""
        try:
            current_score = getattr(self.tetris, 'score', 0)
            current_lines = getattr(self.tetris, 'lines', 0)
            
            score_diff = current_score - self.prev_score
            lines_diff = current_lines - self.prev_lines
            
            self.prev_score = current_score
            self.prev_lines = current_lines
            
            reward = 0.0
            
            if score_diff > 0:
                reward += score_diff / 100.0  # Normalize score
                print(f"[REWARD] +{score_diff/100.0:.2f} for score increase of {score_diff}")
            
            if lines_diff > 0:
                line_reward = 2 ** lines_diff
                reward += line_reward
                print(f"[REWARD] +{line_reward:.2f} for clearing {lines_diff} lines")
            
            if self.turn_based:
                if not self._is_game_over():
                    reward += 0.1  # Small positive reward for each successful piece placement
                    print(f"[REWARD] +0.1 for successful piece placement")
                
                if self._is_game_over():
                    reward -= 5.0  # Reduced penalty in turn-based mode
                    print(f"[REWARD] -5.0 for game over")
            else:
                step_penalty = 0.01
                reward -= step_penalty
                print(f"[REWARD] -{step_penalty:.2f} step penalty (continuous mode)")
                
                if self.piece_locked:
                    placement_reward = 0.5
                    reward += placement_reward
                    print(f"[REWARD] +{placement_reward:.2f} for piece placement (continuous mode)")
                    self.piece_locked = False  # Reset the flag
                
                if self._is_game_over():
                    game_over_penalty = 10.0
                    reward -= game_over_penalty
                    print(f"[REWARD] -{game_over_penalty:.2f} for game over")
            
            print(f"[REWARD] Total reward: {reward:.2f}")
            return reward
        except Exception as e:
            print(f"Warning: Error calculating reward: {e}")
            return 0.0  # Neutral reward on error instead of negative
    
    def _is_game_over(self):
        """
        Check if the game is over using the game_over() method from PyBoy's game wrapper.
        
        Based on user testing, this method is the most reliable way to detect game over.
        """
        if self.frame_count < 300:
            return False
            
        if self.tetris is not None:
            try:
                if self.tetris.game_over():
                    print("[GAME_OVER] Detected via PyBoy's game_over() method")
                    if self.render_mode == "human" and self.pyboy is not None:
                        self._save_game_over_screenshot()
                    return True
            except NotImplementedError:
                if self.frame_count == 300:
                    print("Warning: game_over() method not implemented in game wrapper")
            except Exception as e:
                print(f"Warning: Error calling game_over method: {e}")
                
        return False
        
    def _save_game_over_screenshot(self):
        """Save a screenshot when game over is detected for debugging."""
        try:
            os.makedirs("game_over_screenshots", exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"game_over_screenshots/game_over_{timestamp}_frame{self.frame_count}.png"
            
            screen = self.pyboy.screen
            if hasattr(screen, 'image'):
                img_func = screen.image
                if callable(img_func):
                    img = img_func()
                else:
                    img = img_func
                img.save(filename)
                print(f"Game over screenshot saved to {filename}")
            else:
                print("Failed to save game over screenshot: screen.image not available")
        except Exception as e:
            print(f"Failed to save game over screenshot: {e}")
    
    def _is_piece_locked(self):
        """Check if the current piece has locked in place."""
        try:
            print("[PIECE_LOCK] Checking if piece is locked...")
            board_before = self._get_observation()['board'].copy()
            board_sum_before = np.sum(board_before)
            print(f"[PIECE_LOCK] Board state before: {board_sum_before} filled cells")
            
            print("[PIECE_LOCK] Sending down input to test piece movement")
            self.pyboy.send_input(WindowEvent.PRESS_ARROW_DOWN)
            self.pyboy.tick()
            self.pyboy.send_input(WindowEvent.RELEASE_ARROW_DOWN)
            
            print("[PIECE_LOCK] Waiting for game to process movement")
            for i in range(3):
                self.pyboy.tick()
                print(f"[PIECE_LOCK] Tick {i+1}/3")
            
            board_after = self._get_observation()['board'].copy()
            board_sum_after = np.sum(board_after)
            print(f"[PIECE_LOCK] Board state after: {board_sum_after} filled cells")
            
            is_locked = np.array_equal(board_before, board_after)
            print(f"[PIECE_LOCK] Piece locked: {is_locked}")
            
            if board_sum_after > board_sum_before:
                print("[PIECE_LOCK] Board has more filled cells, piece likely merged with board")
                return True
                
            return is_locked
        except Exception as e:
            print(f"[PIECE_LOCK] Error checking if piece is locked: {e}")
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
        
        if self.turn_based and np.random.random() < 0.3:  # 30% chance of random action
            original_action = action
            action = np.random.randint(0, self.action_space.n)
            print(f"[EXPLORATION] Replacing action {original_action} with random action {action}")
        
        action_name = "None" if action == 6 else str(self.ACTIONS[action]).split('.')[-1]
        print(f"Frame {self.frame_count}: Taking action {action_name}")
        
        if self.turn_based:
            print(f"[TURN-BASED] Starting new piece placement with action: {action_name}")
            
        if self.ACTIONS[action] is not None:
            print(f"[ACTION] Sending input: {action_name}")
            self.pyboy.send_input(self.ACTIONS[action])
            self.pyboy.tick()
            self.pyboy.send_input(self.RELEASE_ACTIONS[action])
            self.frame_count += 1
            
            if self.frame_delay > 0:
                import time
                time.sleep(self.frame_delay)
                print(f"[DELAY] Applied {self.frame_delay}s delay after action")
        else:
            print("[ACTION] No input sent (None action)")
        
        if self.turn_based:
            piece_locked = False
            max_frames_per_piece = 100  # Safety limit to prevent infinite loops
            frames_since_action = 0
            
            print("[TURN-BASED] Waiting for piece to lock...")
            while not piece_locked and frames_since_action < max_frames_per_piece:
                for _ in range(3):
                    self.pyboy.tick()
                    self.frame_count += 1
                
                frames_since_action += 3
                
                if frames_since_action % 15 == 0:
                    print(f"[TURN-BASED] Waited {frames_since_action} frames, checking if piece locked...")
                
                piece_locked = self._is_piece_locked()
                
                if frames_since_action > 50 and frames_since_action % 10 == 0:
                    print("[TURN-BASED] Piece taking too long, sending down input to accelerate")
                    self.pyboy.send_input(WindowEvent.PRESS_ARROW_DOWN)
                    self.pyboy.tick()
                    self.pyboy.send_input(WindowEvent.RELEASE_ARROW_DOWN)
                    self.frame_count += 1
            
            if piece_locked:
                print(f"[TURN-BASED] Piece locked successfully after {frames_since_action} frames")
            else:
                print(f"[TURN-BASED] Piece lock timeout after {frames_since_action} frames")
        else:
            frames_to_advance = 4  # Total will be 5 frames including the action frame
            
            print(f"[CONTINUOUS] Advancing {frames_to_advance} more frames (total 5 with action)")
            for i in range(frames_to_advance):
                self.pyboy.tick()
                self.frame_count += 1
                
                if self.frame_delay > 0:
                    import time
                    time.sleep(self.frame_delay / frames_to_advance)
            
            is_locked = self._is_piece_locked()
            if is_locked:
                print("[CONTINUOUS] Piece has locked in place after advancing frames")
                placement_reward = 0.5
                self.piece_locked = True  # Set flag for reward calculation
        
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
            print("[TURN-BASED] Activating turn-based mode")
            self.pyboy.set_emulation_speed(self.emulation_speed)
            print(f"[TURN-BASED] Emulation speed set to {self.emulation_speed}")
        else:
            print("[CONTINUOUS] Using continuous mode")
            speed = self.emulation_speed if self.emulation_speed > 0 else 4
            self.pyboy.set_emulation_speed(speed)
            print(f"[CONTINUOUS] Emulation speed set to {speed}")
        
        if not self.pyboy.cartridge_title or "TETRIS" not in self.pyboy.cartridge_title.upper():
            print(f"Warning: ROM title '{self.pyboy.cartridge_title}' may not be Tetris, but continuing anyway")
        
        self.tetris = self.pyboy.game_wrapper
        
        print("[INIT] Starting game and skipping loading screens...")
        print(f"[INIT] ROM title: {self.pyboy.cartridge_title}")
        
        is_tetris_dx = self.pyboy.cartridge_title and "DX" in self.pyboy.cartridge_title.upper()
        
        if is_tetris_dx:
            print("[INIT] Detected Tetris DX (Game Boy Color ROM)")
            
            self.tetris.start_game(timer_div=0x00)
            print("[INIT] Called start_game(timer_div=0x00)")
            
            print("[INIT] Advancing 150 frames...")
            for i in range(150):
                self.pyboy.tick()
                if i % 30 == 0:
                    print(f"[INIT] Advanced {i} frames")
            
            for j in range(3):
                print(f"[INIT] Pressing START button (attempt {j+1})...")
                self.pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
                self.pyboy.tick()
                self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
                
                print(f"[INIT] Advancing 60 frames after START button {j+1}...")
                for i in range(60):
                    self.pyboy.tick()
                    if i % 20 == 0:
                        print(f"[INIT] Advanced {i} more frames")
            
            print("[INIT] Pressing A button to select game type...")
            self.pyboy.send_input(WindowEvent.PRESS_BUTTON_A)
            self.pyboy.tick()
            self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)
            
            print("[INIT] Advancing 90 final frames...")
            for i in range(90):
                self.pyboy.tick()
                if i % 30 == 0:
                    print(f"[INIT] Advanced {i} final frames")
        else:
            self.tetris.start_game(timer_div=0x00)
            print("[INIT] Called start_game(timer_div=0x00)")
            
            print("[INIT] Advancing 120 frames...")
            for i in range(120):
                self.pyboy.tick()
                if i % 30 == 0:
                    print(f"[INIT] Advanced {i} frames")
            
            print("[INIT] Pressing START button...")
            self.pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
            self.pyboy.tick()
            self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
            
            print("[INIT] Advancing 60 frames...")
            for i in range(60):
                self.pyboy.tick()
                if i % 20 == 0:
                    print(f"[INIT] Advanced {i} more frames")
            
            print("[INIT] Pressing START button again...")
            self.pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
            self.pyboy.tick()
            self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
            
            print("[INIT] Advancing 30 frames...")
            for i in range(30):
                self.pyboy.tick()
            
            print("[INIT] Pressing A button to select game type...")
            self.pyboy.send_input(WindowEvent.PRESS_BUTTON_A)
            self.pyboy.tick()
            self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)
            
            print("[INIT] Advancing 60 final frames...")
            for i in range(60):
                self.pyboy.tick()
                if i % 20 == 0:
                    print(f"[INIT] Advanced {i} final frames")
        
        print("[INIT] Game initialized and ready to play")
        
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
