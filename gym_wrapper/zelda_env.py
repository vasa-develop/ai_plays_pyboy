import gymnasium as gym
from gymnasium import spaces
import numpy as np
import os
import logging
from pyboy import PyBoy
from pyboy.utils import WindowEvent

class ZeldaPyBoyEnv(gym.Env):
    """
    PyBoy Zelda: Link's Awakening environment that follows the Gymnasium interface.
    This environment provides a standardized way to train reinforcement learning
    agents to play Zelda on the Game Boy emulator.
    """
    metadata = {'render_modes': ['human']}
    
    ACTIONS = [
        WindowEvent.PRESS_ARROW_UP,     # Move up
        WindowEvent.PRESS_ARROW_RIGHT,  # Move right
        WindowEvent.PRESS_ARROW_LEFT,   # Move left
        WindowEvent.PRESS_ARROW_DOWN,   # Move down
        WindowEvent.PRESS_BUTTON_A,     # A button (action/interact)
        WindowEvent.PRESS_BUTTON_B,     # B button (sword/cancel)
        WindowEvent.PRESS_BUTTON_START, # Start button (menu)
        WindowEvent.PRESS_BUTTON_SELECT,# Select button (item swap)
        None,                           # No action
    ]
    
    RELEASE_ACTIONS = [
        WindowEvent.RELEASE_ARROW_UP,
        WindowEvent.RELEASE_ARROW_RIGHT,
        WindowEvent.RELEASE_ARROW_LEFT,
        WindowEvent.RELEASE_ARROW_DOWN,
        WindowEvent.RELEASE_BUTTON_A,
        WindowEvent.RELEASE_BUTTON_B,
        WindowEvent.RELEASE_BUTTON_START,
        WindowEvent.RELEASE_BUTTON_SELECT,
        None,
    ]
    
    def __init__(self, rom_path="zelda.gb", render_mode="human", save_state_path=None):
        super(ZeldaPyBoyEnv, self).__init__()
        
        self.rom_path = rom_path
        self.render_mode = render_mode
        self.save_state_path = save_state_path
        self.pyboy = None
        self.frame_count = 0
        self.max_frames_per_episode = 100000  # Limit episode length
        
        self.prev_health = 0
        self.prev_rupees = 0
        self.prev_items = set()
        self.prev_position = (0, 0)
        self.prev_map_position = (0, 0)
        self.prev_enemies_defeated = 0
        
        self.action_space = spaces.Discrete(len(self.ACTIONS))
        
        self.observation_space = spaces.Dict({
            'screen': spaces.Box(low=0, high=255, shape=(144, 160, 3), dtype=np.uint8),
            'health': spaces.Box(low=0, high=14, shape=(1,), dtype=np.int8),
            'position': spaces.Box(low=0, high=255, shape=(2,), dtype=np.uint8),  # Changed to uint8
            'map_position': spaces.Box(low=0, high=15, shape=(2,), dtype=np.int8),
            'rupees': spaces.Box(low=0, high=999, shape=(1,), dtype=np.int16),
            'inventory': spaces.MultiBinary(20),  # Simplified representation of inventory
        })
        
    def _get_observation(self):
        """Extract the current game state as an observation."""
        screen = self._get_screen_buffer()
        
        health = self._get_health()
        position = self._get_player_position()
        map_position = self._get_map_position()
        rupees = self._get_rupees()
        items = self._get_items()
        
        return {
            'screen': screen,
            'health': np.array([health], dtype=np.int8),
            'position': np.array(position, dtype=np.int8),
            'map_position': np.array(map_position, dtype=np.int8),
            'rupees': np.array([rupees], dtype=np.int16),
            'inventory': items,
        }
    
    def _get_screen_buffer(self):
        """Get the screen buffer as a numpy array."""
        screen = np.zeros((144, 160, 3), dtype=np.uint8)
        return screen
    
    def _get_health(self):
        """Get Link's current health."""
        health = 3  # Default starting health
        return health
    
    def _get_player_position(self):
        """Get Link's current position on the screen."""
        position = (80, 80)  # Center of screen
        return position
    
    def _get_map_position(self):
        """Get the current map/room position."""
        map_position = (8, 8)  # Default starting map position
        return map_position
    
    def _get_rupees(self):
        """Get the current rupee count."""
        rupees = 0
        return rupees
    
    def _get_items(self):
        """Get the current inventory items as a binary array."""
        items = np.zeros(20, dtype=np.int8)
        return items
    
    def _calculate_reward(self):
        """Calculate the reward based on game progress."""
        health = self._get_health()
        rupees = self._get_rupees()
        position = self._get_player_position()
        map_position = self._get_map_position()
        items = self._get_items()
        enemies_defeated = self._get_enemies_defeated()
        
        reward = 0
        
        health_diff = health - self.prev_health
        if health_diff > 0:
            reward += 1.0 * health_diff  # Reward for gaining health
        elif health_diff < 0:
            reward -= 0.5 * abs(health_diff)  # Penalty for losing health
        
        rupee_diff = rupees - self.prev_rupees
        if rupee_diff > 0:
            reward += 0.1 * rupee_diff
        
        current_items = set(np.where(items == 1)[0])
        new_items = current_items - self.prev_items
        if new_items:
            reward += 5.0 * len(new_items)
        
        enemies_diff = enemies_defeated - self.prev_enemies_defeated
        if enemies_diff > 0:
            reward += 2.0 * enemies_diff
        
        if map_position != self.prev_map_position:
            reward += 3.0
        
        if position != self.prev_position:
            reward += 0.01
        
        reward -= 0.001
        
        self.prev_health = health
        self.prev_rupees = rupees
        self.prev_items = current_items
        self.prev_position = position
        self.prev_map_position = map_position
        self.prev_enemies_defeated = enemies_defeated
        
        return reward
    
    def _get_enemies_defeated(self):
        """Get the number of enemies defeated in the current room."""
        return 0
    
    def _is_game_over(self):
        """Check if the game is over (Link has died)."""
        health = self._get_health()
        return health <= 0
    
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
            'health': observation['health'][0],
            'rupees': observation['rupees'][0],
            'position': observation['position'],
            'map_position': observation['map_position'],
            'frame_count': self.frame_count
        }
        
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
        
        if self.pyboy.cartridge_title != "ZELDA":
            self.pyboy.stop()
            raise ValueError("The provided ROM is not Zelda: Link's Awakening")
        
        if self.save_state_path and os.path.exists(self.save_state_path):
            try:
                with open(self.save_state_path, "rb") as file:
                    self.pyboy.load_state(file)
                logging.info(f"Loaded game state from {self.save_state_path}")
            except Exception as e:
                logging.warning(f"Failed to load save state: {e}. Falling back to title screen skip.")
                self._skip_title_screen()
        else:
            self._skip_title_screen()
            
            if self.save_state_path:
                try:
                    os.makedirs(os.path.dirname(os.path.abspath(self.save_state_path)), exist_ok=True)
                    with open(self.save_state_path, "wb") as file:
                        self.pyboy.save_state(file)
                    logging.info(f"Saved game state to {self.save_state_path}")
                except Exception as e:
                    logging.warning(f"Failed to save state: {e}")
        
        self.frame_count = 0
        self.prev_health = self._get_health()
        self.prev_rupees = self._get_rupees()
        self.prev_items = set(np.where(self._get_items() == 1)[0])
        self.prev_position = self._get_player_position()
        self.prev_map_position = self._get_map_position()
        self.prev_enemies_defeated = self._get_enemies_defeated()
        
        observation = self._get_observation()
        
        info = {
            'health': observation['health'][0],
            'rupees': observation['rupees'][0],
            'position': observation['position'],
            'map_position': observation['map_position'],
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
    
    def _skip_title_screen(self):
        """
        Skip the title screen by pressing the START button twice.
        This is used as a fallback when save state loading fails or isn't available.
        """
        logging.info("Skipping title screen manually...")
        
        for _ in range(60):
            self.pyboy.tick()
        
        self.pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        self.pyboy.tick()
        self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
        
        for _ in range(60):
            self.pyboy.tick()
        
        self.pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        self.pyboy.tick()
        self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
        
        for _ in range(60):
            self.pyboy.tick()
    
    def update_save_state_path(self, save_state_path):
        """
        Update the save state path after environment creation.
        
        Args:
            save_state_path: Path to the save state file
        """
        self.save_state_path = save_state_path
        logging.info(f"Updated save state path to: {save_state_path}")
        return True
    
    def close(self):
        """Clean up resources."""
        if self.pyboy is not None:
            self.pyboy.stop()
            self.pyboy = None
