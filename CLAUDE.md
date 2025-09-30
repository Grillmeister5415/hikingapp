# CLAUDE.md

This file provides **project-specific guidance** to Claude Code (claude.ai/code) when working with this repository. It is **automatically loaded into context** and should be treated as **source-of-truth instructions** for agentic coding in *WanderApp*.

> **IMPORTANT — YOU MUST FOLLOW THIS FILE**
> - Read & apply all rules below when proposing or making changes.
> - Prefer accurate, minimal edits over broad rewrites.
> - Never hard‑code secrets or environment‑specific values.
> - When uncertain, plan first (see “Working Mode & Output Expectations”), then implement incrementally and verify.

---

## Project Overview

**WanderApp** is a multi‑activity tracking application with a **Vue.js 3** frontend and a **Django REST Framework** backend. It supports both **hiking trips** and **surfing sessions** with stages, photos, GPS data, and analytics, backed by **PostgreSQL + PostGIS** for geospatial features. The UI has activity‑specific fields and components.

---

## Important Development Guidelines

### 1) Frontend Design System (**must follow**)
All frontend changes **MUST** follow the design system guidelines in **`.claude/Context/DESIGN_SYSTEM_GUIDE.md`**.

**Use design tokens from `src/styles/tokens.css` (no hard‑coded values):**
- **Colors:** `var(--color-primary)`, `var(--color-neutral-600)`, …
- **Spacing:** `var(--space-4)`, `var(--space-8)`, …
- **Typography:** `var(--text-sm)`, `var(--text-lg)`, …
- **Shadows:** `var(--shadow-sm)`, `var(--shadow-md)`, …

**Use base components from `src/components/base/`:**
- `BaseButton.vue` (variants: primary, secondary, ghost, danger, link)
- `BaseInput.vue` (all form inputs & textareas)
- `BaseCard.vue`, `BaseBadge.vue`, `BaseModal.vue`

**Do NOT** hard‑code colors, spacing, or typography. Always reference tokens. See the design system guide for component APIs, variants, and usage examples.

### 2) Change Documentation (**must follow**)
All significant changes **MUST** be documented in **`.claude/Context/CHANGELOG.md`** using “Keep a Changelog” style:

- **Added** / **Changed** / **Deprecated** / **Removed** / **Fixed** / **Security**
- Include **context** (what/why), note **breaking changes**.
- Add **date** and **version** when applicable.
- Keep an **[Unreleased]** section current during development.

### 3) Visual Development (**must verify immediately**)
After any visual (UI/UX) change, **IMMEDIATELY** perform a quick verification:

1. Identify what changed (list modified components/pages).
2. Navigate to the affected views (e.g., via **`mcp__playwright__browser_navigate`**, if configured).
3. Verify design compliance against `.claude/Context/DESIGN_SYSTEM_GUIDE.md`.
4. Validate the change fulfills the specific user request/acceptance criteria.
5. Check acceptance criteria from any context files/requirements.
6. Capture evidence: full‑page screenshots at 1440px desktop viewport for each changed view.
7. Inspect console for errors (e.g., **`mcp__playwright__browser_console_messages`**, if configured).

For substantial UI/UX work or before finalizing a PR with visual changes, request a **comprehensive design review** via the `@agent-design-review` sub‑agent (if available).

---

## Working Mode & Output Expectations

Follow Anthropic’s recommended **explore → plan → code → verify → commit** loop.

1. **Explore (read first):** Identify relevant files; explain the approach. Avoid writing code until you understand the repo pieces you’ll change.
2. **Plan:** Propose a concise step list of edits and tests. Call out risks and edge cases.
3. **Code:** Make minimal, targeted edits. Prefer small, composable changes.
4. **Verify:** Run linters/tests locally; do the **Quick Visual Check** for UI changes.
5. **Commit:** Use descriptive messages, reference issues/tasks, and update **`.claude/Context/CHANGELOG.md`**.
6. **Document:** If a new workflow or command emerges, add it to this file or the `.claude` context (see “Maintaining this File”).

