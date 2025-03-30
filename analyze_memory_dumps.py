"""
Analyze Memory Dumps for Zelda: Link's Awakening

This script analyzes the memory dumps collected by memory_dump_tool.py
to identify patterns and correlations between key presses and memory changes.
"""
import json
import sys
from collections import defaultdict

def load_memory_dumps(filename):
    """Load memory dumps from a JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)

def find_changing_addresses(dumps):
    """Find addresses that change between dumps."""
    changing_addresses = defaultdict(list)
    
    key_groups = defaultdict(list)
    for dump in dumps:
        key = dump["key_pressed"]
        key_groups[key].append(dump)
    
    for key, key_dumps in key_groups.items():
        if len(key_dumps) < 2:
            continue
        
        for i in range(len(key_dumps) - 1):
            dump1 = key_dumps[i]
            dump2 = key_dumps[i + 1]
            
            for region_name in dump1["regions"]:
                region1 = dump1["regions"][region_name]
                region2 = dump2["regions"][region_name]
                
                for addr in region1:
                    if region1[addr] != region2[addr]:
                        changing_addresses[key].append({
                            "address": addr,
                            "region": region_name,
                            "before": region1[addr],
                            "after": region2[addr],
                            "diff": region2[addr] - region1[addr]
                        })
    
    return changing_addresses

def find_consistent_patterns(changing_addresses):
    """Find addresses that change consistently for specific keys."""
    patterns = {}
    
    for key, changes in changing_addresses.items():
        addr_counts = defaultdict(int)
        for change in changes:
            addr_counts[change["address"]] += 1
        
        frequent_addrs = [addr for addr, count in addr_counts.items() 
                         if count >= len(changes) * 0.5]  # Changed in at least 50% of presses
        
        if frequent_addrs:
            patterns[key] = frequent_addrs
    
    return patterns

def analyze_dumps(filename):
    """Analyze memory dumps and print findings."""
    print(f"Analyzing memory dumps from {filename}...")
    
    dumps = load_memory_dumps(filename)
    print(f"Loaded {len(dumps)} memory dumps")
    
    changing_addresses = find_changing_addresses(dumps)
    
    patterns = find_consistent_patterns(changing_addresses)
    
    print("\n=== MEMORY ANALYSIS RESULTS ===\n")
    
    print("Addresses that change consistently for each key press:")
    for key, addrs in patterns.items():
        print(f"\nKey: {key}")
        for addr in addrs:
            sample_change = next((c for c in changing_addresses[key] if c["address"] == addr), None)
            if sample_change:
                print(f"  {addr} ({sample_change['region']}): {sample_change['before']} -> {sample_change['after']} (diff: {sample_change['diff']})")
    
    print("\n=== LIKELY MEMORY ADDRESSES ===\n")
    
    position_candidates = set()
    for key in ["UP", "DOWN", "LEFT", "RIGHT"]:
        if key in patterns:
            position_candidates.update(patterns[key])
    
    print("Likely player position addresses:")
    for addr in position_candidates:
        print(f"  {addr}")
    
    if "A" in patterns or "B" in patterns:
        action_candidates = set()
        if "A" in patterns:
            action_candidates.update(patterns["A"])
        if "B" in patterns:
            action_candidates.update(patterns["B"])
        
        print("\nLikely action-related addresses:")
        for addr in action_candidates:
            print(f"  {addr}")
    
    print("\nRecommended memory map:")
    print("```python")
    print("# Player position and movement")
    if position_candidates:
        for addr in sorted(position_candidates)[:2]:
            print(f"PLAYER_POS_{addr[-2:]} = {addr}  # Changes with movement")
    
    print("\n# Player status")
    if "A" in patterns or "B" in patterns:
        for addr in sorted(action_candidates)[:3]:
            print(f"PLAYER_STATUS_{addr[-2:]} = {addr}  # Changes with actions")
    
    print("```")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "zelda_memory_dumps.json"
    
    analyze_dumps(filename)
