#!/usr/bin/env python3
"""
Rename all Copilot identifiers to Cutie identifiers to avoid conflicts.
This script modifies package.json to replace:
- github.copilot -> cutie
- copilot. -> cutie.
"""

import json
import re
from pathlib import Path

def rename_identifiers_in_value(value, depth=0):
    """Recursively rename identifiers in JSON values."""
    if isinstance(value, str):
        # Skip URLs and certain patterns
        if 'http://' in value or 'https://' in value or 'github.com' in value:
            return value
        
        # Replace translation references like %github.copilot.xxx%
        value = re.sub(r'%github\.copilot\.', r'%cutie.', value)
        
        # Replace github.copilot with cutie
        value = value.replace('github.copilot', 'cutie')
        # Replace copilot-chat with cutie-chat
        value = value.replace('copilot-chat', 'cutie-chat')
        # Replace copilot. with cutie. (but not in URLs or other contexts)
        # Only replace if it's at the start or after a quote/space
        value = re.sub(r'\bcopilot\.', 'cutie.', value)
        # Replace standalone copilot identifiers
        value = re.sub(r'\bcopilot([A-Z])', r'cutie\1', value)  # copilotWelcome -> cutieWelcome
        return value
    elif isinstance(value, dict):
        # Also rename dictionary keys if they contain copilot identifiers
        new_dict = {}
        for k, v in value.items():
            new_key = k
            if 'github.copilot' in k:
                new_key = k.replace('github.copilot', 'cutie')
            elif 'copilot-chat' in k:
                new_key = k.replace('copilot-chat', 'cutie-chat')
            elif k.startswith('copilot.'):
                new_key = k.replace('copilot.', 'cutie.')
            new_dict[new_key] = rename_identifiers_in_value(v, depth+1)
        return new_dict
    elif isinstance(value, list):
        return [rename_identifiers_in_value(item, depth+1) for item in value]
    else:
        return value

def main():
    # Paths to files
    base_path = Path(__file__).parent.parent / 'original' / 'extensions' / 'copilot'
    package_json_path = base_path / 'package.json'
    package_nls_path = base_path / 'package.nls.json'
    
    if not package_json_path.exists():
        print(f"Error: {package_json_path} not found")
        return 1
    
    # Process package.json
    print(f"Reading {package_json_path}...")
    with open(package_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Renaming identifiers in package.json...")
    
    # Rename in specific sections to avoid breaking things
    sections_to_rename = [
        'contributes',
        'activationEvents',
        'badges'
    ]
    
    for section in sections_to_rename:
        if section in data:
            data[section] = rename_identifiers_in_value(data[section])
    
    print(f"Writing modified package.json...")
    with open(package_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Process package.nls.json
    if package_nls_path.exists():
        print(f"\nReading {package_nls_path}...")
        with open(package_nls_path, 'r', encoding='utf-8') as f:
            nls_data = json.load(f)
        
        print("Renaming identifiers in package.nls.json...")
        
        # Rename keys and values in package.nls.json
        new_nls_data = {}
        for key, value in nls_data.items():
            new_key = key
            if 'github.copilot' in key:
                new_key = key.replace('github.copilot', 'cutie')
            elif key.startswith('copilot.'):
                new_key = key.replace('copilot.', 'cutie.')
            
            # Also rename in values (for command links in messages)
            new_value = rename_identifiers_in_value(value)
            new_nls_data[new_key] = new_value
        
        print(f"Writing modified package.nls.json...")
        with open(package_nls_path, 'w', encoding='utf-8') as f:
            json.dump(new_nls_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Renamed {len(new_nls_data)} translation keys")
    
    print("\n✓ Successfully renamed all identifiers")
    print("  github.copilot -> cutie")
    print("  copilot. -> cutie.")
    
    return 0

if __name__ == '__main__':
    exit(main())