**Output formatting**
- When asked to modify files, prefer **patch‑style** or **small, focused code blocks**; include full file only if necessary.
- Provide **shell commands** to run (copy‑paste‑able). Mark dangerous commands clearly.
- **Do not** hard‑code values for one‑off test inputs—implement general logic.
- Keep changes **idempotent** and **re-runnable** (e.g., migrations, scripts).

**Safety & secrets**
- Never commit real secrets or credentials.
- Use environment variables and `.env` (see “Environment Setup”). Place sensitive files outside VCS.

---

## Tool Permissions, MCP, and Commands

- Curate tool permissions via **`/permissions`** or project config to pre‑allow safe operations (e.g., file edits, `git commit`, Playwright/Puppeteer navigation tools if present).
- If using GitHub, install **`gh` CLI**; Claude can open PRs, issues, and read comments.
- If available, configure MCP servers (e.g., Playwright or Puppeteer) in `.mcp.json` or project config so navigation/screenshot tools are ready for all contributors.
- Create **custom slash commands** by adding Markdown prompt files to **`.claude/commands`** (use `$ARGUMENTS` for parameters).

**Example custom command file**: `.claude/commands/fix-github-issue.md`
```
Please analyze and fix the GitHub issue: $ARGUMENTS.

Steps:
1) Use `gh issue view` to get details.
2) Locate relevant files; propose a plan first.
3) Implement changes; write/rerun tests.
4) Ensure linting & type checks pass.
5) Commit with a descriptive message.
6) Push and open a PR using `gh`.
```
This becomes `/project:fix-github-issue 1234` in Claude Code.

---

## Code Style Guidelines

- **Python**: Follow **PEP 8** (4‑space indent, descriptive naming, ≤ 88–100 cols). Prefer explicit imports; type hints where helpful.
- **JavaScript/Vue**: Use **ES modules**, `let`/`const`, Vue 3 **Composition API**, and adhere to project ESLint rules.
- Keep functions small and focused; avoid duplication; write clear comments where intent isn’t obvious.

## Testing & Linting

- **Backend tests**: `python manage.py test` — must pass before commit/PR.
- **Frontend lint**: `npm run lint` — fix all issues before commit/PR.
- For UI changes, include **before/after screenshots** (see Visual Development).

---

## Development Commands

### Backend (`wanderapp_backend/`)
- Start dev server: `python manage.py runserver 0.0.0.0:8000` (from within venv)
- Activate venv: `source venv/bin/activate` (in backend directory)
- Install deps: `pip install -r requirements.txt`
- Migrate: `python manage.py migrate`
- Make migrations: `python manage.py makemigrations`
- Run tests: `python manage.py test`
- Create superuser: `python manage.py createsuperuser`

### Frontend (`wanderapp-frontend/`)
- Start dev server: `npm run serve` (port 8080)
- Build: `npm run build`
- Lint: `npm run lint`
- Install deps: `npm install`

### Development Workflow
1) Start backend: `cd wanderapp_backend && source venv/bin/activate && python manage.py runserver 0.0.0.0:8000`  
2) Start frontend: `cd wanderapp-frontend && npm run serve`  
3) App: `http://localhost:8080`

---

## Architecture

### Backend
- **Framework**: Django 4.2 + DRF
- **Database**: PostgreSQL + **PostGIS**
- **Auth**: JWT via `djangorestframework_simplejwt`
- **Images**: Pillow (`api/image_processing.py`)
- **Config**: Env vars via **python‑decouple** (`.env`)
- **Countries**: `django-countries` (surf trips)
- **GPX**: `gpxpy` for parsing & metrics
- **Prod**: **Gunicorn**

**Key Models** (`api/models.py`)
- `User` — email auth; `is_quick_user` for simplified onboarding
- `Trip` — has `activity_type` (HIKING/SURFING), participants (M2M), `country` (surf)
- `Stage` — child of Trip, with activity‑specific fields  
  **Hiking fields:** duration (manual/calculated), distance, elevation gain/loss, external_link  
  **Surf fields:** surf_spot, time_in_water, surfboard_used, wave_height, wave_quality, water_temperature, waves_caught, tide_stage, tide_movement, swell_direction, wind_direction, wave_energy
