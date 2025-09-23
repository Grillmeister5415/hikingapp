# Surf Tracking Feature Documentation

## Overview

The Surf Tracking feature extends WanderApp from a hiking-focused application to a comprehensive outdoor activity tracker that supports both hiking and surfing. This major enhancement introduces specialized surfing functionality while maintaining full backward compatibility with existing hiking features.

## Key Features

### 🏄‍♂️ Surf Session Tracking
- **Comprehensive Session Details**: Track surf spot, time in water, surfboard used, and session quality
- **Wave Conditions**: Record wave height, quality rating (1-5 stars), and number of waves caught
- **Environmental Data**: Log water temperature, tide information, swell/wind direction, and wave energy
- **Country/Location**: Required country field for surf trips with popular surf destinations highlighted

### 📊 Advanced Statistics
- **Surf-Specific Metrics**: Total surf time, wave count, unique spots surfed, most used surfboard
- **Activity-Based Filtering**: Separate statistics for hiking vs surfing activities
- **Dashboard Integration**: Surf records including longest session, most waves caught, best wave quality

### 🌍 Geographic Features
- **Country Support**: Integration with django-countries for location tracking
- **Popular Surf Destinations**: Pre-configured list of 13 major surf destinations with flag emojis
- **Spot Tracking**: Track and count unique surf spots visited

## Database Schema Changes

### Trip Model Enhancements
- **activity_type**: CharField with choices ['HIKING', 'SURFING'], defaults to 'HIKING'
- **country**: CountryField for surf trip locations (required for surf trips)
- **SURF_DESTINATIONS**: Static list of popular surf countries (AU, BR, CR, FR, ID, MX, MA, NZ, PE, PT, ES, US, ZA)

### Stage Model Surf Fields
All surf-specific fields are optional for backward compatibility:

#### Basic Surf Information
- **activity_type**: CharField matching trip activity type
- **surf_spot**: CharField(200) - Name/description of surf spot
- **time_in_water**: DurationField - Time spent surfing

#### Wave Conditions
- **wave_height**: FloatField - Wave height in meters
- **wave_quality**: IntegerField(1-5) - Star rating with validators
- **waves_caught**: IntegerField - Number of waves surfed
- **wave_energy**: FloatField - Wave power/energy rating

#### Environmental Conditions
- **water_temperature**: FloatField - Temperature in Celsius
- **surfboard_used**: CharField(100) - Surfboard description
- **tide_stage**: CharField choices ['LOW', 'MID', 'HIGH']
- **tide_movement**: CharField choices ['RISING', 'FALLING']
- **swell_direction**: CharField - 8-point compass direction
- **wind_direction**: CharField - 8-point compass direction

### Migration History
1. **0011**: Initial surf fields added to Stage model
2. **0012**: Activity type added to Trip model  
3. **0015**: Country field added to Trip model
4. **0016**: Additional surf conditions (swell/wind direction, wave energy)

## API Enhancements

### New Endpoints
- **GET /api/countries/**: Returns popular surf destinations and all countries with flags
- **Activity filtering**: All user stats endpoints support `?activity_type=SURFING` parameter

### Enhanced Serializers

#### TripListSerializer & TripDetailSerializer
- **Surf aggregations**: `total_surf_time`, `total_wave_count`, `unique_surf_spots_count`
- **Country display**: `country`, `country_display` with flag emojis
- **Session counting**: `surf_session_count` method
- **Validation**: Country required for surf trips

#### StageSerializer
- **All surf fields**: Complete integration of surf-specific data
- **Backward compatibility**: Existing hiking fields unchanged
- **Activity-based handling**: Different processing based on activity_type

### Updated Views

#### TripViewSet
- **Enhanced queryset**: Surf-specific annotations for totals and counts
- **Activity filtering**: Support for filtering by activity type
- **Lightweight listing**: Optimized TripListSerializer for performance

#### UserStatsView & DashboardDataView  
- **Activity filtering**: `?activity_type=SURFING` support
- **Surf statistics**: Comprehensive surfing metrics
- **Separate records**: Activity-specific achievement tracking
- **Most used equipment**: Surfboard usage analytics

## Frontend Implementation

### New Components

#### SurfStageCreate.vue
- **Comprehensive form**: All surf-specific fields with validation
- **Tide information**: Dedicated section for tide stage/movement
- **Wave conditions**: Swell/wind direction with 8-point compass
- **Time formatting**: Duration input with HH:MM pattern validation
- **Mobile responsive**: Optimized layouts for different screen sizes

#### SurfStageEdit.vue
- **Complete editing**: Full surf session modification capabilities
- **Data formatting**: Proper handling of duration display (strips seconds)
- **Validation**: Required fields and data type conversion
- **Consistent styling**: Matches create form design

### Enhanced Existing Components

#### TripCreate.vue
- **Activity-aware sections**: Huts for hiking, country for surfing
- **Popular destinations**: Grouped country dropdown with surf favorites
- **Dynamic labels**: Activity-specific trip type labels
- **Conditional validation**: Country required for surf trips

#### TripDetail.vue
- **Activity-specific overviews**: Different stats for hiking vs surfing
- **Surf metrics display**: Total surf time, wave count, spots surfed
- **Dynamic sections**: Huts for hiking, surf spots for surfing  
- **Activity icons**: Visual indicators for different stage types
- **Smart routing**: Activity-aware stage creation links

#### TripList.vue
- **Activity filtering**: Support for category-based filtering
- **Different statistics**: Surf stats vs hiking stats display
- **Visual indicators**: Activity-specific styling and icons

#### UserDashboard.vue
- **Activity filtering**: Toggle between hiking and surfing stats
- **Surf statistics**: Comprehensive surfing metrics and records
- **Equipment tracking**: Most used surfboard analytics
- **Temperature ranges**: Min/max water temperature tracking

### Routing Enhancements

#### New Routes
- **/surfing**: TripList with defaultCategory: 'SURFING'
- **/hiking**: TripList with defaultCategory: 'HIKING'  
- **/trip/:tripId/add-surf-stage**: SurfStageCreate component
- **/surf-stage/:id/edit**: SurfStageEdit component

