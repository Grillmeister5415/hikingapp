#!/usr/bin/env python
import os
import sys
import django
from datetime import date, timedelta
import random

# Setup Django
sys.path.insert(0, '/Users/fabian/WanderProject/wanderapp_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wanderapp_backend.settings')
django.setup()

from api.models import Trip, Stage, User

def create_hiking_trips():
    # Get or create a user
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={'username': 'testuser', 'is_quick_user': False}
    )
    print(f'Using user: {user.username}')

    # 20 Hiking Trip data with corresponding stages
    hiking_trip_data = [
        {
            'trip': {
                'name': 'Scottish Highlands Explorer',
                'description': 'Remote wilderness hiking through ancient Scottish mountains',
                'start_date': date(2024, 5, 10),
                'end_date': date(2024, 5, 11),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Ben Nevis Summit Trail',
                'description': 'UK highest peak via tourist path. Weather can change rapidly at summit.',
                'manual_duration': timedelta(hours=7, minutes=15),
                'manual_length_km': 15.5,
                'manual_elevation_gain': 1345,
                'manual_elevation_loss': 1345
            }
        },
        {
            'trip': {
                'name': 'Norwegian Fjord Adventure',
                'description': 'Dramatic mountain ridges above deep blue fjords',
                'start_date': date(2024, 6, 22),
                'end_date': date(2024, 6, 23),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Preikestolen (Pulpit Rock)',
                'description': 'Famous cliff edge with 604m drop. Extremely crowded during summer months.',
                'manual_duration': timedelta(hours=4, minutes=30),
                'manual_length_km': 8.0,
                'manual_elevation_gain': 350,
                'manual_elevation_loss': 350
            }
        },
        {
            'trip': {
                'name': 'Pyrenees Border Crossing',
                'description': 'Cross-border hiking between France and Spain',
                'start_date': date(2024, 7, 5),
                'end_date': date(2024, 7, 6),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Pic du Midi d\'Ossau Circuit',
                'description': 'Technical mountain route requiring some scrambling. Views of both countries.',
                'manual_duration': timedelta(hours=8, minutes=45),
                'manual_length_km': 18.2,
                'manual_elevation_gain': 980,
                'manual_elevation_loss': 980
            }
        },
        {
            'trip': {
                'name': 'Carpathian Wilderness Trek',
                'description': 'Remote mountains in Romania with pristine forests',
                'start_date': date(2024, 8, 3),
                'end_date': date(2024, 8, 4),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Omu Peak Ascent',
                'description': 'Highest peak in Bucegi Mountains. Weather station at summit provides shelter.',
                'manual_duration': timedelta(hours=6, minutes=20),
                'manual_length_km': 12.8,
                'manual_elevation_gain': 850,
                'manual_elevation_loss': 450
            }
        },
        {
            'trip': {
                'name': 'Icelandic Highland Crossing',
                'description': 'Volcanic landscapes and geothermal features',
                'start_date': date(2024, 7, 18),
                'end_date': date(2024, 7, 19),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Landmannalaugar Rainbow Hills',
                'description': 'Multicolored rhyolite mountains and natural hot springs. 4WD access only.',
                'manual_duration': timedelta(hours=5, minutes=45),
                'manual_length_km': 13.5,
                'manual_elevation_gain': 420,
                'manual_elevation_loss': 650
            }
        },
        {
            'trip': {
                'name': 'Greek Island Peak Challenge',
                'description': 'Mediterranean mountain hiking with ancient ruins',
                'start_date': date(2024, 9, 12),
                'end_date': date(2024, 9, 13),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Mount Olympus Mytikas Summit',
                'description': 'Home of the gods - Greece highest peak. Requires overnight mountain hut stay.',
                'manual_duration': timedelta(hours=9, minutes=30),
                'manual_length_km': 16.7,
                'manual_elevation_gain': 1200,
                'manual_elevation_loss': 800
            }
        },
        {
            'trip': {
                'name': 'Welsh Coastal Path',
                'description': 'Rugged clifftop walking along Pembrokeshire coast',
                'start_date': date(2024, 4, 20),
                'end_date': date(2024, 4, 21),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Stackpole to Bosherston Cliffs',
                'description': 'Spectacular sea arch views and puffin colonies. Very windy conditions typical.',
                'manual_duration': timedelta(hours=3, minutes=45),
                'manual_length_km': 9.5,
                'manual_elevation_gain': 280,
                'manual_elevation_loss': 320
            }
        },
        {
            'trip': {
                'name': 'Polish Tatra Mountains',
                'description': 'High alpine lakes and dramatic granite peaks',
                'start_date': date(2024, 6, 8),
                'end_date': date(2024, 6, 9),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Morskie Oko to Rysy Peak',
                'description': 'Famous mountain lake and Polish highest accessible peak. Very popular trail.',
                'manual_duration': timedelta(hours=7, minutes=0),
                'manual_length_km': 14.2,
                'manual_elevation_gain': 1070,
                'manual_elevation_loss': 1070
            }
        },
        {
            'trip': {
                'name': 'Corsican GR20 Section',
                'description': 'Europe most challenging long-distance trail',
                'start_date': date(2024, 9, 25),
                'end_date': date(2024, 9, 26),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Calenzana to Ortu di u Piobbu',
                'description': 'Technical first stage with chains and scrambling. Extremely demanding.',
                'manual_duration': timedelta(hours=6, minutes=15),
                'manual_length_km': 11.5,
                'manual_elevation_gain': 1450,
                'manual_elevation_loss': 790
            }
        },
        {
            'trip': {
                'name': 'Czech Bohemian Paradise',
                'description': 'Unique sandstone formations and medieval castles',
                'start_date': date(2024, 5, 16),
                'end_date': date(2024, 5, 17),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Prachovské Skály Rock Labyrinth',
                'description': 'Maze of sandstone towers with ladder sections. Popular with rock climbers.',
                'manual_duration': timedelta(hours=4, minutes=20),
                'manual_length_km': 8.8,
                'manual_elevation_gain': 350,
                'manual_elevation_loss': 350
            }
        },
        {
            'trip': {
                'name': 'Slovenian Julian Alps',
                'description': 'pristine alpine environment with crystal lakes',
                'start_date': date(2024, 8, 14),
                'end_date': date(2024, 8, 15),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Lake Bled to Vintgar Gorge',
                'description': 'Tourist classic combining lake views with dramatic gorge walkways. Very busy.',
                'manual_duration': timedelta(hours=3, minutes=30),
                'manual_length_km': 7.2,
                'manual_elevation_gain': 180,
                'manual_elevation_loss': 220
            }
        },
        {
            'trip': {
                'name': 'Portuguese Coastal Camino',
                'description': 'Pilgrimage route along Atlantic coastline',
                'start_date': date(2024, 10, 18),
                'end_date': date(2024, 10, 19),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Porto to Vila do Conde',
                'description': 'Beach walking with historic fishing villages. Sandy sections can be tiring.',
                'manual_duration': timedelta(hours=5, minutes=15),
                'manual_length_km': 16.8,
                'manual_elevation_gain': 120,
                'manual_elevation_loss': 140
            }
        },
        {
            'trip': {
                'name': 'Bulgarian Rila Mountains',
                'description': 'Balkans highest peaks with pristine wilderness',
                'start_date': date(2024, 7, 28),
                'end_date': date(2024, 7, 29),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Musala Summit Trail',
                'description': 'Balkan Peninsula highest point. Weather station and emergency shelter at top.',
                'manual_duration': timedelta(hours=6, minutes=45),
                'manual_length_km': 13.2,
                'manual_elevation_gain': 920,
                'manual_elevation_loss': 920
            }
        },
        {
            'trip': {
                'name': 'Estonian Bog Walking',
                'description': 'Unique wetland ecosystems on wooden boardwalks',
                'start_date': date(2024, 6, 1),
                'end_date': date(2024, 6, 2),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Soomaa National Park Bog Trail',
                'description': 'Raised bog ecosystem with unique plant life. Boardwalks can be slippery when wet.',
                'manual_duration': timedelta(hours=2, minutes=45),
                'manual_length_km': 6.5,
                'manual_elevation_gain': 20,
                'manual_elevation_loss': 20
            }
        },
        {
            'trip': {
                'name': 'Croatian Island Hopping',
                'description': 'Mediterranean coastal trails on Dalmatian islands',
                'start_date': date(2024, 9, 3),
                'end_date': date(2024, 9, 4),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Hvar Island Lavender Trail',
                'description': 'Aromatic lavender fields and traditional stone villages. Best during bloom season.',
                'manual_duration': timedelta(hours=4, minutes=10),
                'manual_length_km': 10.2,
                'manual_elevation_gain': 380,
                'manual_elevation_loss': 380
            }
        },
        {
            'trip': {
                'name': 'Finnish Lapland Wilderness',
                'description': 'Arctic Circle hiking through untouched tundra',
                'start_date': date(2024, 8, 20),
                'end_date': date(2024, 8, 21),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Kevo Canyon Nature Trail',
                'description': 'Sub-arctic canyon with rare flora. Midnight sun during summer months.',
                'manual_duration': timedelta(hours=8, minutes=30),
                'manual_length_km': 19.5,
                'manual_elevation_gain': 250,
                'manual_elevation_loss': 250
            }
        },
        {
            'trip': {
                'name': 'Sardinian Coastal Mountains',
                'description': 'Rugged Mediterranean peaks meeting azure waters',
                'start_date': date(2024, 10, 5),
                'end_date': date(2024, 10, 6),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Supramonte Plateau Trek',
                'description': 'Limestone karst landscape with deep canyons. Navigation skills essential.',
                'manual_duration': timedelta(hours=5, minutes=55),
                'manual_length_km': 12.8,
                'manual_elevation_gain': 680,
                'manual_elevation_loss': 520
            }
        },
        {
            'trip': {
                'name': 'Turkish Cappadocia Valleys',
                'description': 'Volcanic rock formations and ancient cave churches',
                'start_date': date(2024, 4, 12),
                'end_date': date(2024, 4, 13),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Rose Valley to Red Valley',
                'description': 'Fairy chimneys and Byzantine frescoes. Perfect for sunrise/sunset photography.',
                'manual_duration': timedelta(hours=3, minutes=20),
                'manual_length_km': 5.8,
                'manual_elevation_gain': 220,
                'manual_elevation_loss': 280
            }
        },
        {
            'trip': {
                'name': 'Faroe Islands Storm Hiking',
                'description': 'Dramatic cliffs and grass-roof villages',
                'start_date': date(2024, 5, 28),
                'end_date': date(2024, 5, 29),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Kallur Lighthouse Trail',
                'description': 'Northern Europe most dramatic cliff walk. Extremely dangerous in high winds.',
                'manual_duration': timedelta(hours=2, minutes=30),
                'manual_length_km': 3.2,
                'manual_elevation_gain': 180,
                'manual_elevation_loss': 180
            }
        },
        {
            'trip': {
                'name': 'Andorran Pyrenees Circuit',
                'description': 'High altitude lakes in micro-nation mountain refuge',
                'start_date': date(2024, 7, 12),
                'end_date': date(2024, 7, 13),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Coma Pedrosa National Peak',
                'description': 'Andorra highest mountain with panoramic Pyrenees views. Clear marking essential.',
                'manual_duration': timedelta(hours=5, minutes=40),
                'manual_length_km': 11.8,
                'manual_elevation_gain': 780,
                'manual_elevation_loss': 780
            }
        }
    ]

    created_count = 0

    for i, trip_stage in enumerate(hiking_trip_data):
        trip_data = trip_stage['trip']
        stage_data = trip_stage['stage']

        # Create trip
        trip = Trip.objects.create(
            creator=user,
            **trip_data
        )
        trip.participants.add(user)

        # Set stage date to be within trip bounds
        stage_date = trip.start_date

        # Create stage
        stage_kwargs = {
            'trip': trip,
            'creator': user,
            'date': stage_date,
            'activity_type': 'HIKING',  # Ensure all stages are hiking
            **stage_data
        }

        stage = Stage.objects.create(**stage_kwargs)

        created_count += 1
        print(f'🥾 Created: {trip.name} -> {stage.name}')

    print(f'\\nSuccessfully created {created_count} hiking trips with stages!')

if __name__ == '__main__':
    create_hiking_trips()