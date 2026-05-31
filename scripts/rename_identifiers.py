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

def rename_identifiers_in_value(value, depth=0, key_name=''):
    """Recursively rename identifiers in JSON values."""
    if isinstance(value, str):
        # Skip URLs and certain patterns - check for URL schemes and img.shields.io
        if 'http://' in value or 'https://' in value or 'github.com' in value or 'img.shields.io' in value:
            return value
        
        # Replace display names for chat participants
        if key_name in ['name', 'fullName']:
            if value == 'GitHubCopilot' or value == 'GitHub Copilot':
                return 'Cutie'
        
        # Replace translation references like %github.copilot.xxx%
        value = re.sub(r'%github\.copilot\.', r'%cutie.', value)
        
        # Replace github.copilot with cutie
        value = value.replace('github.copilot', 'cutie')
        # Replace copilot-chat with cutie-chat
        value = value.replace('copilot-chat', 'cutie-chat')
        # Replace copilot. with cutie. (but not in URLs or other contexts)
        # Only replace if it's at the start or after a quote/space
        value = re.sub(r'\bcopilot\.', 'cutie.', value)
        
        # Skip replacing copilot[A-Z] patterns that refer to specific tools/features
        # like copilotCLI, copilotDebugCommand, etc.
        # Only replace copilot[A-Z] if it's NOT followed by CLI or DebugCommand
        value = re.sub(r'\bcopilot(?!CLI|DebugCommand)([A-Z])', r'cutie\1', value)
        
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
            new_dict[new_key] = rename_identifiers_in_value(v, depth+1, k)
        return new_dict
    elif isinstance(value, list):
        return [rename_identifiers_in_value(item, depth+1, key_name) for item in value]
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
    
    # Fix view name "Chat" to "Cutie" to avoid confusion with built-in Copilot
    if 'contributes' in data and 'views' in data['contributes']:
        views = data['contributes']['views']
        if 'cutie' in views:
            for view in views['cutie']:
                if view.get('id') == 'cutie.chatView' and view.get('name') == 'Chat':
                    view['name'] = 'Cutie'
                    print("  ✓ Renamed chat view name from 'Chat' to 'Cutie'")
    
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
            
            # Don't replace copilotCLI or CopilotCLI - they refer to GitHub Copilot CLI tool
            
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