- `Photo` — multiple versions (original/display/thumbnail/WebP) + dimensions
- `TrackPoint` — PostGIS `PointField(geography=True, srid=4326)`
- `Hut` — accommodation
- `Comment` — author, text, timestamp

**Key API Structure**
- `api/views.py` — ViewSets + custom endpoints  
  `TripViewSet` (subquery annotations), `StageViewSet` (incl. `upload_photos`), `UserViewSet` (`me`, `quick_create`, `search`), `PhotoViewSet` (cascaded deletions), `UserStatsView`, `DashboardDataView`, `CountriesAPIView`, `search_suggestions`, `calculate_gpx_metrics`
- `api/serializers.py` — `TripListSerializer` (light), `TripDetailSerializer` (nested stages), `StageSerializer` (activity fields + photos/comments)
- `api/permissions.py` — `IsCreatorOrReadOnly`, `IsAuthorOrStageCreatorOrAdmin`
- `api/pagination.py` — `StandardResultsSetPagination` (default 10; `page_size=none` supported)
- `api/filters.py` — rich `TripFilter` (hiking metrics, surf conditions, general filters)
- `api/image_processing.py` — EXIF rotation, sRGB conversion, multi‑format outputs, dimension calc
- `api/urls.py` — router + custom paths

### Frontend
- **Vue 3 (Composition API)**, **Vue Router 4** (auth guards, dynamic titles)
- **Axios** with JWT interceptors + refresh queue (`src/api.js`)
- **Mapbox GL JS** for GPS visualization
- **Uppy** for uploads; **PhotoSwipe** for lightbox
- **gpxparser** for GPX parsing
- **Playwright** for E2E tests

**Key Components** (`src/components/`)
- **Trip Management:** `TripList.vue`, `TripDetail.vue`, `TripCreate.vue`, `TripEdit.vue`
- **Hiking:** `StageCreate.vue`, `StageEdit.vue`, `HikeMap.vue`, `HikingAdvancedSearch.vue`
- **Surfing:** `SurfStageCreate.vue`, `SurfStageEdit.vue`
- **UI:** `UserDashboard.vue`, `LoginView.vue`, `AuthNotification.vue`
- **Shared:** `ImageUploader.vue`, `ParticipantSelector.vue`, `MultiSelectDropdown.vue`, `CommentSection.vue`, `AdvancedSearch.vue`, `ProcessedText.vue`

**Design System** (`src/components/base/`)  
`BaseBadge.vue`, `BaseButton.vue`, `BaseCard.vue`, `BaseInput.vue`, `BaseModal.vue`

**Styling** (`src/styles/`)  
`base.css`, `tokens.css`

**Configuration**  
`vue.config.js` (proxy `/api` & `/media` → backend :8000), `src/router.js`, `src/store.js`, `src/api.js`

---

## Environment Setup

### Backend `.env` (in `wanderapp_backend/`)
Required:
- `SECRET_KEY`, `DEBUG`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `SERVER_IP`
- `USE_HTTPS` (enables SSL redirect, secure cookies, etc.)
- `GDAL_LIBRARY_PATH`, `GEOS_LIBRARY_PATH`

