from pyboy import PyBoy
import os
import time

def analyze_memory():
    """Analyze memory changes during gameplay to identify important addresses."""
    rom_path = os.path.join(os.path.dirname(__file__), "zelda.gbc")
    pyboy = PyBoy(rom_path, window="headless")
    pyboy.set_emulation_speed(0)
    
    initial_memory = {}
    for addr in range(0xC000, 0xDFFF):
        initial_memory[addr] = pyboy.memory[addr]
    
    print("Starting memory monitoring...")
    print("Looking for addresses related to:")
    print("- Health (hearts)")
    print("- Position coordinates")
    print("- Inventory items")
    print("- Game progress flags")
    print("- Enemy states")
    print("- Map/room identifiers")
    
    for _ in range(60):
        pyboy.tick()
    
    changes_count = {}
    try:
        for _ in range(300):  # Run for 300 frames
            pyboy.tick()
            
            if _ % 10 == 0:
                changes = []
                for addr in range(0xC000, 0xDFFF):
                    current_value = pyboy.memory[addr]
                    if current_value != initial_memory[addr]:
                        changes.append((addr, initial_memory[addr], current_value))
                        changes_count[addr] = changes_count.get(addr, 0) + 1
                        initial_memory[addr] = current_value
                
                if changes:
                    print("\nDetected memory changes:")
                    for addr, old_val, new_val in changes:
                        print(f"Address 0x{addr:04X}: {old_val:02X} -> {new_val:02X}")
    
    except KeyboardInterrupt:
        print("\nStopping memory monitoring...")
        print("\nMost active memory addresses:")
        for addr, count in sorted(changes_count.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"Address 0x{addr:04X} changed {count} times")
    finally:
        pyboy.stop()

if __name__ == "__main__":
    analyze_memory()