#### Enhanced Navigation
- **Activity-aware stage creation**: Different routes based on trip activity type
- **Consistent URL patterns**: Maintains RESTful structure
- **Backward compatibility**: All existing routes preserved

## User Experience Features

### Visual Design
- **Surf theming**: Aqua/teal color scheme (#20b2aa) for surf elements
- **Activity icons**: 🏄‍♂️ for surfing, 🥾 for hiking
- **Star ratings**: Visual wave quality display (⭐⭐⭐⭐⭐)
- **Flag emojis**: Country representation in dropdowns and displays

### Data Input
- **Smart validation**: Activity-appropriate field requirements
- **Format assistance**: Time input with pattern validation (HH:MM)
- **Grouped options**: Popular surf destinations highlighted
- **Range validation**: Wave quality 1-5, compass directions

### Statistics & Analytics
- **Comprehensive tracking**: 15+ surf-specific metrics
- **Activity separation**: Clear distinction between hiking and surfing stats
- **Equipment insights**: Most used surfboard identification
- **Environmental records**: Temperature ranges, best conditions

## Technical Implementation

### Backward Compatibility
- **Default values**: All new fields default appropriately (activity_type='HIKING')
- **Optional fields**: All surf fields are nullable/blank
- **Existing data**: No impact on current hiking trips and stages
- **API compatibility**: Existing endpoints unchanged

### Performance Optimizations
- **Efficient queries**: Optimized aggregations for large datasets
- **Conditional loading**: Activity-specific data loading
- **Lightweight serializers**: Separate list/detail serializers for performance

### Data Validation
- **Model validators**: MinValueValidator/MaxValueValidator for quality ratings
- **Frontend validation**: HTML5 pattern matching and type validation
- **API validation**: DRF serializer validation with custom rules
- **Country requirements**: Surf trips must specify country

## Migration Guide

### Database Migration
```bash
python manage.py migrate
```

### Required Dependencies
- **django-countries**: Already included in requirements.txt
- **No new frontend dependencies**: Uses existing Vue.js ecosystem

### Configuration
- **Popular surf destinations**: Configured in `Trip.SURF_DESTINATIONS`
- **Country API**: New endpoint for country selection
- **Activity choices**: Centralized in model choices

---

## Summary

The Surf Tracking feature represents a significant expansion of WanderApp's capabilities, transforming it from a hiking-specific application into a comprehensive outdoor activity tracker. The implementation maintains full backward compatibility while providing rich, specialized functionality for surf enthusiasts. With comprehensive data tracking, intuitive user interfaces, and robust technical architecture, this feature positions WanderApp as a versatile platform for outdoor activity tracking across multiple sports.

Key achievements:
- ✅ **15+ surf-specific data fields** for comprehensive session tracking
- ✅ **Complete UI/UX redesign** with activity-aware components  
- ✅ **Advanced statistics** with activity-based filtering
- ✅ **Geographic integration** with popular surf destinations
- ✅ **100% backward compatibility** with existing hiking features
- ✅ **Mobile-responsive design** for field data entry
- ✅ **RESTful API design** with efficient data aggregation