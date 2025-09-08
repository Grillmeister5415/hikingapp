# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WanderApp is a hiking application with a Vue.js 3 frontend and Django REST Framework backend. It allows users to track hiking trips with stages, photos, and GPS data using PostgreSQL with PostGIS for geographical features.

## Development Commands

### Backend (`wanderapp_backend/`)
- **Start development server**: `python manage.py runserver 0.0.0.0:8000` (from within venv)
- **Activate virtual environment**: `source venv/bin/activate` (from backend directory)
- **Install dependencies**: `pip install -r requirements.txt`
- **Run migrations**: `python manage.py migrate`
- **Create migrations**: `python manage.py makemigrations`
- **Run tests**: `python manage.py test`
- **Create superuser**: `python manage.py createsuperuser`

### Frontend (`wanderapp-frontend/`)
- **Start development server**: `npm run serve` (runs on port 8080)
- **Build for production**: `npm run build`
- **Lint code**: `npm run lint`
- **Install dependencies**: `npm install`

### Development Workflow
1. Start backend: `cd wanderapp_backend && source venv/bin/activate && python manage.py runserver 0.0.0.0:8000`
2. Start frontend: `cd wanderapp-frontend && npm run serve`
3. Access application at `http://localhost:8080`

## Architecture

### Backend Architecture
- **Framework**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL with PostGIS extension
- **Authentication**: JWT tokens via djangorestframework_simplejwt
- **Image processing**: Pillow with custom `image_processing.py` module
- **Configuration**: Environment variables via python-decouple (`.env` file)

**Key Models** (`api/models.py`):
- `User`: Custom user model with email authentication
- `Trip`: Main hiking trip entity with participants (M2M relationship)
- `Stage`: Individual hiking stages within trips
- `Photo`: Images linked to stages with multiple versions (original, thumbnails, WebP)
- `TrackPoint`: GPS coordinates using PostGIS PointField
- `Hut`: Accommodation details for trips

**Key API Structure**:
- `api/views.py`: ViewSets for CRUD operations
- `api/serializers.py`: Nested serialization (stages include photos automatically)
- `api/image_processing.py`: EXIF processing, rotation, format conversion
- `api/urls.py`: API endpoint routing

### Frontend Architecture
- **Framework**: Vue.js 3 with Composition API
- **Router**: Vue Router 4 with authentication guards
- **HTTP Client**: Axios with JWT interceptors (`src/api.js`)
- **Maps**: Mapbox GL JS for GPS visualization
- **File Upload**: Uppy for photo uploads
- **Photo Gallery**: PhotoSwipe for lightbox functionality

**Key Components** (`src/components/`):
- `TripList.vue`: Main trip listing with filters
- `TripDetail.vue`: Trip details with stages and photos
- `UserDashboard.vue`: Personal statistics and records
- `ImageUploader.vue`: Uppy-based photo upload modal
- `MultiSelectDropdown.vue`: Custom multi-select component for filters

**Configuration**:
- `vue.config.js`: Dev server proxy configuration (proxies `/api` and `/media` to backend)
- `src/router.js`: Route definitions with authentication guards
- `src/store.js`: Global state management
- `src/api.js`: Centralized API communication with JWT token management

## Environment Setup

### Backend Environment (`.env` file in `wanderapp_backend/`)
Required environment variables:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Boolean for debug mode
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`: PostgreSQL credentials  
- `SERVER_IP`: IP address for CORS and allowed hosts
- `GDAL_LIBRARY_PATH`, `GEOS_LIBRARY_PATH`: OS-specific geodjango library paths

### System Dependencies
- **macOS**: GDAL/GEOS via Homebrew (`/opt/homebrew/lib/`)
- **Ubuntu**: libgdal-dev, libgeos-dev packages (`/usr/lib/x86_64-linux-gnu/`)
- **Node.js**: Installed via NVM for consistent versions
- **PostgreSQL**: With PostGIS extension enabled

## Key Technical Details

### Database Features
- PostGIS for geographical data (GPS tracks)
- Custom User model with email-based authentication
- Many-to-many relationships for trip participants
- Nested foreign key relationships (Trip → Stage → Photo/TrackPoint)

### Image Processing Pipeline
The `image_processing.py` module handles:
- EXIF rotation correction
- sRGB color space conversion
- Multiple format generation (original, thumbnails, WebP)
- Original dimension calculation after rotation

### API Design
- RESTful endpoints with nested serialization
- JWT authentication with refresh token handling
- Special upload endpoint for photos (`stages/{id}/upload_photos/`)
- Calculated vs manual field separation for hiking metrics

### Frontend-Backend Integration
- Vue dev server proxies API calls to Django backend
- JWT tokens stored in localStorage with automatic refresh
- CORS configured for cross-origin development
- Shared authentication state across components

## Production Considerations
Current setup is development-focused. Production deployment requires:
- Gunicorn WSGI server replacing `runserver`  
- Nginx for static file serving and reverse proxy
- `npm run build` for optimized frontend bundle
- Production `.env` with `DEBUG=False`
- SSL/HTTPS configuration