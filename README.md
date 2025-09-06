# WanderApp - Technische Dokumentation

**Version 1.0 - Stand: 06. September 2025**

## 1. Einleitung & Übersicht

Dieses Dokument beschreibt die technische Architektur und die wichtigsten Konzepte der Wander-App. Es dient als Nachschlagewerk für zukünftige Wartungs- und Erweiterungsarbeiten, insbesondere für den Umzug der Entwicklungsumgebung und die Vorbereitung auf einen produktiven Einsatz.

### 1.1. Kerntechnologien

Die Anwendung ist als moderne "Single Page Application" (SPA) mit getrenntem Backend und Frontend aufgebaut:

* **Backend:**
    * **Framework:** Django & Django REST Framework
    * **Datenbank:** PostgreSQL mit PostGIS-Erweiterung für Geodaten
    * **API-Stil:** RESTful API
    * **Authentifizierung:** JSON Web Tokens (JWT)
    * **Bildverarbeitung:** Pillow
    * **Abhängigkeiten:** `requirements.txt`

* **Frontend:**
    * **Framework:** Vue.js 3 (mit Composition API)
    * **HTTP-Client:** Axios
    * **Karten-Darstellung:** Mapbox GL JS
    * **Bilder-Upload:** Uppy
    * **Bilder-Galerie (Lightbox):** PhotoSwipe
    * **Abhängigkeiten:** `package.json`

---

## 2. Backend-Architektur (`wanderapp_backend`)

Das Backend basiert auf dem **Django REST Framework** und dient als reine API ("headless"), die JSON-Daten bereitstellt. Es hat keine eigenen Ansichten für den Benutzer, sondern kommuniziert ausschliesslich mit dem Frontend.

### 2.1. Konfigurations-Dateien & Konzept

Die Konfiguration ist so aufgebaut, dass sie auf verschiedenen Systemen (macOS, Ubuntu) ohne Code-Änderungen lauffähig ist.

#### `wanderapp_backend/settings.py`

Dies ist die zentrale Konfigurationsdatei von Django. Sie wurde angepasst, um alle maschinenspezifischen und sensiblen Daten aus einer separaten `.env`-Datei zu laden.

* **Wichtigste Anpassung:** Alle variablen Werte (z.B. `SECRET_KEY`, Datenbank-Passwörter, Pfade) werden mit `config('VARIABLEN_NAME')` geladen.
* **Netzwerk-Konfiguration:** Die `ALLOWED_HOSTS` und `CORS_ALLOWED_ORIGINS` werden dynamisch aus der `SERVER_IP` in der `.env`-Datei aufgebaut, um Zugriffe aus dem lokalen Netzwerk zu ermöglichen.

#### `.env`-Datei (Beispiel für Ubuntu)

Diese Datei liegt im Hauptverzeichnis des Backends (`wanderapp_backend/`) und darf **niemals auf GitHub hochgeladen werden**. Sie enthält die "Geheimnisse" und systemabhängigen Pfade.

```
# .env file for Ubuntu

# Django Settings
SECRET_KEY=Ihr_geheimer_Schlüssel_hier
DEBUG=True

# Database Settings
DB_NAME=wanderapp_db
DB_USER=wanderapp_user
DB_PASSWORD=Ihr_sicheres_Datenbankpasswort

# Netzwerk
SERVER_IP=192.168.178.58 # Die IP des Ubuntu-Rechners

# Library Paths for Ubuntu
GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so.1
```

```
# .env file for Ubuntu

# Django Settings
SECRET_KEY=Ihr_geheimer_Schlüssel_hier
DEBUG=True

# Database Settings
DB_NAME=db_name
DB_USER=user
DB_PASSWORD=Ihr_sicheres_Datenbankpasswort

# Netzwerk
SERVER_IP=192.168.178.58 # Die IP des Ubuntu-Rechners

# Library Paths for Ubuntu
GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so.1
```
```
# .env file for macOS

# Django Settings
SECRET_KEY=django-insecure-dummy-key-for-development
DEBUG=True

# Database Settings
DB_NAME=db_name
DB_USER=user
DB_PASSWORD=Ihr_sicheres_Datenbankpasswort

SERVER_IP=192.168.178.65

# Library Paths for macOS
GDAL_LIBRARY_PATH=/opt/homebrew/lib/libgdal.dylib
GEOS_LIBRARY_PATH=/opt/homebrew/lib/libgeos_c.dylib
```

