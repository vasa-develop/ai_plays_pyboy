"""
Analyze Memory Changes Log for Zelda: Link's Awakening

This script analyzes the memory changes log created by memory_change_monitor.py
to identify frequently changing addresses and patterns in memory changes.

Usage:
    python analyze_memory_changes.py [log_file]

If log_file is not provided, it defaults to 'memory_changes.log'.
"""
import sys
import re
from collections import Counter, defaultdict

def analyze_memory_changes(log_file='memory_changes.log'):
    """Analyze memory changes log to identify patterns."""
    print(f"Analyzing memory changes from {log_file}...")
    
    line_pattern = re.compile(r'\[(\d+)\] (0x[0-9A-F]{4}): (\d+) -> (\d+)')
    
    address_frequency = Counter()
    address_value_ranges = defaultdict(set)
    frame_changes = defaultdict(int)
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        data_lines = [line for line in lines if line_pattern.match(line)]
        
        if not data_lines:
            print("No memory change data found in the log file.")
            return
        
        print(f"Found {len(data_lines)} memory change records.")
        
        for line in data_lines:
            match = line_pattern.match(line)
            if match:
                frame, addr, old_val, new_val = match.groups()
                frame = int(frame)
                addr = addr  # Keep as hex string
                old_val = int(old_val)
                new_val = int(new_val)
                
                address_frequency[addr] += 1
                
                address_value_ranges[addr].add(new_val)
                
                frame_changes[frame] += 1
        
        print("\n=== Most Frequently Changing Addresses ===")
        for addr, count in address_frequency.most_common(20):
            values = address_value_ranges[addr]
            value_range = f"Range: {min(values)}-{max(values)}" if len(values) > 1 else f"Value: {list(values)[0]}"
            print(f"{addr}: {count} changes, {len(values)} unique values, {value_range}")
        
        print("\n=== Address Groups by Change Frequency ===")
        
        high_freq = [addr for addr, count in address_frequency.items() if count > len(data_lines) * 0.1]
        print(f"\nVery High Frequency Changes (potential timers/counters): {len(high_freq)} addresses")
        for addr in high_freq[:10]:  # Show top 10
            print(f"  {addr}: {address_frequency[addr]} changes, {len(address_value_ranges[addr])} unique values")
        
        med_freq = [addr for addr, count in address_frequency.items() 
                   if count > len(data_lines) * 0.01 and count <= len(data_lines) * 0.1]
        print(f"\nMedium Frequency Changes (potential player/enemy state): {len(med_freq)} addresses")
        for addr in med_freq[:10]:  # Show top 10
            print(f"  {addr}: {address_frequency[addr]} changes, {len(address_value_ranges[addr])} unique values")
        
        low_freq = [addr for addr, count in address_frequency.items() if count <= len(data_lines) * 0.01]
        print(f"\nLow Frequency Changes (potential flags/inventory): {len(low_freq)} addresses")
        for addr in low_freq[:10]:  # Show top 10
            print(f"  {addr}: {address_frequency[addr]} changes, {len(address_value_ranges[addr])} unique values")
        
        print("\n=== Potential Position Coordinates ===")
        position_candidates = [addr for addr, values in address_value_ranges.items() 
                              if len(values) > 20 and address_frequency[addr] > len(data_lines) * 0.05]
        
        for addr in position_candidates:
            print(f"  {addr}: {address_frequency[addr]} changes, {len(address_value_ranges[addr])} unique values")
        
        print("\n=== Potential Binary State Flags ===")
        flag_candidates = [addr for addr, values in address_value_ranges.items() 
                          if len(values) <= 2 and address_frequency[addr] > 1]
        
        for addr in flag_candidates[:20]:  # Show top 20
            print(f"  {addr}: {address_frequency[addr]} changes, values: {sorted(address_value_ranges[addr])}")
        
        print("\n=== Summary ===")
        print(f"Total addresses with changes: {len(address_frequency)}")
        print(f"Total frames with changes: {len(frame_changes)}")
        print(f"Average changes per active frame: {sum(frame_changes.values()) / len(frame_changes):.2f}")
        
    except FileNotFoundError:
        print(f"Error: Log file '{log_file}' not found.")
    except Exception as e:
        print(f"Error analyzing log file: {e}")

if __name__ == "__main__":
    log_file = sys.argv[1] if len(sys.argv) > 1 else 'memory_changes.log'
    analyze_memory_changes(log_file)
