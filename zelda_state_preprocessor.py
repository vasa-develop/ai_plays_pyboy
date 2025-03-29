import numpy as np
from pyboy import PyBoy

class ZeldaStatePreprocessor:
    """
    Preprocesses the Zelda game state for use with reinforcement learning algorithms.
    Extracts relevant features from the game state and converts them into a format
    suitable for neural networks.
    """
    
    def __init__(self, pyboy_instance=None):
        """
        Initialize the state preprocessor.
        
        Args:
            pyboy_instance: An instance of PyBoy running Zelda
        """
        self.pyboy = pyboy_instance
        
        self.ADDR_HEALTH = 0xDB5D        # Player's health
        self.ADDR_MAX_HEALTH = 0xDB5E    # Player's maximum health
        self.ADDR_RUPEES = 0xDB8C        # Player's rupee count
        self.ADDR_PLAYER_X = 0xD362      # Player's X position on screen
        self.ADDR_PLAYER_Y = 0xD363      # Player's Y position on screen
        self.ADDR_MAP_X = 0xD35E         # Current map X position
        self.ADDR_MAP_Y = 0xD35F         # Current map Y position
        self.ADDR_ROOM_STATE = 0xD800    # Room state (enemies, etc.)
        self.ADDR_INVENTORY_START = 0xDB00  # Start of inventory data
        
    def set_pyboy(self, pyboy_instance):
        """Set the PyBoy instance to use for state extraction."""
        self.pyboy = pyboy_instance
    
    def get_memory_value(self, address):
        """
        Get a value from the Game Boy's memory.
        
        Args:
            address: Memory address to read
            
        Returns:
            Value at the specified address
        """
        if self.pyboy is None:
            return 0
        
        try:
            return self.pyboy.get_memory_value(address)
        except Exception as e:
            print(f"Error reading memory at address {hex(address)}: {str(e)}")
            return 0
    
    def get_screen_state(self):
        """
        Get the current screen state as a normalized array.
        
        Returns:
            Normalized screen state as a numpy array
        """
        if self.pyboy is None:
            return np.zeros((144, 160, 3), dtype=np.float32)
        
        try:
            screen = np.zeros((144, 160, 3), dtype=np.uint8)
            
            return screen.astype(np.float32) / 255.0
        except Exception as e:
            print(f"Error getting screen state: {str(e)}")
            return np.zeros((144, 160, 3), dtype=np.float32)
    
    def get_health(self):
        """
        Get Link's current health.
        
        Returns:
            Current health as a float between 0 and 1
        """
        health = self.get_memory_value(self.ADDR_HEALTH)
        max_health = self.get_memory_value(self.ADDR_MAX_HEALTH)
        
        if max_health == 0:
            return 0.0
        
        return health / max_health
    
    def get_player_position(self):
        """
        Get Link's current position on the screen.
        
        Returns:
            Normalized position as (x, y) where each is between 0 and 1
        """
        x = self.get_memory_value(self.ADDR_PLAYER_X)
        y = self.get_memory_value(self.ADDR_PLAYER_Y)
        
        return x / 255.0, y / 255.0
    
    def get_map_position(self):
        """
        Get the current map/room position.
        
        Returns:
            Map position as (x, y)
        """
        x = self.get_memory_value(self.ADDR_MAP_X)
        y = self.get_memory_value(self.ADDR_MAP_Y)
        
        return x, y
    
    def get_rupees(self):
        """
        Get the current rupee count.
        
        Returns:
            Normalized rupee count between 0 and 1 (assuming max of 999)
        """
        rupees = self.get_memory_value(self.ADDR_RUPEES)
        
        return rupees / 999.0
    
    def get_inventory(self):
        """
        Get the current inventory as a binary array.
        
        Returns:
            Binary array representing inventory items
        """
        inventory = np.zeros(20, dtype=np.int8)
        
        
        return inventory
    
    def get_enemies(self):
        """
        Get information about enemies in the current room.
        
        Returns:
            Array of enemy positions and types
        """
        
        return np.zeros((5, 3), dtype=np.float32)  # Up to 5 enemies, each with (x, y, type)
    
    def get_state_vector(self):
        """
        Get a vector representation of the game state for use with RL algorithms.
        
        Returns:
            State vector as a numpy array
        """
        health = self.get_health()
        player_x, player_y = self.get_player_position()
        map_x, map_y = self.get_map_position()
        rupees = self.get_rupees()
        inventory = self.get_inventory()
        
        state_vector = np.concatenate([
            [health],
            [player_x, player_y],
            [map_x / 16.0, map_y / 16.0],  # Normalize map position
            [rupees],
            inventory
        ])
        
        return state_vector
    
    def get_cnn_state(self):
        """
        Get a state representation suitable for CNN-based RL algorithms.
        
        Returns:
            Dictionary of state components
        """
        return {
            'screen': self.get_screen_state(),
            'vector': self.get_state_vector()
        }
    
    def detect_game_over(self):
        """
        Detect if the game is over (Link has died).
        
        Returns:
            True if game is over, False otherwise
        """
        health = self.get_memory_value(self.ADDR_HEALTH)
        return health <= 0
    
    def detect_progress(self, previous_state=None):
        """
        Detect progress in the game compared to a previous state.
        
        Args:
            previous_state: Previous state to compare with
            
        Returns:
            Dictionary of progress indicators
        """
        if previous_state is None:
            return {
                'health_change': 0,
                'rupee_change': 0,
                'position_change': 0,
                'map_change': False,
                'inventory_change': 0
            }
        
        current_health = self.get_health()
        current_rupees = self.get_rupees()
        current_player_pos = self.get_player_position()
        current_map_pos = self.get_map_position()
        current_inventory = self.get_inventory()
        
        prev_health = previous_state.get('health', 0)
        prev_rupees = previous_state.get('rupees', 0)
        prev_player_pos = previous_state.get('player_position', (0, 0))
        prev_map_pos = previous_state.get('map_position', (0, 0))
        prev_inventory = previous_state.get('inventory', np.zeros_like(current_inventory))
        
        health_change = current_health - prev_health
        rupee_change = current_rupees - prev_rupees
        
        position_change = np.sqrt(
            (current_player_pos[0] - prev_player_pos[0])**2 +
            (current_player_pos[1] - prev_player_pos[1])**2
        )
        
        map_change = current_map_pos != prev_map_pos
        
        inventory_change = np.sum((current_inventory - prev_inventory) > 0)
        
        return {
            'health_change': health_change,
            'rupee_change': rupee_change,
            'position_change': position_change,
            'map_change': map_change,
            'inventory_change': inventory_change
        }