**Anpassung bei Umzug:** Dies ist die **einzige Datei**, die Sie anpassen müssen, wenn Sie das Projekt auf einen neuen Server oder Rechner umziehen.

### 2.2. Kern-Logik der `api`-App

#### `api/models.py`

Definiert die "Blaupausen" für Ihre Datenbank-Tabellen. Jede Klasse entspricht einer Tabelle.
* `Trip`: Das Hauptobjekt. Enthält Name, Datum und eine `ManyToManyField` zu `User` für die Teilnehmer.
* `Stage`: Eine Etappe, die immer zu einem `Trip` gehört (`ForeignKey`). Enthält die Etappen-Details wie Distanz, Höhenmeter etc.
* `Photo`: Ein Foto, das immer zu einer `Stage` gehört (`ForeignKey`). Enthält Pfade zu den verschiedenen Bildversionen und die vom Backend berechneten Original-Dimensionen (`original_width`, `original_height`).
* `Comment`, `Hut`, `TrackPoint`: Weitere Datenmodelle, die jeweils mit einer Etappe oder einem Trip verknüpft sind.

#### `api/serializers.py`

Diese Dateien sind die "Übersetzer" zwischen den Python-Objekten aus der Datenbank und dem JSON-Format, das die API sendet.
* Für jedes Modell (z.B. `Trip`) gibt es einen `TripSerializer`.
* **Wichtige Logik:** Der `StageSerializer` enthält eine "verschachtelte" `PhotoSerializer`-Instanz. Dies sorgt dafür, dass, wenn eine Etappe abgefragt wird, die Informationen zu allen zugehörigen Fotos direkt mitgeliefert werden.

#### `api/views.py`

Hier befindet sich die "Denk"-Logik Ihrer API. Jede Klasse (`...ViewSet` oder `...View`) ist ein Endpunkt, den das Frontend ansprechen kann.
* `TripViewSet`: Stellt die Endpunkte für Trips bereit (`/api/trips/`). Enthält die Logik zur Berechnung der Gesamtstatistiken (`total_distance` etc.) für die Listenansicht.
* `StageViewSet`: Stellt die Endpunkte für Etappen bereit. Enthält eine spezielle `@action` namens `upload_photos`, die nur für den Foto-Upload zuständig ist.
* `UserStatsView`: Der Endpunkt für die "Total"-Kacheln im Dashboard. Berechnet die Gesamt-Statistiken für einen bestimmten Benutzer.
* `DashboardDataView`: Der Endpunkt für die "Persönlichen Rekorde" und "Top Wanderpartner".

#### `api/image_processing.py`

Ein dediziertes Hilfsmodul, das die gesamte Logik für die Bildverarbeitung enthält.
* **Funktion `process_and_save_photo`:**
    1.  Nimmt eine hochgeladene Datei entgegen.
    2.  Liest die EXIF-Daten und rotiert das Bild korrekt.
    3.  Konvertiert das Bild in den sRGB-Farbraum, um Farb-Konsistenz zu gewährleisten.
    4.  Liest die **korrekten Dimensionen nach der Rotation** aus.
    5.  Speichert das normalisierte Original und erstellt und speichert die kleineren Derivate (Thumbnails, WebP).

---

## 3. Frontend-Architektur (`wanderapp-frontend`)

Das Frontend ist eine Vue.js 3-Anwendung, die im Browser des Benutzers läuft.

### 3.1. Konfigurations-Dateien

#### `vue.config.js`

Diese Datei konfiguriert den Vue-Entwicklungsserver.
* **Wichtigste Funktion:** Der `proxy`. Er leitet alle Anfragen, die im Frontend an `/api/...` oder `/media/...` gehen, an den lokalen Backend-Server (`http://localhost:8000`) weiter. Dies umgeht alle CORS-Netzwerkprobleme während der Entwicklung.
* `allowedHosts: 'all'`: Erlaubt den Zugriff auf den Entwicklungsserver von anderen Geräten im selben Netzwerk (z.B. Ihrem iPhone).

