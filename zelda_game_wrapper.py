from pyboy.utils import WindowEvent
import memory_map_zelda as mem

class ZeldaGameWrapper:
    """Game wrapper for Zelda: Link's Awakening."""
    
    def __init__(self, pyboy):
        self.pyboy = pyboy
        self.game_area_height = 144  # Screen height
        self.game_area_width = 160   # Screen width
        
        if self.pyboy.cartridge_title != "ZELDA":
            raise ValueError("This wrapper is for Zelda: Link's Awakening only")
    
    def get_health(self):
        """Get Link's current health."""
        return self.pyboy.memory[mem.LINK_HEALTH]
    
    def get_max_health(self):
        """Get Link's maximum health."""
        return self.pyboy.memory[mem.LINK_MAX_HEALTH]
    
    def get_player_position(self):
        """Get Link's current position on the screen."""
        x = self.pyboy.memory[mem.LINK_X_POS]
        y = self.pyboy.memory[mem.LINK_Y_POS]
        return (x, y)
    
    def get_player_direction(self):
        """Get Link's facing direction.
        
        Returns:
            int: Direction constant (0=UP, 1=RIGHT, 2=DOWN, 3=LEFT)
        """
        direction_flags = self.pyboy.memory[mem.LINK_DIRECTION_FLAGS]
        
        if direction_flags == 0:
            sprite_x = self.pyboy.memory[mem.LINK_SPRITE_X]
            sprite_y = self.pyboy.memory[mem.LINK_SPRITE_Y]
            
            if sprite_x % 2 == 0:
                return mem.DIRECTION_UP
            else:
                return mem.DIRECTION_LEFT
        else:
            sprite_x = self.pyboy.memory[mem.LINK_SPRITE_X]
            sprite_y = self.pyboy.memory[mem.LINK_SPRITE_Y]
            
            if sprite_y % 2 == 0:
                return mem.DIRECTION_RIGHT
            else:
                return mem.DIRECTION_DOWN
    
    def get_enemy_states(self):
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
    
    def get_game_progress(self):
        """Get current game progress."""
        return self.pyboy.memory[mem.GAME_PROGRESS]
    
    def move_player(self, direction, steps=1):
        """Move the player in the specified direction.
        
        In Zelda: Link's Awakening, the first key press changes Link's facing direction,
        and subsequent presses in the same direction actually move the character.
        
        Args:
            direction: Direction to move ('up', 'down', 'left', 'right')
            steps: Number of steps to move in that direction
        """
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
        
        direction_values = {
            'up': mem.DIRECTION_UP,
            'down': mem.DIRECTION_DOWN,
            'left': mem.DIRECTION_LEFT,
            'right': mem.DIRECTION_RIGHT
        }
        
        if direction in button_mapping:
            current_direction = self.get_player_direction()
            target_direction = direction_values[direction]
            
            if current_direction != target_direction:
                self.pyboy.send_input(button_mapping[direction])
                self.pyboy.tick()
                self.pyboy.send_input(release_mapping[direction])
                self.pyboy.tick()
            
            for _ in range(steps):
                self.pyboy.send_input(button_mapping[direction])
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
    
    def is_zelda(self):
        """Check if this wrapper is being used with a Zelda ROM."""
        return self.pyboy.cartridge_title == "ZELDA"
    
    def __str__(self):
        return f"Zelda Link's Awakening:\n" \
               f"Health: {self.get_health()}/{self.get_max_health()}\n" \
               f"Position: {self.get_player_position()}\n" \
               f"Direction: {self.get_player_direction()}\n" \
               f"Enemies: {len(self.get_enemy_states())}"
