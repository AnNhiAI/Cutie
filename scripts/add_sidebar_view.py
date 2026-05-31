#!/usr/bin/env python3
"""
Add Cutie Chat view container and view to sidebar (activitybar).
This adds the main chat interface to the VS Code sidebar.
"""

import json
from pathlib import Path

def add_sidebar_view():
    # Path to package.json
    package_json_path = Path(__file__).parent.parent / 'original' / 'extensions' / 'copilot' / 'package.json'
    
    print(f"Reading {package_json_path}...")
    with open(package_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Add view container to activitybar
    if 'contributes' in data and 'viewsContainers' in data['contributes']:
        activitybar = data['contributes']['viewsContainers'].get('activitybar', [])
        
        # Check if cutie container already exists
        cutie_exists = any(container.get('id') == 'cutie' for container in activitybar)
        
        if not cutie_exists:
            print("Adding Cutie Chat view container to activity bar...")
            # Insert at the beginning
            activitybar.insert(0, {
                "id": "cutie",
                "title": "Cutie Chat",
                "icon": "$(comment-discussion)"
            })
            data['contributes']['viewsContainers']['activitybar'] = activitybar
        else:
            print("Cutie Chat view container already exists")
    
    # Add view to the cutie container
    if 'contributes' in data and 'views' in data['contributes']:
        views = data['contributes']['views']
        
        # Check if cutie view already exists
        if 'cutie' not in views:
            print("Adding Cutie Chat view...")
            views['cutie'] = [
                {
                    "id": "cutie.chatView",
                    "name": "Cutie",
                    "when": "!cutie.chat.disabled"
                }
            ]
        else:
            print("Cutie Chat view already exists")
    
    print("Writing modified package.json...")
    with open(package_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("\n✓ Successfully added Cutie Chat sidebar view")
    print("  - View container ID: cutie")
    print("  - Title: Cutie Chat")
    print("  - Icon: comment-discussion")

if __name__ == '__main__':
    add_sidebar_view()