#### `src/api.js`

Dies ist die zentrale Datei für die gesamte Backend-Kommunikation.
* **Axios-Instanz:** Erstellt eine einzige, wiederverwendbare `axios`-Instanz.
* **`baseURL: '/api'`**: Weist alle Anfragen an, den relativen Pfad `/api` zu verwenden. Der Proxy in `vue.config.js` fängt dies ab und leitet es korrekt weiter.
* **Interceptors:**
    * Ein "Request Interceptor" fügt bei jeder ausgehenden Anfrage automatisch den `Authorization`-Header mit dem JWT-Token hinzu.
    * Ein "Response Interceptor" fängt `401 Unauthorized`-Fehler ab und versucht, mit dem `refreshToken` automatisch einen neuen `accessToken` zu holen, was den Benutzer eingeloggt hält.

#### `src/router.js`

Definiert die "Seiten" Ihrer App und welche Komponente für welche URL zuständig ist.
* Beispiel: `path: '/trip/:id'` ist mit der `TripDetail.vue`-Komponente verknüpft.
* **Navigation Guard (`router.beforeEach`):** Eine globale Sicherheitsfunktion, die vor jedem Seitenwechsel prüft, ob der Benutzer eingeloggt ist. Wenn nicht, wird er automatisch zur `/login`-Seite weitergeleitet.

### 3.2. Wichtige Komponenten

* `TripList.vue`: Die Hauptansicht mit der Filterleiste und der Liste aller Trips.
* `TripDetail.vue`: Die Detailansicht eines Trips, die alle Etappen, Kommentare und Fotos anzeigt.
* `UserDashboard.vue`: Die Dashboard-Ansicht mit den persönlichen Statistiken und Rekorden.
* `ImageUploader.vue`: Kapselt die gesamte Logik für die `Uppy`-Bibliothek. Sie wird als Pop-up (Modal) konfiguriert und sendet die Dateien an den korrekten Endpunkt. Bei Erfolg sendet sie ein `upload-success`-Event an die Eltern-Komponente.
* `MultiSelectDropdown.vue`: Eine von uns erstellte, wiederverwendbare Komponente für eine benutzerfreundliche Mehrfachauswahl mit Checkboxen, die in der Filterleiste verwendet wird.

---

## 4. Umzug der Entwicklungsumgebung (z.B. von Mac auf Ubuntu)

Dieser Prozess beschreibt, wie Sie Ihr komplettes Projekt inklusive aller Daten auf einen neuen Rechner umziehen.

### Schritt 1: Daten auf dem alten Rechner sichern
1.  **Datenbank-Backup:** Erstellen Sie ein Backup Ihrer PostgreSQL-Datenbank.
    ```bash
    pg_dump -U IHR_BENUTZERNAME -d wanderapp_db -F c -b -v -f wanderapp_db_backup.sql
    ```
2.  **Medien-Backup:** Komprimieren Sie Ihren `media`-Ordner.
    ```bash
    # Im Ordner wanderapp_backend
    tar -czvf media_backup.tar.gz media/
    ```
3.  Übertragen Sie die beiden Dateien (`wanderapp_db_backup.sql` und `media_backup.tar.gz`) auf den neuen Rechner.

### Schritt 2: Neuen Rechner vorbereiten
1.  **System-Abhängigkeiten installieren:**
    ```bash
    # Für Ubuntu
    sudo apt update && sudo apt upgrade -y
    sudo apt install git python3-pip python3-venv build-essential postgresql postgis libgdal-dev libgeos-dev proj-bin libproj-dev postgresql-server-dev-all -y
    ```
2.  **Node.js installieren (via NVM):**
    ```bash
    curl -o- [https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh](https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh) | bash
    # Terminal schliessen und neu öffnen
    nvm install --lts
    ```

### Schritt 3: Datenbank auf dem neuen Rechner aufsetzen
1.  **Datenbank und Benutzer erstellen:**
    ```bash
    sudo -u postgres psql
    ```
    Im `psql`-Prompt:
    ```sql
    CREATE USER wanderapp_user WITH PASSWORD 'IHR_NEUES_PASSWORT';
    ALTER USER wanderapp_user SUPERUSER; -- Temporär für die Installation von PostGIS
    CREATE DATABASE wanderapp_db OWNER wanderapp_user;
    \q
    ```