**Example:**
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=wanderapp_db
DB_USER=wanderapp_user
DB_PASSWORD=your-password
SERVER_IP=192.168.1.100
USE_HTTPS=False
GDAL_LIBRARY_PATH=/opt/homebrew/lib/libgdal.dylib
GEOS_LIBRARY_PATH=/opt/homebrew/lib/libgeos_c.dylib
```

### System Dependencies
- **macOS:** GDAL/GEOS via Homebrew (`/opt/homebrew/lib/`)
- **Ubuntu:** `libgdal-dev`, `libgeos-dev` (`/usr/lib/x86_64-linux-gnu/`)
- **Node.js:** Use **NVM**
- **PostgreSQL:** With **PostGIS**

---

## Key Technical Details

### Database Highlights
- PostGIS for GPS tracks: `PointField(geography=True, srid=4326)`
- Custom User (`USERNAME_FIELD='email'`); `is_quick_user`
- M2M participants; nested relations Trip → Stage → (Photo/TrackPoint/Comment)
- Activity separation (HIKING/SURFING) with dedicated fields
- `django-countries` for surf trip locations
- Validators (e.g., `wave_quality` 1–5)

### Image Pipeline (`api/image_processing.py`)
- EXIF rotation correction
- sRGB conversion
- Multi‑format generation (original, thumbnails, WebP)
- Original dimension calculation after rotation

### API Design
- RESTful endpoints; nested serialization
- JWT auth (access ~60 min, refresh ~1 day)
- Two‑tier serializers (`TripListSerializer` vs `TripDetailSerializer`)
- Subquery annotations to prevent duplication
- Manual vs calculated hiking metrics (manual preferred)
- Activity‑specific aggregations (hiking: distance/elevation; surfing: time/waves/spots)

**Main Endpoints**
- **Auth:** `POST /api/token/`, `POST /api/token/refresh/`
- **Trips:** `GET/POST /api/trips/`, `GET/PUT/PATCH/DELETE /api/trips/{id}/`
- **Stages:** `GET/POST /api/stages/`, `GET/PUT/PATCH/DELETE /api/stages/{id}/`, `POST /api/stages/{id}/upload_photos/`
- **Photos:** `GET /api/photos/`, `GET/DELETE /api/photos/{id}/`
- **Comments:** `GET/POST /api/comments/`, `DELETE /api/comments/{id}/`
- **Users:** `GET /api/users/`, `GET /api/users/me/`, `POST /api/users/quick_create/`, `GET /api/users/search/?q=<q>`
- **Statistics:** `GET /api/stats/`, `GET /api/stats/{id}/`, `GET /api/dashboard-data/`, `GET /api/dashboard-data/{id}/`
- **Surf‑specific:** `GET /api/countries/`, `GET /api/search-suggestions/?q=<q>`
- **Utilities:** `POST /api/calculate-gpx/`, `GET /api/huts/`

**Filtering & Pagination**
- `page`, `page_size` (use `page_size=none` to disable pagination)
- 20+ TripFilter fields (activity_type, participants, date ranges, hiking metrics, surf conditions)

### Frontend ↔ Backend Integration
- Dev proxy: `/api` and `/media` → `http://localhost:8000`
- JWT in `localStorage` with refresh queue; centralized logout
- CORS: dynamic origins based on `SERVER_IP` + `USE_HTTPS`
- Router guards for auth operations; dynamic titles via route meta

### Frontend Routes
- `/login`, `/`, `/hiking`, `/surfing`
- `/trip/new`, `/trip/:id`, `/trip/:id/edit`
- `/trip/:tripId/add-stage`, `/trip/:tripId/add-surf-stage`
- `/stage/:id/edit`, `/surf-stage/:id/edit`
- `/dashboard/:id?`

---

## Dependencies

### Backend (`requirements.txt`)
- **Core:** `Django==4.2.23`, `djangorestframework==3.16.1`, `psycopg2-binary==2.9.10`, `django.contrib.gis`
- **Auth/Sec:** `djangorestframework_simplejwt==5.5.1`, `PyJWT==2.10.1`, `bcrypt==4.3.0`
- **Geo/Filter:** `djangorestframework-gis==1.2.0`, `django-filter==25.1`, `gpxpy==1.6.2`
- **Location/Images:** `django-countries==7.6.1`, `pillow==11.3.0`, `django-cors-headers==4.7.0`
- **Config/Prod:** `python-decouple==3.8`, `gunicorn==23.0.0`
- **Utils:** `asgiref==3.9.1`, `sqlparse==0.5.3`, `packaging==25.0`, `typing-extensions==4.15.0`

### Frontend (`package.json`)
- **Core:** `vue@3.2.13`, `vue-router@4.5.1`, `axios@1.11.0`, `core-js@3.8.3`
- **Maps/GPX:** `mapbox-gl@3.14.0`, `gpxparser@3.0.8`
- **Photos:** `@uppy/*@5.x`, `photoswipe@5.4.4`
- **Dev:** `@vue/cli-service@5.0.0`, `@vue/cli-plugin-babel@5.0.9`, `@vue/cli-plugin-eslint@5.0.9`, `eslint@8.57.0`, `eslint-plugin-vue@9.26.0`, `@babel/eslint-parser@7.24.7`, `vue-eslint-parser@9.4.3`
- **Testing:** `@playwright/test@1.55.1`, `@types/node@24.6.0`

