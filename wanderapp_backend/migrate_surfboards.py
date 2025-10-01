#!/usr/bin/env python
"""
Data migration script to convert surfboard text strings to Surfboard objects
"""
import os
import django
import re

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wanderapp_backend.settings')
django.setup()

from api.models import Stage, Surfboard, User

def detect_board_type(name):
    """Detect board type from name"""
    name_lower = name.lower()
    if 'longboard' in name_lower:
        return 'LONGBOARD'
    elif 'fish' in name_lower:
        return 'FISH'
    elif 'gun' in name_lower:
        return 'GUN'
    elif 'shortboard' in name_lower or 'hpsb' in name_lower or 'performance' in name_lower:
        return 'SHORTBOARD'
    elif 'hybrid' in name_lower:
        return 'HYBRID'
    elif 'foam' in name_lower:
        return 'FOAMBOARD'
    elif 'funboard' in name_lower:
        return 'FUNBOARD'
    else:
        return 'OTHER'

def extract_length(name):
    """Extract length from name (e.g., 6'2" from "6'2\" Shortboard")"""
    # Match patterns like 6'2", 6'2, 6.2, 190cm
    match = re.search(r"(\d+['\"]?\d*[\"']?|\d+cm)", name)
    if match:
        return match.group(1)
    return ''

def migrate_surfboards():
    """Main migration function"""
    # Get all stages with surfboard_used text
    stages_with_boards = Stage.objects.filter(
        surfboard_used__isnull=False
    ).exclude(surfboard_used='').select_related('creator')

    # Group by (surfboard_used, creator)
    board_owners = {}
    for stage in stages_with_boards:
        key = (stage.surfboard_used, stage.creator.id)
        if key not in board_owners:
            board_owners[key] = {
                'name': stage.surfboard_used,
                'owner': stage.creator,
                'stages': []
            }
        board_owners[key]['stages'].append(stage)

    print(f'Found {len(board_owners)} unique surfboard-owner combinations\n')

    created_count = 0
    updated_count = 0

    for (board_name, owner_id), data in board_owners.items():
        name = data['name']
        owner = data['owner']
        stages = data['stages']

        # Check if this surfboard already exists for this owner
        surfboard, created = Surfboard.objects.get_or_create(
            owner=owner,
            name=name,
            defaults={
                'board_type': detect_board_type(name),
                'length': extract_length(name),
            }
        )

        if created:
            created_count += 1
            print(f'✓ Created: "{name}" for {owner.username} (type: {surfboard.board_type}, length: {surfboard.length or "N/A"})')

        # Link all stages to this surfboard
        for stage in stages:
            if stage.surfboard_id != surfboard.id:
                stage.surfboard = surfboard
                stage.save(update_fields=['surfboard'])
                updated_count += 1

    print(f'\nMigration complete:')
    print(f'  - Created {created_count} surfboard objects')
    print(f'  - Updated {updated_count} stage links')

if __name__ == '__main__':
    migrate_surfboards()
