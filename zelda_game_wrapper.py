from pyboy.utils import WindowEvent
import memory_map_zelda as mem

class ZeldaGameWrapper:
    """Game wrapper for Zelda: Link's Awakening using official RAM map."""
    
    def __init__(self, pyboy):
        self.pyboy = pyboy
        self.game_area_height = 144  # Screen height
        self.game_area_width = 160   # Screen width
        self.last_direction_key = None  # Track last direction key pressed
        
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
        """Get Link's facing direction using official memory address.
        
        Returns:
            int: Direction constant (0=UP, 1=RIGHT, 2=DOWN, 3=LEFT)
        """
        return self.pyboy.memory[mem.LINK_DIRECTION]
    
    def get_player_direction_name(self):
        """Get Link's facing direction as a string."""
        direction = self.get_player_direction()
        
        if direction == mem.DIRECTION_UP:
            return "UP"
        elif direction == mem.DIRECTION_RIGHT:
            return "RIGHT"
        elif direction == mem.DIRECTION_DOWN:
            return "DOWN"
        elif direction == mem.DIRECTION_LEFT:
            return "LEFT"
        else:
            return "UNKNOWN"
    
    def get_player_animation_state(self):
        """Get Link's animation state."""
        return self.pyboy.memory[mem.LINK_ANIMATION_STATE]
    
    def get_rupees(self):
        """Get Link's rupee count."""
        low_byte = self.pyboy.memory[mem.LINK_RUPEES]
        high_byte = self.pyboy.memory[mem.LINK_RUPEES_HIGH]
        return (high_byte << 8) + low_byte
    
    def get_items(self):
        """Get Link's inventory items."""
        return {
            "sword_level": self.pyboy.memory[mem.LINK_SWORD_LEVEL],
            "shield_level": self.pyboy.memory[mem.LINK_SHIELD_LEVEL],
            "bombs": self.pyboy.memory[mem.LINK_BOMBS],
            "arrows": self.pyboy.memory[mem.LINK_ARROWS],
            "magic_powder": self.pyboy.memory[mem.LINK_MAGIC_POWDER],
            "selected_item_a": self.pyboy.memory[mem.LINK_SELECTED_ITEM_A],
            "selected_item_b": self.pyboy.memory[mem.LINK_SELECTED_ITEM_B]
        }
    
    def get_game_state(self):
        """Get current game state."""
        return {
            "state": self.pyboy.memory[mem.GAME_STATE],
            "substate": self.pyboy.memory[mem.GAME_SUBSTATE],
            "room_id": self.pyboy.memory[mem.GAME_ROOM_ID],
            "dungeon_id": self.pyboy.memory[mem.GAME_DUNGEON_ID]
        }
    
    def get_enemy_states(self):
        """Get states of enemies on screen."""
        enemies = []
        enemy_count = self.pyboy.memory[mem.ENEMY_COUNT]
        
        for i in range(min(enemy_count, 5)):  # Limit to 5 enemies
            base_addr = mem.ENEMY_STATE_START + (i * 16)  # 16 bytes per enemy
            enemy_type = self.pyboy.memory[base_addr + (mem.ENEMY_TYPE - mem.ENEMY_STATE_START)]
            
            if enemy_type != 0:
                enemy = {
                    'type': enemy_type,
                    'health': self.pyboy.memory[base_addr + (mem.ENEMY_HEALTH - mem.ENEMY_STATE_START)],
                    'x': self.pyboy.memory[base_addr + (mem.ENEMY_POSITION_X - mem.ENEMY_STATE_START)],
                    'y': self.pyboy.memory[base_addr + (mem.ENEMY_POSITION_Y - mem.ENEMY_STATE_START)]
                }
                enemies.append(enemy)
        
        return enemies
    
    def get_game_progress(self):
        """Get current game progress flags."""
        progress_flags = []
        for i in range(16):  # Read 16 bytes of progress flags
            progress_flags.append(self.pyboy.memory[mem.GAME_PROGRESS_FLAGS + i])
        return progress_flags
    
    def move_player(self, direction, steps=1, delay_frames=10):
        """Move the player in the specified direction with delay.
        
        In Zelda: Link's Awakening, the first key press changes Link's facing direction,
        and subsequent presses in the same direction actually move the character.
        
        Args:
            direction: Direction to move ('up', 'down', 'left', 'right')
            steps: Number of steps to move in that direction
            delay_frames: Number of frames to wait between key presses
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
            self.last_direction_key = direction
            
            current_direction = self.get_player_direction()
            target_direction = direction_values[direction]
            
            if current_direction != target_direction:
                self.pyboy.send_input(button_mapping[direction])
                
                for _ in range(delay_frames):
                    self.pyboy.tick()
                
                self.pyboy.send_input(release_mapping[direction])
                
                for _ in range(delay_frames):
                    self.pyboy.tick()
            
            for _ in range(steps):
                self.pyboy.send_input(button_mapping[direction])
                
                for _ in range(delay_frames):
                    self.pyboy.tick()
                
                self.pyboy.send_input(release_mapping[direction])
                
                for _ in range(delay_frames):
                    self.pyboy.tick()
    
    def press_button(self, button, hold_frames=10):
        """Press a game button with configurable hold duration."""
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
            
            for _ in range(5):
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
               f"Direction: {self.get_player_direction_name()}\n" \
               f"Enemies: {len(self.get_enemy_states())}"
