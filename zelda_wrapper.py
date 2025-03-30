from pyboy.utils import WindowEvent
from pyboy.plugins.base_plugin import PyBoyGameWrapper, PyBoyPlugin
import memory_map_zelda as mem

class ZeldaGameWrapper(PyBoyGameWrapper):
    """Game wrapper for Zelda: Link's Awakening."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_area_height = 144  # Screen height
        self.game_area_width = 160   # Screen width
    
    def _get_health(self):
        """Get Link's current health."""
        return self.pyboy.memory[mem.LINK_HEALTH]
    
    def _get_max_health(self):
        """Get Link's maximum health."""
        return self.pyboy.memory[mem.LINK_MAX_HEALTH]
    
    def _get_player_position(self):
        """Get Link's current position on the screen."""
        x = self.pyboy.memory[mem.LINK_X_POS]
        y = self.pyboy.memory[mem.LINK_Y_POS]
        return (x, y)
    
    def _get_player_direction(self):
        """Get Link's facing direction."""
        return self.pyboy.memory[mem.LINK_DIRECTION]
    
    def _get_enemy_states(self):
        """Get states of enemies on screen."""
        enemies = []
        for i in range(5):
            base_addr = mem.ENEMY_STATE_START + (i * 16)  # Assuming 16 bytes per enemy
            enemy_type = self.pyboy.memory[base_addr + 1]  # ENEMY_TYPE offset
            
            if enemy_type != 0:
                enemy = {
                    'type': enemy_type,
                    'behavior': self.pyboy.memory[base_addr + 2],  # ENEMY_BEHAVIOR offset
                    'x': self.pyboy.memory[base_addr + 7],         # ENEMY_POSITION_X offset
                    'y': self.pyboy.memory[base_addr + 8],         # ENEMY_POSITION_Y offset
                    'state': self.pyboy.memory[base_addr + 9]      # ENEMY_STATE offset
                }
                enemies.append(enemy)
        
        return enemies
    
    def _get_game_progress(self):
        """Get current game progress."""
        return self.pyboy.memory[mem.GAME_PROGRESS]
    
    def move_player(self, direction, steps=1):
        """Move the player in the specified direction."""
        button_mapping = {
            'up': WindowEvent.PRESS_ARROW_UP,
            'down': WindowEvent.PRESS_ARROW_DOWN,
            'left': WindowEvent.PRESS_ARROW_LEFT,
            'right': WindowEvent.PRESS_ARROW_RIGHT
        }
        
        release_mapping = {
            'up': WindowEvent.RELEASE_ARROW_UP,
            'down': WindowEvent.RELEASE_ARROW_DOWN,
            'left': WindowEvent.RELEASE_ARROW_LEFT,
            'right': WindowEvent.RELEASE_ARROW_RIGHT
        }
        
        if direction in button_mapping:
            self.pyboy.send_input(button_mapping[direction])
            
            for _ in range(steps):
                self.pyboy.tick()
            
            self.pyboy.send_input(release_mapping[direction])
            self.pyboy.tick()
    
    def press_button(self, button, hold_frames=1):
        """Press a game button."""
        button_mapping = {
            'a': WindowEvent.PRESS_BUTTON_A,
            'b': WindowEvent.PRESS_BUTTON_B,
            'start': WindowEvent.PRESS_BUTTON_START,
            'select': WindowEvent.PRESS_BUTTON_SELECT
        }
        
        release_mapping = {
            'a': WindowEvent.RELEASE_BUTTON_A,
            'b': WindowEvent.RELEASE_BUTTON_B,
            'start': WindowEvent.RELEASE_BUTTON_START,
            'select': WindowEvent.RELEASE_BUTTON_SELECT
        }
        
        if button in button_mapping:
            self.pyboy.send_input(button_mapping[button])
            
            for _ in range(hold_frames):
                self.pyboy.tick()
            
            self.pyboy.send_input(release_mapping[button])
            self.pyboy.tick()
    
    def game_area(self):
        """Get the game area."""
        return (0, 0, self.game_area_width, self.game_area_height)
    
    def start_game(self):
        """Start the game by skipping the title screen."""
        for _ in range(100):
            self.pyboy.tick()
        
        self.press_button('start')
        
        for _ in range(50):
            self.pyboy.tick()
