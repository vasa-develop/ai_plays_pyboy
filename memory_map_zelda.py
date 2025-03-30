"""
Memory map for Zelda: Link's Awakening based on official RAM map.

This file documents the memory addresses from the official RAM map:
https://datacrystal.tcrf.net/wiki/The_Legend_of_Zelda:_Link%27s_Awakening_(Game_Boy)/RAM_map
"""

LINK_X_POS_OLD = 0xC000  # Link's X position (reverse-engineered)
LINK_Y_POS_OLD = 0xC001  # Link's Y position (reverse-engineered)
LINK_DIRECTION_OLD = 0xC00B  # Link's facing direction (reverse-engineered)

DEST_X_POS = 0xD404  # Destination X coordinate
DEST_Y_POS = 0xD405  # Destination Y coordinate

DUNGEON_POS = 0xDBAE  # Position on 8x8 dungeon grid

DIRECTION_UP = 0    # Facing up
DIRECTION_RIGHT = 1 # Facing right
DIRECTION_DOWN = 2  # Facing down
DIRECTION_LEFT = 3  # Facing left

LINK_HEALTH = 0xDB5A  # Current health (official)
LINK_MAX_HEALTH = 0xDB5B  # Maximum health (official)

HELD_ITEM_A = 0xDB00  # Currently held item A
HELD_ITEM_B = 0xDB01  # Currently held item B
INVENTORY_START = 0xDB02  # Start of inventory (10 bytes)
INVENTORY_END = 0xDB0B  # End of inventory

FLIPPERS = 0xDB0C  # Flippers (01=have)
POTION = 0xDB0D  # Potion (01=have)
TRADING_ITEM = 0xDB0E  # Current trading item (01=Yoshi, 0E=magnifier)
SECRET_SHELLS = 0xDB0F  # Number of secret shells
DUNGEON_KEYS = 0xDB10  # Dungeon entrance keys (5 bytes, 01=have)
GOLDEN_LEAVES = 0xDB15  # Number of golden leaves

POWER_BRACELET_LEVEL = 0xDB43  # Power bracelet level
SHIELD_LEVEL = 0xDB44  # Shield level
SWORD_LEVEL = 0xDB4E  # Sword level

ARROWS = 0xDB45  # Number of arrows
OCARINA_SONGS = 0xDB49  # Ocarina songs (3 bits mask, 0=none, 7=all)
OCARINA_SELECTED = 0xDB4A  # Ocarina selected song
MAGIC_POWDER = 0xDB4C  # Magic powder quantity
BOMBS = 0xDB4D  # Number of bombs

RUPEES_LOW = 0xDB5D  # Rupees (low byte)
RUPEES_HIGH = 0xDB5E  # Rupees (high byte)

MAX_MAGIC_POWDER = 0xDB76  # Max magic powder
MAX_BOMBS = 0xDB77  # Max bombs
MAX_ARROWS = 0xDB78  # Max arrows
KEYS_IN_POSESSION = 0xDBD0  # Quantity of keys in possession

GAME_STATE = 0xDBE0  # Current game state
GAME_SUBSTATE = 0xDBE1  # Game substate
GAME_ROOM_ID = 0xD800  # Current room ID
GAME_DUNGEON_ID = 0xDBB8  # Current dungeon ID
GAME_PROGRESS_FLAGS = 0xDBA0  # Game progress flags (start of array)

WORLD_MAP_STATUS = 0xD800  # World map status (256 bytes)
CURRENT_MAP = 0xD700  # Currently loaded map

ITEM_SWORD = 0x01
ITEM_BOMBS = 0x02
ITEM_POWER_BRACELET = 0x03
ITEM_SHIELD = 0x04
ITEM_BOW = 0x05
ITEM_HOOKSHOT = 0x06
ITEM_FIRE_ROD = 0x07
ITEM_PEGASUS_BOOTS = 0x08
ITEM_OCARINA = 0x09
ITEM_FEATHER = 0x0A
ITEM_SHOVEL = 0x0B
ITEM_MAGIC_POWDER = 0x0C
ITEM_BOOMERANG = 0x0D
