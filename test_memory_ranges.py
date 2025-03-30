from pyboy import PyBoy
from pyboy.utils import WindowEvent
import time

def test_memory_ranges():
    """Test identified memory ranges to verify their purpose."""
    rom_path = "zelda.gbc"
    pyboy = PyBoy(rom_path, window="SDL2")
    pyboy.set_emulation_speed(1)

    print("Starting game in render mode. Press Ctrl+C to exit.")
    print("Monitoring memory addresses:")
    print("- 0xC000-0xC001: Expected position coordinates")
    print("- 0xC100-0xC104: Expected status/health")
    print("- 0xD300-0xD305: Expected enemy states")
    
    print("Initializing game...")
    for _ in range(180):
        if _ == 100:  # Press start after some frames
            pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        elif _ == 120:  # Release start
            pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
        pyboy.tick()

    try:
        print("\nGame started! Use arrow keys to move Link and verify memory addresses.")
        print("Press Ctrl+C to exit\n")
        
        while True:
            if pyboy.frame_count % 2 == 0:  # Check input every other frame
                pyboy.send_input(WindowEvent.RELEASE_ARROW_RIGHT)
                pyboy.send_input(WindowEvent.RELEASE_ARROW_DOWN)
                pyboy.send_input(WindowEvent.RELEASE_ARROW_LEFT)
                pyboy.send_input(WindowEvent.RELEASE_ARROW_UP)
                
                if pyboy.frame_count % 120 < 30:  # Move right
                    pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
                elif pyboy.frame_count % 120 < 60:  # Move down
                    pyboy.send_input(WindowEvent.PRESS_ARROW_DOWN)
                elif pyboy.frame_count % 120 < 90:  # Move left
                    pyboy.send_input(WindowEvent.PRESS_ARROW_LEFT)
                else:  # Move up
                    pyboy.send_input(WindowEvent.PRESS_ARROW_UP)
            
            pyboy.tick()
            
            if pyboy.frame_count % 30 == 0:
                print("\nFrame:", pyboy.frame_count)
                print("Position coordinates:")
                for addr in range(0xC000, 0xC010):
                    val = pyboy.memory[addr]
                    print(f"  0x{addr:04X}: {val:02X} ({val})")
                
                print("\nStatus/Health region:")
                for addr in range(0xC100, 0xC110):
                    val = pyboy.memory[addr]
                    print(f"  0x{addr:04X}: {val:02X} ({val})")
                
                print("\nEnemy state region:")
                for addr in range(0xD300, 0xD310):
                    val = pyboy.memory[addr]
                    print(f"  0x{addr:04X}: {val:02X} ({val})")
                
    except KeyboardInterrupt:
        print("\nStopping memory monitoring...")
    finally:
        pyboy.stop()

if __name__ == "__main__":
    test_memory_ranges()
