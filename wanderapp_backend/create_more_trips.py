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

def create_trips_with_stages():
    # Get or create a user
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={'username': 'testuser', 'is_quick_user': False}
    )
    print(f'Using user: {user.username}')

    # Trip data with corresponding stages
    trip_stage_data = [
        # Hiking Trips
        {
            'trip': {
                'name': 'Bernese Oberland Explorer',
                'description': 'Classic Swiss hiking adventure through the Bernese Alps',
                'start_date': date(2024, 6, 15),
                'end_date': date(2024, 6, 16),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Gimmelwald to Mürren Ridge Walk',
                'description': 'Spectacular cliff-edge path with Eiger views. Perfect weather conditions.',
                'manual_duration': timedelta(hours=2, minutes=45),
                'manual_length_km': 7.2,
                'manual_elevation_gain': 320,
                'manual_elevation_loss': 180
            }
        },
        {
            'trip': {
                'name': 'Matterhorn Circuit Challenge',
                'description': 'Multi-day trek around the iconic Matterhorn peak',
                'start_date': date(2024, 7, 20),
                'end_date': date(2024, 7, 21),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Zermatt to Schwarzsee Paradise',
                'description': 'Steep ascent to alpine lake with Matterhorn reflections. Cable car option available.',
                'manual_duration': timedelta(hours=4, minutes=15),
                'manual_length_km': 9.8,
                'manual_elevation_gain': 850,
                'manual_elevation_loss': 220
            }
        },
        {
            'trip': {
                'name': 'Rhine Valley Wine Trail',
                'description': 'Gentle vineyard walking through historic wine regions',
                'start_date': date(2024, 8, 12),
                'end_date': date(2024, 8, 12),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Rüdesheim Vineyard Circuit',
                'description': 'Easy walk through terraced vineyards with wine tasting stops. Very relaxing.',
                'manual_duration': timedelta(hours=3, minutes=30),
                'manual_length_km': 12.5,
                'manual_elevation_gain': 280,
                'manual_elevation_loss': 280
            }
        },
        {
            'trip': {
                'name': 'Black Forest Adventure',
                'description': 'Dense forest trails through Germany famous Black Forest',
                'start_date': date(2024, 9, 5),
                'end_date': date(2024, 9, 5),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Triberg Waterfall Hike',
                'description': 'Germany highest waterfalls accessed via forest paths. Muddy after recent rain.',
                'manual_duration': timedelta(hours=1, minutes=50),
                'manual_length_km': 4.2,
                'manual_elevation_gain': 150,
                'manual_elevation_loss': 150
            }
        },
        {
            'trip': {
                'name': 'Alpine Meadows Discovery',
                'description': 'Wildflower season peak in high alpine meadows',
                'start_date': date(2024, 6, 28),
                'end_date': date(2024, 6, 29),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Almenrausch Flower Trail',
                'description': 'Peak wildflower blooming season with incredible diversity. Many photographers present.',
                'manual_duration': timedelta(hours=5, minutes=20),
                'manual_length_km': 14.7,
                'manual_elevation_gain': 620,
                'manual_elevation_loss': 380
            }
        },
        {
            'trip': {
                'name': 'Dolomites Vertical Challenge',
                'description': 'Via ferrata routes through dramatic limestone towers',
                'start_date': date(2024, 8, 18),
                'end_date': date(2024, 8, 19),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Tre Cime Via Ferrata',
                'description': 'Exposed climbing route with fixed cables. Requires head for heights and good weather.',
                'manual_duration': timedelta(hours=6, minutes=45),
                'manual_length_km': 8.9,
                'manual_elevation_gain': 1200,
                'manual_elevation_loss': 400
            }
        },
        {
            'trip': {
                'name': 'Bavarian Castle Walk',
                'description': 'Fairy-tale castles connected by forest paths',
                'start_date': date(2024, 10, 2),
                'end_date': date(2024, 10, 2),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Neuschwanstein to Hohenschwangau',
                'description': 'Tourist-heavy but magical walk between famous castles. Early morning recommended.',
                'manual_duration': timedelta(hours=2, minutes=15),
                'manual_length_km': 5.8,
                'manual_elevation_gain': 220,
                'manual_elevation_loss': 340
            }
        },
        {
            'trip': {
                'name': 'Lake Geneva Circuit',
                'description': 'Lakeside paths with Swiss and French Alps backdrop',
                'start_date': date(2024, 9, 14),
                'end_date': date(2024, 9, 15),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Montreux Lavaux Terraces',
                'description': 'UNESCO World Heritage terraced vineyards along lake. Wine stops highly recommended.',
                'manual_duration': timedelta(hours=4, minutes=30),
                'manual_length_km': 11.2,
                'manual_elevation_gain': 450,
                'manual_elevation_loss': 450
            }
        },
        {
            'trip': {
                'name': 'Austrian Lakes District',
                'description': 'Crystal clear mountain lakes and traditional villages',
                'start_date': date(2024, 7, 8),
                'end_date': date(2024, 7, 9),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Hallstatt Salzberg Trail',
                'description': 'Historic salt mine trail above the famous lake village. Can be crowded in summer.',
                'manual_duration': timedelta(hours=3, minutes=15),
                'manual_length_km': 6.8,
                'manual_elevation_gain': 480,
                'manual_elevation_loss': 120
            }
        },
        {
            'trip': {
                'name': 'Italian Riviera Coastal Path',
                'description': 'Dramatic coastline connecting Cinque Terre villages',
                'start_date': date(2024, 8, 25),
                'end_date': date(2024, 8, 26),
                'activity_type': 'HIKING'
            },
            'stage': {
                'name': 'Monterosso to Vernazza',
                'description': 'Most challenging Cinque Terre section with stunning coastal views. Trail repairs ongoing.',
                'manual_duration': timedelta(hours=2, minutes=30),
                'manual_length_km': 3.2,
                'manual_elevation_gain': 180,
                'manual_elevation_loss': 220
            }
        },
        # Surfing Trips
        {
            'trip': {
                'name': 'Portuguese Atlantic Adventure',
                'description': 'World-class surf breaks along the Portuguese coast',
                'start_date': date(2024, 9, 20),
                'end_date': date(2024, 9, 22),
                'activity_type': 'SURFING',
                'country': 'PT'
            },
            'stage': {
                'name': 'Ericeira Point Break Session',
                'description': 'Perfect offshore winds and consistent swell. Local surf school very helpful.',
                'activity_type': 'SURFING',
                'surf_spot': 'Ericeira',
                'time_in_water': timedelta(hours=2, minutes=30),
                'surfboard_used': '6\'2" Shortboard',
                'wave_height': 1.8,
                'wave_quality': 4,
                'waves_caught': 18,
                'water_temperature': 17.5,
                'tide_stage': 'MID',
                'tide_movement': 'RISING',
                'swell_direction': 'W',
                'wind_direction': 'E'
            }
        },
        {
            'trip': {
                'name': 'French Atlantic Coast',
                'description': 'Beach breaks and point breaks in Southwest France',
                'start_date': date(2024, 6, 10),
                'end_date': date(2024, 6, 12),
                'activity_type': 'SURFING',
                'country': 'FR'
            },
            'stage': {
                'name': 'Hossegor La Gravière',
                'description': 'Heavy beach break with powerful barrels. Advanced surfers only in these conditions.',
                'activity_type': 'SURFING',
                'surf_spot': 'Hossegor',
                'time_in_water': timedelta(hours=1, minutes=45),
                'surfboard_used': '5\'10" Fish',
                'wave_height': 2.5,
                'wave_quality': 5,
                'waves_caught': 12,
                'water_temperature': 16.0,
                'tide_stage': 'LOW',
                'tide_movement': 'RISING',
                'swell_direction': 'W',
                'wind_direction': 'SE'
            }
        },
        {
            'trip': {
                'name': 'Moroccan Point Breaks',
                'description': 'Right-hand point breaks and consistent Atlantic swells',
                'start_date': date(2024, 11, 15),
                'end_date': date(2024, 11, 17),
                'activity_type': 'SURFING',
                'country': 'MA'
            },
            'stage': {
                'name': 'Anchor Point Taghazout',
                'description': 'Perfect right-hand point break with long rides. Very crowded during peak season.',
                'activity_type': 'SURFING',
                'surf_spot': 'Anchor Point',
                'time_in_water': timedelta(hours=3, minutes=15),
                'surfboard_used': '6\'6" Longboard',
                'wave_height': 2.2,
                'wave_quality': 5,
                'waves_caught': 25,
                'water_temperature': 19.5,
                'tide_stage': 'MID',
                'tide_movement': 'FALLING',
                'swell_direction': 'NW',
                'wind_direction': 'NE'
            }
        },
        {
            'trip': {
                'name': 'Spanish Basque Coast',
                'description': 'Powerful beach breaks in the Basque Country',
                'start_date': date(2024, 10, 8),
                'end_date': date(2024, 10, 10),
                'activity_type': 'SURFING',
                'country': 'ES'
            },
            'stage': {
                'name': 'Mundaka Left Barrel',
                'description': 'World-famous left-hand river mouth break. Tidal and seasonal conditions critical.',
                'activity_type': 'SURFING',
                'surf_spot': 'Mundaka',
                'time_in_water': timedelta(hours=2, minutes=0),
                'surfboard_used': '6\'0" Performance',
                'wave_height': 1.5,
                'wave_quality': 4,
                'waves_caught': 15,
                'water_temperature': 18.5,
                'tide_stage': 'LOW',
                'tide_movement': 'RISING',
                'swell_direction': 'NW',
                'wind_direction': 'S'
            }
        },
        {
            'trip': {
                'name': 'Indonesian Barrel Hunt',
                'description': 'Tropical reef breaks in the archipelago',
                'start_date': date(2024, 8, 1),
                'end_date': date(2024, 8, 5),
                'activity_type': 'SURFING',
                'country': 'ID'
            },
            'stage': {
                'name': 'Uluwatu Temple Bowls',
                'description': 'Consistent reef break with multiple sections. Sharp coral requires caution.',
                'activity_type': 'SURFING',
                'surf_spot': 'Uluwatu',
                'time_in_water': timedelta(hours=2, minutes=45),
                'surfboard_used': '6\'1" Step-up',
                'wave_height': 3.0,
                'wave_quality': 5,
                'waves_caught': 20,
                'water_temperature': 26.5,
                'tide_stage': 'MID',
                'tide_movement': 'FALLING',
                'swell_direction': 'S',
                'wind_direction': 'E'
            }
        },
        {
            'trip': {
                'name': 'Costa Rican Pacific',
                'description': 'Warm water point breaks and beach breaks',
                'start_date': date(2024, 12, 20),
                'end_date': date(2024, 12, 23),
                'activity_type': 'SURFING',
                'country': 'CR'
            },
            'stage': {
                'name': 'Witch\'s Rock Offshore',
                'description': 'Boat access only to this famous right-hand break. Consistent and uncrowded.',
                'activity_type': 'SURFING',
                'surf_spot': 'Witch\'s Rock',
                'time_in_water': timedelta(hours=3, minutes=30),
                'surfboard_used': '6\'4" Gun',
                'wave_height': 2.8,
                'wave_quality': 4,
                'waves_caught': 22,
                'water_temperature': 24.0,
                'tide_stage': 'HIGH',
                'tide_movement': 'FALLING',
                'swell_direction': 'SW',
                'wind_direction': 'NE'
            }
        },
        {
            'trip': {
                'name': 'Australian Gold Coast',
                'description': 'World-renowned surf breaks and consistent waves',
                'start_date': date(2024, 5, 18),
                'end_date': date(2024, 5, 21),
                'activity_type': 'SURFING',
                'country': 'AU'
            },
            'stage': {
                'name': 'Superbank Barrel Section',
                'description': 'Man-made sand bottom point break creating perfect barrels. Very competitive lineup.',
                'activity_type': 'SURFING',
                'surf_spot': 'Superbank',
                'time_in_water': timedelta(hours=2, minutes=15),
                'surfboard_used': '5\'11" HPSB',
                'wave_height': 1.2,
                'wave_quality': 5,
                'waves_caught': 28,
                'water_temperature': 22.0,
                'tide_stage': 'LOW',
                'tide_movement': 'RISING',
                'swell_direction': 'E',
                'wind_direction': 'W'
            }
        },
        {
            'trip': {
                'name': 'Brazilian Northeast Coast',
                'description': 'Consistent trade wind swells and warm water',
                'start_date': date(2024, 4, 25),
                'end_date': date(2024, 4, 28),
                'activity_type': 'SURFING',
                'country': 'BR'
            },
            'stage': {
                'name': 'Fernando de Noronha',
                'description': 'Remote island break with crystal clear water. Marine sanctuary with strict regulations.',
                'activity_type': 'SURFING',
                'surf_spot': 'Cacimba do Padre',
                'time_in_water': timedelta(hours=1, minutes=30),
                'surfboard_used': '6\'8" Semi-gun',
                'wave_height': 4.2,
                'wave_quality': 5,
                'waves_caught': 8,
                'water_temperature': 27.5,
                'tide_stage': 'MID',
                'tide_movement': 'RISING',
                'swell_direction': 'NE',
                'wind_direction': 'SE'
            }
        },
        {
            'trip': {
                'name': 'New Zealand South Island',
                'description': 'Cold water perfection in remote locations',
                'start_date': date(2024, 3, 12),
                'end_date': date(2024, 3, 15),
                'activity_type': 'SURFING',
                'country': 'NZ'
            },
            'stage': {
                'name': 'Papatowai Left Point',
                'description': 'Isolated left-hand point break requiring long hike. Full wetsuit essential.',
                'activity_type': 'SURFING',
                'surf_spot': 'Papatowai',
                'time_in_water': timedelta(hours=1, minutes=15),
                'surfboard_used': '6\'3" Quad',
                'wave_height': 2.0,
                'wave_quality': 4,
                'waves_caught': 12,
                'water_temperature': 14.5,
                'tide_stage': 'LOW',
                'tide_movement': 'RISING',
                'swell_direction': 'S',
                'wind_direction': 'W'
            }
        },
        {
            'trip': {
                'name': 'Mexican Pacific Coast',
                'description': 'Beach breaks and point breaks along Oaxaca coast',
                'start_date': date(2024, 1, 30),
                'end_date': date(2024, 2, 2),
                'activity_type': 'SURFING',
                'country': 'MX'
            },
            'stage': {
                'name': 'Puerto Escondido Beach Break',
                'description': 'World\'s heaviest beach break wave. Extremely dangerous for inexperienced surfers.',
                'activity_type': 'SURFING',
                'surf_spot': 'Puerto Escondido',
                'time_in_water': timedelta(hours=1, minutes=0),
                'surfboard_used': '7\'2" Gun',
                'wave_height': 5.5,
                'wave_quality': 5,
                'waves_caught': 4,
                'water_temperature': 25.5,
                'tide_stage': 'LOW',
                'tide_movement': 'FALLING',
                'swell_direction': 'SW',
                'wind_direction': 'NE'
            }
        }
    ]

    created_count = 0

    for i, trip_stage in enumerate(trip_stage_data):
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
            **stage_data
        }

        # Ensure activity_type is set (default to trip's activity type if not specified in stage)
        if 'activity_type' not in stage_kwargs:
            stage_kwargs['activity_type'] = trip.activity_type

        stage = Stage.objects.create(**stage_kwargs)

        created_count += 1
        activity_emoji = '🏄‍♂️' if trip.activity_type == 'SURFING' else '🥾'
        print(f'{activity_emoji} Created: {trip.name} -> {stage.name}')

    print(f'\\nSuccessfully created {created_count} trips with stages!')

if __name__ == '__main__':
    create_trips_with_stages()