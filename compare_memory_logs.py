"""
Compare Memory Logs for Zelda: Link's Awakening

This script compares two memory log files to identify addresses that appear
in the movement log but not in the no-movement log, helping to identify
memory addresses specifically related to character movement.

Usage:
    python compare_memory_logs.py
"""
import re
import os
from collections import defaultdict, Counter

def extract_addresses(file_path):
    """Extract memory addresses from a log file."""
    addresses = set()
    address_values = defaultdict(set)
    address_counts = Counter()
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        address_pattern = re.compile(r'0x([0-9A-F]{4})')
        
        if file_path.endswith('.txt'):
            for line in content.split('\n'):
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        addr_match = address_pattern.search(parts[0])
                        if addr_match:
                            addr = addr_match.group(0)
                            addresses.add(addr)
                            address_counts[addr] += 1
                            
                            value_match = re.search(r'(\d+)', parts[1])
                            if value_match:
                                address_values[addr].add(int(value_match.group(1)))
        
        elif file_path.endswith('.log'):
            for line in content.split('\n'):
                addr_match = address_pattern.search(line)
                if addr_match:
                    addr = addr_match.group(0)
                    addresses.add(addr)
                    address_counts[addr] += 1
                    
                    value_match = re.search(r'(\d+) -> (\d+)', line)
                    if value_match:
                        address_values[addr].add(int(value_match.group(1)))
                        address_values[addr].add(int(value_match.group(2)))
        
        return addresses, address_values, address_counts
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return set(), defaultdict(set), Counter()

def compare_logs(movement_file, no_movement_file):
    """Compare logs and find addresses unique to movement file."""
    print(f"Analyzing movement file: {movement_file}")
    movement_addresses, movement_values, movement_counts = extract_addresses(movement_file)
    print(f"Found {len(movement_addresses)} unique addresses in movement file")
    
    print(f"\nAnalyzing no-movement file: {no_movement_file}")
    no_movement_addresses, no_movement_values, no_movement_counts = extract_addresses(no_movement_file)
    print(f"Found {len(no_movement_addresses)} unique addresses in no-movement file")
    
    unique_to_movement = movement_addresses - no_movement_addresses
    print(f"\nFound {len(unique_to_movement)} addresses unique to movement file")
    
    sorted_unique = sorted(unique_to_movement, 
                          key=lambda addr: (movement_counts[addr], len(movement_values[addr])), 
                          reverse=True)
    
    print("\n=== Addresses Unique to Movement (sorted by frequency) ===")
    for addr in sorted_unique[:30]:  # Show top 30
        values = movement_values[addr]
        value_range = f"Range: {min(values)}-{max(values)}" if len(values) > 1 else f"Value: {list(values)[0]}"
        print(f"{addr}: {movement_counts[addr]} occurrences, {len(values)} unique values, {value_range}")
    
    address_ranges = defaultdict(list)
    for addr in unique_to_movement:
        prefix = addr[:4]
        address_ranges[prefix].append(addr)
    
    print("\n=== Address Ranges with Movement-Specific Addresses ===")
    for prefix, addrs in sorted(address_ranges.items(), key=lambda x: len(x[1]), reverse=True):
        if len(addrs) > 1:
            print(f"{prefix}xx: {len(addrs)} addresses")
            for addr in sorted(addrs)[:5]:  # Show first 5 addresses in each range
                values = movement_values[addr]
                value_range = f"Range: {min(values)}-{max(values)}" if len(values) > 1 else f"Value: {list(values)[0]}"
                print(f"  {addr}: {movement_counts[addr]} occurrences, {len(values)} unique values, {value_range}")
            if len(addrs) > 5:
                print(f"  ... and {len(addrs) - 5} more addresses")
    
    potential_position = {addr: values for addr, values in movement_values.items() 
                         if addr in unique_to_movement and len(values) > 5}
    
    print("\n=== Potential Position Coordinates (many unique values) ===")
    for addr, values in sorted(potential_position.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"{addr}: {len(values)} unique values, Range: {min(values)}-{max(values)}")
    
    with open("movement_analysis.txt", "w") as f:
        f.write("=== Addresses Unique to Movement (sorted by frequency) ===\n")
        for addr in sorted_unique:
            values = movement_values[addr]
            value_range = f"Range: {min(values)}-{max(values)}" if len(values) > 1 else f"Value: {list(values)[0]}"
            f.write(f"{addr}: {movement_counts[addr]} occurrences, {len(values)} unique values, {value_range}\n")
    
    print(f"\nComplete analysis written to movement_analysis.txt")
    return unique_to_movement, movement_values, movement_counts

if __name__ == "__main__":
    movement_file = os.path.expanduser("~/attachments/113a9bbf-9183-470f-a025-7241ac346a6c/movement.txt")
    no_movement_file = os.path.expanduser("~/attachments/e3563655-bfc2-4030-b29e-4123e7bb66ec/no_movement.log")
    
    if not os.path.exists(movement_file):
        print(f"Error: Movement file not found at {movement_file}")
    elif not os.path.exists(no_movement_file):
        print(f"Error: No-movement file not found at {no_movement_file}")
    else:
        compare_logs(movement_file, no_movement_file)
