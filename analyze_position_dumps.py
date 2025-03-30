"""
Position-Focused Memory Dump Analyzer for Zelda: Link's Awakening

This script analyzes the memory dumps collected by the position-focused memory dump tool
to identify patterns in position-related memory addresses during consecutive key presses.
"""
import json
import sys
from collections import defaultdict
import memory_map_zelda as mem

def load_memory_dumps(filename):
    """Load memory dumps from a JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)

def analyze_position_changes(dumps):
    """Analyze position-related memory changes across consecutive key presses."""
    direction_groups = defaultdict(list)
    
    for dump in dumps:
        if "key_pressed" in dump and dump["key_pressed"] in ["UP", "DOWN", "LEFT", "RIGHT"]:
            key = (dump["key_pressed"], dump.get("consecutive_count", 0))
            direction_groups[key].append(dump)
    
    position_changes = {}
    
    for (direction, count), dumps_list in direction_groups.items():
        if count == 0:
            continue
            
        if len(dumps_list) < 1:
            continue
            
        dump = dumps_list[0]
        
        if "position_data" in dump:
            position_data = dump["position_data"]
            position_changes[(direction, count)] = position_data
    
    return position_changes

def detect_position_patterns(position_changes):
    """Detect patterns in position changes across consecutive key presses."""
    patterns = defaultdict(list)
    
    for (direction, count), position_data in position_changes.items():
        patterns[direction].append((count, position_data))
    
    for direction in patterns:
        patterns[direction].sort(key=lambda x: x[0])
    
    return patterns

def analyze_dumps(filename):
    """Analyze position-focused memory dumps and print findings."""
    print(f"Analyzing position-focused memory dumps from {filename}...")
    
    dumps = load_memory_dumps(filename)
    print(f"Loaded {len(dumps)} memory dumps")
    
    position_changes = analyze_position_changes(dumps)
    patterns = detect_position_patterns(position_changes)
    
    print("\n=== POSITION ANALYSIS RESULTS ===\n")
    
    for direction in ["UP", "DOWN", "LEFT", "RIGHT"]:
        if direction not in patterns:
            continue
            
        print(f"\nDirection: {direction}")
        
        sequence = patterns[direction]
        
        for count, position_data in sequence:
            print(f"  Press #{count}:")
            
            for addr, value in position_data.items():
                addr_name = "Unknown"
                if addr == f"0x{mem.LINK_X_POS:04X}":
                    addr_name = "LINK_X_POS"
                elif addr == f"0x{mem.LINK_Y_POS:04X}":
                    addr_name = "LINK_Y_POS"
                elif addr == f"0x{mem.LINK_SPRITE_X:04X}":
                    addr_name = "LINK_SPRITE_X"
                elif addr == f"0x{mem.LINK_SPRITE_Y:04X}":
                    addr_name = "LINK_SPRITE_Y"
                elif addr == f"0x{mem.LINK_DIRECTION_FLAGS:04X}":
                    addr_name = "LINK_DIRECTION_FLAGS"
                elif addr == f"0x{mem.LINK_DIRECTION_FLAGS2:04X}":
                    addr_name = "LINK_DIRECTION_FLAGS2"
                
                print(f"    {addr} ({addr_name}): {value}")
        
        if len(sequence) >= 2:
            print("\n  Changes between consecutive presses:")
            
            for i in range(len(sequence) - 1):
                count1, data1 = sequence[i]
                count2, data2 = sequence[i + 1]
                
                print(f"    Press #{count1} -> Press #{count2}:")
                
                for addr in data1:
                    if addr in data2 and data1[addr] != data2[addr]:
                        addr_name = "Unknown"
                        if addr == f"0x{mem.LINK_X_POS:04X}":
                            addr_name = "LINK_X_POS"
                        elif addr == f"0x{mem.LINK_Y_POS:04X}":
                            addr_name = "LINK_Y_POS"
                        elif addr == f"0x{mem.LINK_SPRITE_X:04X}":
                            addr_name = "LINK_SPRITE_X"
                        elif addr == f"0x{mem.LINK_SPRITE_Y:04X}":
                            addr_name = "LINK_SPRITE_Y"
                        elif addr == f"0x{mem.LINK_DIRECTION_FLAGS:04X}":
                            addr_name = "LINK_DIRECTION_FLAGS"
                        elif addr == f"0x{mem.LINK_DIRECTION_FLAGS2:04X}":
                            addr_name = "LINK_DIRECTION_FLAGS2"
                        
                        print(f"      {addr} ({addr_name}): {data1[addr]} -> {data2[addr]} (diff: {data2[addr] - data1[addr]})")
    
    print("\n=== POSITION MEMORY MAP RECOMMENDATIONS ===\n")
    
    direction_change_addrs = set()
    movement_addrs = set()
    
    for direction, sequence in patterns.items():
        if len(sequence) < 2:
            continue
        
        first_count, first_data = sequence[0]
        
        for i in range(1, len(sequence)):
            count, data = sequence[i]
            prev_count, prev_data = sequence[i-1]
            
            for addr in data:
                if addr in prev_data and data[addr] != prev_data[addr]:
                    if i == 1:  # First movement after direction change
                        direction_change_addrs.add(addr)
                    else:  # Subsequent movements
                        movement_addrs.add(addr)
    
    print("Direction change addresses (first key press):")
    for addr in sorted(direction_change_addrs):
        print(f"  {addr}")
    
    print("\nMovement addresses (subsequent key presses):")
    for addr in sorted(movement_addrs):
        print(f"  {addr}")
    
    print("\nRecommended memory map updates:")
    print("```python")
    print("# Player position")
    for addr in sorted(movement_addrs):
        addr_int = int(addr, 16)
        if addr_int in [mem.LINK_X_POS, mem.LINK_Y_POS]:
            print(f"LINK_POSITION_{addr[-2:]} = {addr}  # Changes with movement")
    
    print("\n# Player direction")
    for addr in sorted(direction_change_addrs):
        addr_int = int(addr, 16)
        if addr_int in [mem.LINK_DIRECTION_FLAGS, mem.LINK_DIRECTION_FLAGS2]:
            print(f"LINK_DIRECTION_{addr[-2:]} = {addr}  # Changes with direction")
    print("```")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "zelda_position_dumps.json"
    
    analyze_dumps(filename)
