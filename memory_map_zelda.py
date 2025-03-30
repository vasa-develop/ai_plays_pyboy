"""
Memory map for Zelda: Link's Awakening based on analysis.

This file documents the memory addresses identified through testing
and analysis of the Zelda: Link's Awakening ROM.
"""

LINK_X_POS = 0xC000  # Link's X position on screen (absolute)
LINK_Y_POS = 0xC001  # Link's Y position on screen (absolute)
LINK_SPRITE_X = 0xC008  # Link's sprite X position
LINK_SPRITE_Y = 0xC009  # Link's sprite Y position

LINK_DIRECTION_FLAGS = 0xC00B  # Direction flags
LINK_DIRECTION_FLAGS2 = 0xC00F  # Secondary direction flags

DIRECTION_UP = 3    # Observed when pressing UP
DIRECTION_RIGHT = 2 # Observed when pressing RIGHT
DIRECTION_DOWN = 3  # Observed when pressing DOWN (same as UP)
DIRECTION_LEFT = 0  # Observed when pressing LEFT

LINK_HEALTH = 0xC100  # Current health value
LINK_MAX_HEALTH = 0xC104  # Maximum health value
LINK_STATUS = 0xC102  # Status flags (possibly)

ENEMY_STATE_START = 0xD300  # Start of enemy state memory region
ENEMY_TYPE = 0xD301  # Enemy type identifier
ENEMY_BEHAVIOR = 0xD302  # Enemy behavior pattern
ENEMY_POSITION_X = 0xD307  # Enemy X position
ENEMY_POSITION_Y = 0xD308  # Enemy Y position
ENEMY_STATE = 0xD309  # Enemy state (active, inactive, etc.)

GAME_PROGRESS = 0xD350  # Game progress flags
