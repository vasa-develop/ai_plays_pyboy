"""
Memory map for Zelda: Link's Awakening based on official RAM map.

This file documents the memory addresses from the official RAM map:
https://datacrystal.tcrf.net/wiki/The_Legend_of_Zelda:_Link%27s_Awakening_(Game_Boy)/RAM_map
"""

LINK_X_POS = 0xDB00  # Link's X position (official)
LINK_Y_POS = 0xDB01  # Link's Y position (official)
LINK_DIRECTION = 0xDB04  # Link's facing direction (official)
LINK_ANIMATION_STATE = 0xDB05  # Link's animation state
LINK_SPRITE_ATTR = 0xDB06  # Link's sprite attributes

DIRECTION_UP = 0    # Facing up
DIRECTION_RIGHT = 1 # Facing right
DIRECTION_DOWN = 2  # Facing down
DIRECTION_LEFT = 3  # Facing left

LINK_HEALTH = 0xDB5A  # Current health (official)
LINK_MAX_HEALTH = 0xDB5B  # Maximum health (official)
LINK_MAGIC_POWDER = 0xDB4F  # Magic powder count
LINK_BOMBS = 0xDB4E  # Bomb count
LINK_ARROWS = 0xDB4D  # Arrow count
LINK_RUPEES = 0xDB46  # Rupee count (low byte)
LINK_RUPEES_HIGH = 0xDB47  # Rupee count (high byte)

LINK_SWORD_LEVEL = 0xDB4A  # Sword level
LINK_SHIELD_LEVEL = 0xDB49  # Shield level
LINK_SELECTED_ITEM_A = 0xDB75  # Selected A button item
LINK_SELECTED_ITEM_B = 0xDB76  # Selected B button item

GAME_STATE = 0xDBE0  # Current game state
GAME_SUBSTATE = 0xDBE1  # Game substate
GAME_ROOM_ID = 0xD800  # Current room ID
GAME_DUNGEON_ID = 0xDBB8  # Current dungeon ID
GAME_PROGRESS_FLAGS = 0xDBA0  # Game progress flags (start of array)

ENEMY_STATE_START = 0xD000  # Start of enemy state memory region
ENEMY_COUNT = 0xD001  # Number of active enemies
ENEMY_TYPE = 0xD008  # Enemy type identifier
ENEMY_HEALTH = 0xD009  # Enemy health
ENEMY_POSITION_X = 0xD00C  # Enemy X position
ENEMY_POSITION_Y = 0xD00D  # Enemy Y position
