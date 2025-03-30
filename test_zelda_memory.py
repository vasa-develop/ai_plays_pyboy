from pyboy import PyBoy
import memory_map_zelda as mem
import time

def test_zelda_memory():
    """Test memory access for Zelda: Link's Awakening."""
    rom_path = "zelda.gbc"
    pyboy = PyBoy(rom_path, window="SDL2")
    pyboy.set_emulation_speed(1)
    
    print("Starting game...")
    for _ in range(100):
        pyboy.tick()
    
    pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
    pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
    
    for _ in range(60):
        pyboy.tick()
    
    print("\nInitial memory values:")
    print(f"Link X position (0x{mem.LINK_X_POS:04X}): {pyboy.memory[mem.LINK_X_POS]}")
    print(f"Link Y position (0x{mem.LINK_Y_POS:04X}): {pyboy.memory[mem.LINK_Y_POS]}")
    print(f"Link health (0x{mem.LINK_HEALTH:04X}): {pyboy.memory[mem.LINK_HEALTH]}")
    print(f"Link max health (0x{mem.LINK_MAX_HEALTH:04X}): {pyboy.memory[mem.LINK_MAX_HEALTH]}")
    print(f"Link direction (0x{mem.LINK_DIRECTION:04X}): {pyboy.memory[mem.LINK_DIRECTION]}")
    
    print("\nEnemy states:")
    for i in range(5):
        base_addr = mem.ENEMY_STATE_START + (i * 16)
        enemy_type = pyboy.memory[base_addr + 1]
        if enemy_type != 0:
            print(f"Enemy {i}:")
            print(f"  Type (0x{base_addr+1:04X}): {enemy_type}")
            print(f"  Behavior (0x{base_addr+2:04X}): {pyboy.memory[base_addr+2]}")
            print(f"  X position (0x{base_addr+7:04X}): {pyboy.memory[base_addr+7]}")
            print(f"  Y position (0x{base_addr+8:04X}): {pyboy.memory[base_addr+8]}")
            print(f"  State (0x{base_addr+9:04X}): {pyboy.memory[base_addr+9]}")
    
    print("\nTesting movement...")
    print("\nMoving right...")
    pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
    for _ in range(30):
        pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_ARROW_RIGHT)
    
    print(f"New X position: {pyboy.memory[mem.LINK_X_POS]}")
    print(f"New Y position: {pyboy.memory[mem.LINK_Y_POS]}")
    print(f"New direction: {pyboy.memory[mem.LINK_DIRECTION]}")
    
    print("\nMoving down...")
    pyboy.send_input(WindowEvent.PRESS_ARROW_DOWN)
    for _ in range(30):
        pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_ARROW_DOWN)
    
    print(f"New X position: {pyboy.memory[mem.LINK_X_POS]}")
    print(f"New Y position: {pyboy.memory[mem.LINK_Y_POS]}")
    print(f"New direction: {pyboy.memory[mem.LINK_DIRECTION]}")
    
    print("\nTest complete!")
    pyboy.stop()

if __name__ == "__main__":
    from pyboy.utils import WindowEvent
    test_zelda_memory()
