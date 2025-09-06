Technische Dokumentation: WanderApp (Erweitert)
Version 1.0 - Stand: 06. September 2025

1. Einleitung & Übersicht
(Dieser Teil bleibt wie in der vorherigen Version)

2. Backend-Architektur (wanderapp_backend)
Das Backend basiert auf dem Django REST Framework und dient als reine API ("headless"), die JSON-Daten bereitstellt. Es hat keine eigenen Ansichten für den Benutzer, sondern kommuniziert ausschliesslich mit dem Frontend.

2.1. Konfigurations-Dateien & Konzept

Die Konfiguration ist so aufgebaut, dass sie auf verschiedenen Systemen (macOS, Ubuntu) ohne Code-Änderungen lauffähig ist.

wanderapp_backend/settings.py

Dies ist die zentrale Konfigurationsdatei von Django. Sie wurde angepasst, um alle maschinenspezifischen und sensiblen Daten aus einer separaten .env-Datei zu laden.

Wichtigste Anpassung: Alle variablen Werte (z.B. SECRET_KEY, Datenbank-Passwörter, Pfade) werden mit config('VARIABLEN_NAME') geladen.

Netzwerk-Konfiguration: Die ALLOWED_HOSTS und CORS_ALLOWED_ORIGINS werden dynamisch aus der SERVER_IP in der .env-Datei aufgebaut, um Zugriffe aus dem lokalen Netzwerk zu ermöglichen.

.env-Datei (Beispiel für Ubuntu)

Diese Datei liegt im Hauptverzeichnis des Backends (wanderapp_backend/) und darf niemals auf GitHub hochgeladen werden. Sie enthält die "Geheimnisse" und systemabhängigen Pfade.

# .env file for macOS

# Django Settings
SECRET_KEY=django-insecure-dummy-key-for-development
DEBUG=True

# Database Settings
DB_NAME=wanderapp_db
DB_USER=fabian
DB_PASSWORD=hyqjy1-paGcex-puqxim

SERVER_IP=192.168.178.65

# Library Paths for macOS
GDAL_LIBRARY_PATH=/opt/homebrew/lib/libgdal.dylib
GEOS_LIBRARY_PATH=/opt/homebrew/lib/libgeos_c.dylib


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
Anpassung bei Umzug: Dies ist die einzige Datei, die Sie anpassen müssen, wenn Sie das Projekt auf einen neuen Server oder Rechner umziehen.

2.2. Kern-Logik der api-App

api/models.py

Definiert die "Blaupausen" für Ihre Datenbank-Tabellen. Jede Klasse entspricht einer Tabelle.

Trip: Das Hauptobjekt. Enthält Name, Datum und eine ManyToManyField zu User für die Teilnehmer.

Stage: Eine Etappe, die immer zu einem Trip gehört (ForeignKey). Enthält die Etappen-Details wie Distanz, Höhenmeter etc.

Photo: Ein Foto, das immer zu einer Stage gehört (ForeignKey). Enthält Pfade zu den verschiedenen Bildversionen und die vom Backend berechneten Original-Dimensionen (original_width, original_height).

Comment, Hut, TrackPoint: Weitere Datenmodelle, die jeweils mit einer Etappe oder einem Trip verknüpft sind.

api/serializers.py

Diese Dateien sind die "Übersetzer" zwischen den Python-Objekten aus der Datenbank und dem JSON-Format, das die API sendet.

Für jedes Modell (z.B. Trip) gibt es einen TripSerializer.

Wichtige Logik: Der StageSerializer enthält eine "verschachtelte" PhotoSerializer-Instanz. Dies sorgt dafür, dass, wenn eine Etappe abgefragt wird, die Informationen zu allen zugehörigen Fotos direkt mitgeliefert werden.

api/views.py

Hier befindet sich die "Denk"-Logik Ihrer API. Jede Klasse (...ViewSet oder ...View) ist ein Endpunkt, den das Frontend ansprechen kann.

