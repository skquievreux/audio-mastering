# Changelog

Alle wichtigen Änderungen am Audio Mastering Tool werden hier dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
und dieses Projekt hält sich an [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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