2.  **PostGIS-Erweiterung aktivieren:**
    ```bash
    sudo -u postgres psql -d wanderapp_db -c "CREATE EXTENSION postgis;"
    ```
3.  **Datenbank-Backup wiederherstellen:**
    ```bash
    pg_restore --no-owner -U wanderapp_user -d wanderapp_db -v ~/wanderapp_db_backup.sql
    ```
4.  **Superuser-Rechte wieder entziehen (Sicherheit):**
    ```bash
    sudo -u postgres psql -c "ALTER USER wanderapp_user NOSUPERUSER;"
    ```

### Schritt 4: Projekte auf dem neuen Rechner einrichten
1.  **Code von GitHub klonen:** Klonen Sie beide Repositories (`wanderapp_backend` und `wanderapp-frontend`).
2.  **Backend einrichten:**
    * Erstellen und aktivieren Sie die virtuelle Umgebung (`python3 -m venv venv`, `source venv/bin/activate`).
    * Erstellen Sie eine neue `.env`-Datei mit den systemspezifischen Werten (Datenbank-Passwort, Pfade zu GDAL/GEOS, IP-Adresse des neuen Rechners).
    * Installieren Sie die Abhängigkeiten: `pip install -r requirements.txt`.
    * Führen Sie `python3 manage.py migrate` aus.
    * Entpacken Sie `media_backup.tar.gz` in den Projektordner.
3.  **Frontend einrichten:**
    * Installieren Sie die Abhängigkeiten: `npm install`.

### Schritt 5: Server starten
* **Backend:** `python3 manage.py runserver 0.0.0.0:8000`
* **Frontend:** `npm run serve`

---

## 5. Produktivsetzung (Deployment)

Der aktuelle Zustand ist ein **Entwicklungs-Setup**. Für einen Live-Betrieb im Internet sind zusätzliche Schritte notwendig. Hier ist eine Übersicht des professionellen Vorgehens:

1.  **Server:** Sie benötigen einen Server (z.B. einen "Droplet" bei DigitalOcean oder eine "EC2-Instanz" bei AWS).
2.  **Backend-Server (Gunicorn):** Der `manage.py runserver` ist unsicher und ineffizient. Er wird durch einen professionellen Applikations-Server wie **Gunicorn** ersetzt.
    * Startbefehl: `gunicorn --bind 0.0.0.0:8000 wanderapp_backend.wsgi`
3.  **Web-Server (Nginx):** Ein Web-Server wie **Nginx** wird vor Gunicorn geschaltet. Er ist extrem schnell und übernimmt folgende Aufgaben:
    * **Proxy:** Leitet API-Anfragen (`/api/`) an Gunicorn weiter.
    * **Auslieferung von Dateien:** Liefert die Frontend-Dateien, Bilder (`/media/`) und CSS/JS (`/static/`) direkt aus, was Gunicorn entlastet.
    * **Sicherheit & SSL:** Kümmert sich um HTTPS-Verschlüsselung (mit Let's Encrypt).
4.  **Frontend-Build:** Sie führen `npm run build` im Frontend aus. Dies erstellt eine hochoptimierte, statische Version Ihrer App, die dann von Nginx ausgeliefert wird.
5.  **Datenbank:** Die PostgreSQL-Datenbank läuft als eigener Dienst auf dem Server.
6.  **`.env`-Datei:** Auf dem Produktions-Server wird eine `.env`-Datei mit den Produktions-Einstellungen angelegt (`DEBUG=False`, Produktions-Datenbank-Passwort, etc.).
7.  **Prozess-Management (Systemd):** Ein Tool wie `systemd` stellt sicher, dass Ihr Gunicorn-Prozess automatisch startet und bei einem Absturz neu gestartet wird.

Ein Wechsel in die Produktion ist ein grosses Thema, aber diese Übersicht zeigt Ihnen die wichtigsten Komponenten und den Weg dorthin.