TripViewSet: Stellt die Endpunkte für Trips bereit (/api/trips/). Enthält die Logik zur Berechnung der Gesamtstatistiken (total_distance etc.) für die Listenansicht.

StageViewSet: Stellt die Endpunkte für Etappen bereit. Enthält eine spezielle @action namens upload_photos, die nur für den Foto-Upload zuständig ist.

UserStatsView: Der Endpunkt für die "Total"-Kacheln im Dashboard. Berechnet die Gesamt-Statistiken für einen bestimmten Benutzer.

DashboardDataView: Der Endpunkt für die "Persönlichen Rekorde" und "Top Wanderpartner".

api/image_processing.py

Ein dediziertes Hilfsmodul, das die gesamte Logik für die Bildverarbeitung enthält.

Funktion process_and_save_photo:

Nimmt eine hochgeladene Datei entgegen.

Liest die EXIF-Daten und rotiert das Bild korrekt.

Konvertiert das Bild in den sRGB-Farbraum, um Farb-Konsistenz zu gewährleisten.

Liest die korrekten Dimensionen nach der Rotation aus.

Speichert das normalisierte Original und erstellt und speichert die kleineren Derivate (Thumbnails, WebP).

3. Frontend-Architektur (wanderapp-frontend)
Das Frontend ist eine Vue.js 3-Anwendung, die die vom Backend gelieferten Daten im Browser des Benutzers darstellt.

3.1. Konfigurations-Dateien

vue.config.js

Diese Datei konfiguriert den Vue-Entwicklungsserver.

Wichtigste Funktion: Der proxy. Er leitet alle Anfragen, die im Frontend an /api/... oder /media/... gehen, an den lokalen Backend-Server (http://localhost:8000) weiter. Dies umgeht alle CORS-Netzwerkprobleme während der Entwicklung.

allowedHosts: 'all': Erlaubt den Zugriff auf den Entwicklungsserver von anderen Geräten im selben Netzwerk (z.B. Ihrem iPhone).

src/api.js

Dies ist die zentrale Datei für die gesamte Backend-Kommunikation.

Axios-Instanz: Erstellt eine einzige, wiederverwendbare axios-Instanz.

baseURL: '/api': Weist alle Anfragen an, den relativen Pfad /api zu verwenden. Der Proxy in vue.config.js fängt dies ab und leitet es korrekt weiter.

Interceptors:

Ein "Request Interceptor" fügt bei jeder ausgehenden Anfrage automatisch den Authorization-Header mit dem JWT-Token hinzu.

Ein "Response Interceptor" fängt 401 Unauthorized-Fehler ab und versucht, mit dem refreshToken automatisch einen neuen accessToken zu holen, was den Benutzer eingeloggt hält.

src/router.js

Definiert die "Seiten" Ihrer App und welche Komponente für welche URL zuständig ist.

Beispiel: path: '/trip/:id' ist mit der TripDetail.vue-Komponente verknüpft.

Navigation Guard (router.beforeEach): Eine globale Sicherheitsfunktion, die vor jedem Seitenwechsel prüft, ob der Benutzer eingeloggt ist. Wenn nicht, wird er automatisch zur /login-Seite weitergeleitet.

3.2. Wichtige Komponenten

TripDetail.vue: Eine komplexe Komponente, die viele Unter-Komponenten wie HikeMap.vue, ImageUploader.vue und CommentSection.vue verwendet. Sie ist dafür verantwortlich, die Daten nach einem Upload oder dem Hinzufügen eines Kommentars neu zu laden (fetchTripData) und die Lightbox-Galerie (PhotoSwipe) neu zu initialisieren.

ImageUploader.vue: Kapselt die gesamte Logik für die Uppy-Bibliothek. Sie wird als Pop-up (Modal) konfiguriert und sendet die Dateien an den korrekten Endpunkt. Bei Erfolg sendet sie ein upload-success-Event an die Eltern-Komponente.

MultiSelectDropdown.vue: Eine von uns erstellte, wiederverwendbare Komponente für eine benutzerfreundliche Mehrfachauswahl mit Checkboxen, die in der Filterleiste verwendet wird.
