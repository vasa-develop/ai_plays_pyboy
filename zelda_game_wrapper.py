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
        """Get Link's current position on the screen.
        
        Uses the reverse-engineered memory addresses that have been verified to work.
        The official RAM map doesn't explicitly list Link's X/Y coordinates.
        """
        x = self.pyboy.memory[mem.LINK_X_POS_OLD]
        y = self.pyboy.memory[mem.LINK_Y_POS_OLD]
        return (x, y)
    
    def get_destination_position(self):
        """Get the destination X/Y coordinates when changing rooms/areas."""
        x = self.pyboy.memory[mem.DEST_X_POS]
        y = self.pyboy.memory[mem.DEST_Y_POS]
        return (x, y)
    
    def get_dungeon_position(self):
        """Get Link's position on the 8x8 dungeon grid."""
        return self.pyboy.memory[mem.DUNGEON_POS]
    
    def get_player_direction(self):
        """Get Link's facing direction using reverse-engineered memory address.
        
        Returns:
            int: Direction constant (0=UP, 1=RIGHT, 2=DOWN, 3=LEFT)
        """
        return self.pyboy.memory[mem.LINK_DIRECTION_OLD]
    
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
    
    def get_held_items(self):
        """Get Link's currently held items (A and B buttons)."""
        item_a = self.pyboy.memory[mem.HELD_ITEM_A]
        item_b = self.pyboy.memory[mem.HELD_ITEM_B]
        
        item_names = {
            mem.ITEM_SWORD: "Sword",
            mem.ITEM_BOMBS: "Bombs",
            mem.ITEM_POWER_BRACELET: "Power Bracelet",
            mem.ITEM_SHIELD: "Shield",
            mem.ITEM_BOW: "Bow",
            mem.ITEM_HOOKSHOT: "Hookshot",
            mem.ITEM_FIRE_ROD: "Fire Rod",
            mem.ITEM_PEGASUS_BOOTS: "Pegasus Boots",
            mem.ITEM_OCARINA: "Ocarina",
            mem.ITEM_FEATHER: "Feather",
            mem.ITEM_SHOVEL: "Shovel",
            mem.ITEM_MAGIC_POWDER: "Magic Powder",
            mem.ITEM_BOOMERANG: "Boomerang"
        }
        
        item_a_name = item_names.get(item_a, f"Unknown ({item_a})")
        item_b_name = item_names.get(item_b, f"Unknown ({item_b})")
        
        return {
            "item_a": item_a,
            "item_a_name": item_a_name,
            "item_b": item_b,
            "item_b_name": item_b_name
        }
    
    def get_rupees(self):
        """Get Link's rupee count."""
        low_byte = self.pyboy.memory[mem.RUPEES_LOW]
        high_byte = self.pyboy.memory[mem.RUPEES_HIGH]
        return (high_byte << 8) + low_byte
    
    def get_items(self):
        """Get Link's inventory items."""
        return {
            "sword_level": self.pyboy.memory[mem.SWORD_LEVEL],
            "shield_level": self.pyboy.memory[mem.SHIELD_LEVEL],
            "bombs": self.pyboy.memory[mem.BOMBS],
            "arrows": self.pyboy.memory[mem.ARROWS],
            "magic_powder": self.pyboy.memory[mem.MAGIC_POWDER],
            "flippers": self.pyboy.memory[mem.FLIPPERS],
            "potion": self.pyboy.memory[mem.POTION],
            "trading_item": self.pyboy.memory[mem.TRADING_ITEM],
            "secret_shells": self.pyboy.memory[mem.SECRET_SHELLS],
            "golden_leaves": self.pyboy.memory[mem.GOLDEN_LEAVES],
            "ocarina_songs": self.pyboy.memory[mem.OCARINA_SONGS],
            "ocarina_selected": self.pyboy.memory[mem.OCARINA_SELECTED]
        }
    
    def get_max_capacities(self):
        """Get maximum capacities for consumable items."""
        return {
            "max_magic_powder": self.pyboy.memory[mem.MAX_MAGIC_POWDER],
            "max_bombs": self.pyboy.memory[mem.MAX_BOMBS],
            "max_arrows": self.pyboy.memory[mem.MAX_ARROWS],
            "keys": self.pyboy.memory[mem.KEYS_IN_POSESSION]
        }
    
    def get_game_state(self):
        """Get current game state."""
        return {
            "state": self.pyboy.memory[mem.GAME_STATE],
            "substate": self.pyboy.memory[mem.GAME_SUBSTATE],
            "room_id": self.pyboy.memory[mem.GAME_ROOM_ID],
            "dungeon_id": self.pyboy.memory[mem.GAME_DUNGEON_ID],
            "current_map": self.pyboy.memory[mem.CURRENT_MAP]
        }
    
    def get_game_progress(self):
        """Get current game progress flags."""
        progress_flags = []
        for i in range(16):  # Read 16 bytes of progress flags
            progress_flags.append(self.pyboy.memory[mem.GAME_PROGRESS_FLAGS + i])
        return progress_flags
    
    def get_inventory(self):
        """Get Link's full inventory (10 bytes)."""
        inventory = []
        for addr in range(mem.INVENTORY_START, mem.INVENTORY_END + 1):
            item_id = self.pyboy.memory[addr]
            inventory.append(item_id)
        return inventory
    
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
               f"Held Items: A={self.get_held_items()['item_a_name']}, B={self.get_held_items()['item_b_name']}"
