from pyboy.utils import WindowEvent
from pyboy.plugins.game_wrapper_super import GameWrapperSuper

class GameWrapperZelda(GameWrapperSuper):
    """Game wrapper for Zelda: Link's Awakening."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def _get_health(self):
        """Get Link's current health from memory."""
        return self.pyboy.memory[0xC100]  # Observed incrementing health-like value
        
    def _get_player_position(self):
        """Get Link's position from memory."""
        x = self.pyboy.memory[0xC000]  # Position values showing smooth transitions
        y = self.pyboy.memory[0xC001]
        return (x, y)
        
    def _get_enemy_states(self):
        """Get enemy states from memory."""
        states = []
        for addr in range(0xD300, 0xD350):
            states.append(self.pyboy.memory[addr])
        return states
