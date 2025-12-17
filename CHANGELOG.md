# Changelog

Alle wichtigen Änderungen am Audio Mastering Tool werden hier dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
und dieses Projekt hält sich an [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2025-10-12

### 🐛 Fixed - Bugfixes
- **Preset-Konfiguration vereinheitlicht**: Klare Zuordnung zwischen "Automatisch" und "Suno AI" Preset
- **Weboberfläche Preset-Anzeige**: Verwendetes Preset wird jetzt in der Statistik angezeigt
- **Default-Preset korrigiert**: Alle Komponenten verwenden jetzt konsistent "suno" als Standard
- **Automatische Analyse**: Empfiehlt immer Suno AI Preset für optimale AI-Musik-Verarbeitung

### 🔧 Changed - Änderungen
- **Preset-Hierarchie geklärt**: "Automatisch" = Suno AI, "Suno AI" = explizit Suno AI
- **Weboberfläche Labels**: Klare Bezeichnungen für bessere Benutzerführung

---

## [1.1.0] - 2025-10-12

### 🎵 Added - Neue Features
- **Intelligente Preset-Vorschläge**: Automatische Analyse der Audio-Dateien und Empfehlung des optimalen Mastering-Presets basierend auf LUFS-Werten
- **Drag & Drop Upload**: Moderne Datei-Upload-Oberfläche mit Drag-and-Drop-Funktionalität für mehrere Dateien gleichzeitig
- **Weboberfläche-Upload**: Direkter Datei-Upload über die Weboberfläche mit automatischer Speicherung im Input-Ordner
- **Mastering über Weboberfläche**: One-Click-Mastering-Start direkt aus der Weboberfläche mit verschiedenen Preset-Optionen
- **Löschen-Funktion**: Möglichkeit, gemasterte Dateien direkt über die Weboberfläche zu löschen
- **Versionsanzeige**: App-Version wird prominent in der Weboberfläche angezeigt
- **Vermeidung doppelter Verarbeitung**: Automatische Erkennung bereits verarbeiteter Dateien zur Vermeidung unnötiger Neuverarbeitung

### 🔧 Changed - Änderungen
- **Verbesserte Weboberfläche**: Moderneres Design mit besserer Benutzerführung und responsivem Layout
- **Upload-Prozess**: Nahtlose Integration von Upload und Verarbeitung in einem Workflow
- **Batch-Verarbeitung**: Optimierte Logik zur Vermeidung doppelter Verarbeitung bereits gemasterter Dateien

### 🐛 Fixed - Bugfixes
- **Upload-Dateien**: Hochgeladene Dateien werden jetzt korrekt im Input-Ordner gespeichert und verarbeitet
- **Webserver-Stabilität**: Verbesserte Fehlerbehandlung und Stabilität des lokalen Webservers

### 📚 Technical Details
- **Neue Webserver-Endpoints**: `/upload`, `/process`, `/delete/<filename>` für vollständige Weboberfläche-Integration
- **Audio-Analyse für Presets**: Automatische LUFS-basierte Preset-Empfehlungen
- **Erweiterte Batch-Verarbeitung**: Unterstützung für Überspringen bereits verarbeiteter Dateien

---

## [1.0.0] - 2025-10-12

### 🎵 Added - Neue Features
- **Vollständige Audio-Mastering-Pipeline**: High-Pass Filter, Kompression, LUFS-Normalisierung, Peak-Limiting
- **Batch-Verarbeitung**: Mehrere WAV/MP3-Dateien gleichzeitig verarbeiten
- **Webserver für A/B-Vergleich**: Lokaler Server mit professionellem Audio-Vergleich
- **Automatisches Update-System**: Sichere Updates von Cloudflare Storage
- **NSIS-Installer**: Professionelle Windows-Installation mit Deinstallation
- **Detaillierte Qualitätsanalyse**: LUFS, True Peak, Crest Factor, Stereo-Analyse
- **Tastatur-Shortcuts**: Schnelle Navigation im Web-Interface
- **Logging-System**: Vollständige Verarbeitungsprotokolle

### 🔧 Changed - Änderungen
- **Professionelle Mastering-Standards**: Alle Parameter nach ITU-R BS.1770-4 und EBU R128
- **Modulare Architektur**: Saubere Trennung von Audio-Processing, Batch-Verwaltung und UI
- **Type Hints**: Vollständige Python Type Hints für bessere Code-Qualität

### 🐛 Fixed - Bugfixes
- **Audio-Position beibehalten**: Beim A/B-Wechsel springt die Wiedergabe nicht mehr zurück
- **Memory-Management**: Effiziente Verarbeitung großer Audio-Dateien
- **Fehlerbehandlung**: Robuste Verarbeitung defekter Dateien

### 📚 Technical Details
- **Python 3.8+** Kompatibilität
- **PyInstaller** für Standalone-EXE-Erstellung
- **Flask** für Web-Interface
- **NSIS** für Windows-Installer
- **Cloudflare** für Update-Distribution

### 🎯 Breaking Changes
- Erste stabile Version - keine Breaking Changes von vorherigen Versionen

### 📝 Known Issues
- MP3-Decoding kann bei sehr großen Dateien (>500MB) Performance-Probleme verursachen
- Webserver läuft nur lokal (localhost), kein Remote-Zugang

---

## [Unreleased]

### Planned
- [ ] GUI-Version mit tkinter
- [ ] Preset-System für verschiedene Musikgenres
- [ ] Parallele Verarbeitung mehrerer Dateien
- [ ] Cloud-Integration (S3, Dropbox)
- [ ] VST-Plugin Export

---

## Version History

- **1.1.1** (2025-10-12): Bugfix-Release - Preset-Konfiguration vereinheitlicht
- **1.1.0** (2025-10-12): Weboberfläche-Integration mit Upload und Mastering
- **1.0.0** (2025-10-12): Erste stabile Release mit allen Kernfunktionen
- **0.1.0-alpha** (2025-10-10): Initialer Prototyp mit grundlegender Funktionalität

---

## Contributing

Bitte lese die [CONTRIBUTING.md](CONTRIBUTING.md) für Details zum Beitrag zu diesem Projekt.

## Support

Bei Problemen oder Fragen:
- Öffne ein Issue auf GitHub
- Schaue in die [README.md](README.md) für Anleitungen
- Prüfe die Logs in `logs/` für Debug-Informationen