---

## Additional Project Files

**Root**
- `CLAUDE.md` (this file)
- `README.md`
- `CHANGELOG.md`
- `DESIGN_SYSTEM_GUIDE.md`
- `surf-tracking.md`
- `.gitignore`

**Backend**
- `wanderapp_backend/.env` (not in git)
- `wanderapp_backend/manage.py`
- `wanderapp_backend/create_hiking_trips.py`
- `wanderapp_backend/create_more_trips.py`
- `wanderapp_backend/track.gpx`
- `wanderapp_backend/venv/` (not in git)
- `wanderapp_backend/media/` (not in git)

**Frontend**
- `wanderapp-frontend/.eslintrc.js`, `babel.config.js`, `jsconfig.json`
- `wanderapp-frontend/playwright.config.ts`
- `wanderapp-frontend/tests/`, `tests-examples/`
- `wanderapp-frontend/.github/` (workflows/actions)

**Claude Code Configuration**
- `.claude/` — project config
- `.claude/Context/DESIGN_SYSTEM_GUIDE.md` — **Frontend design system (MUST follow)**
- `.claude/Context/CHANGELOG.md` — **Project changelog (MUST update)**
- `.claude/Context/security_assessment.txt` — Security notes
- `.claude/Agents/` — custom agent definitions (e.g., `@agent-design-review`)
- `.claude/commands/` — custom slash commands
- `.claude/settings.local.json` — local settings

---

## Production Considerations

- Replace `runserver` with **Gunicorn**; put **Nginx** in front for static/media and reverse proxy.
- Build frontend: `npm run build` (optimized bundle).
- Production `.env`: `DEBUG=False`, `USE_HTTPS=True`.
- SSL/HTTPS when `USE_HTTPS=True`:
  - `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')`
  - `SECURE_SSL_REDIRECT = True`
  - `SESSION_COOKIE_SECURE = True`
  - `CSRF_COOKIE_SECURE = True`
  - CORS origins include HTTPS variants.
- `python manage.py collectstatic` (serve via Nginx); media via Nginx.
- Environment‑specific `ALLOWED_HOSTS`.

---

## Surfing Feature Details

**Model**
- Trip `country` (django‑countries) for surf location
- Surf stage fields: spot, surfboard, wave conditions (height, quality, energy), water temperature, tide (stage/movement), wind/swell direction, waves caught, time in water

**UI**
- `SurfStageCreate.vue`, `SurfStageEdit.vue` (surf forms)
- Filters/search by location/spot/conditions
- Dashboard surf stats & records
- Autocomplete for surf spots/boards
- Tide/wind/swell selectors

**Metrics**
- Total time in water; total waves caught
- Unique surf spots; water temp min/max/avg
- Wave quality rating (1–5); most used board type

**Integration**
- Activity filter across app (`/hiking`, `/surfing`)
- Unified trip list with activity badges
- Activity‑specific dashboard stats
- Combined cross‑activity search

---

## CI & Automation (optional but recommended)

- Use **Claude Code headless mode** for CI or automation (e.g., triage issues, subjective linting).  
  Example: `claude -p "<prompt here>" --output-format stream-json`
- Consider a GitHub Action that:
  - Runs tests & linters on PRs
  - Invokes headless Claude for **issue triage** or **subjective review** (naming/message clarity, stale comments, etc.)

---

## Maintaining this File

- This file is part of the prompt context. **Iterate** on it as a prompt:
  - Keep it **concise and human‑readable**.
  - Use strong emphasis (like **IMPORTANT**/**YOU MUST**) where adherence matters.
  - Update when you discover better instructions/workflows.
- Use the `#` shortcut in Claude Code to quickly add reminders; include `CLAUDE.md` changes in commits so teammates benefit.
