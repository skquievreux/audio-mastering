# Audio Mastering Automation Tool

Automatisiertes Audio-Mastering für Suno AI generierte Songs mit Batch-Verarbeitung und professionellen Standards.

## 🚀 Schnellstart

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Audio-Dateien vorbereiten
Lege deine WAV oder MP3-Dateien in den `input/` Ordner.

### 3. Mastering starten
```bash
python mastering_tool.py
```

### 4. Ergebnisse finden
Die gemasterten Dateien findest du im `output/` Ordner mit dem Suffix "_mastered".

## 📋 Funktionen

- **Batch-Verarbeitung**: Mehrere Dateien gleichzeitig verarbeiten
- **Professionelle Chain**: High-Pass → Kompression → LUFS-Norm → Peak-Limiting
- **Qualitätskontrolle**: Automatische LUFS und Peak-Messungen
- **Detaillierte Reports**: Übersicht über alle Verarbeitungsergebnisse
- **Fehlerbehandlung**: Robuste Verarbeitung mit aussagekräftigen Meldungen

## 🎛️ Mastering-Standards

| Parameter | Wert | Begründung |
|-----------|------|------------|
| Sample Rate | 44100 Hz | CD-Qualität, Streaming-Standard |
| Bit Depth | 16-bit | Ausreichend für Streaming |
| Target LUFS | -10.0 LUFS | Moderne Musik-Standards |
| True Peak Ceiling | -1.0 dBTP | Verhindert Inter-Sample Peaks |
| High-Pass | 20 Hz | Entfernt Subsonic-Rumpeln |
| Kompression | 3:1 @ -20dB | Balance zwischen Kontrolle und Natürlichkeit |

## 📖 Verwendung

### Grundlegende Verwendung
```bash
# Standard-Ordner verwenden
python mastering_tool.py

# Benutzerdefinierte Ordner
python mastering_tool.py -i ./meine_songs -o ./gemastert

# Detaillierte Ausgabe
python mastering_tool.py --verbose
```

### Kommandozeilen-Optionen
```
-i, --input     Input-Ordner (Standard: input/)
-o, --output    Output-Ordner (Standard: output/)
--verbose, -v   Detaillierte Ausgabe
--workers       Anzahl paralleler Worker (Standard: 1)
```

## 📊 Beispiel-Output

```
================================================================================
AUDIO MASTERING BATCH REPORT
================================================================================

ZUSAMMENFASSUNG:
  Verarbeitete Dateien: 3
  Fehlerhafte Dateien: 0
  Gesamtzeit: 12.45 Sekunden
  Durchschnitt pro Datei: 4.15 Sekunden

VERARBEITETE DATEIEN:
--------------------------------------------------------------------------------
Dateiname                 | LUFS   | Peak dB | Peak dBTP | Dauer
--------------------------------------------------------------------------------
song1.wav                 | -10.0  | -2.3    | -1.0      | 3:24
song2.wav                 | -10.0  | -1.8    | -1.0      | 2:51
song3.wav                 | -10.0  | -3.1    | -1.0      | 4:12

================================================================================
```

## 🏗️ Architektur

### Komponenten
- **`mastering_tool.py`**: Haupt-Script mit CLI
- **`audio_processor.py`**: Audio-Verarbeitungsklasse
- **`batch_processor.py`**: Batch-Verwaltung
- **`config.py`**: Konfiguration und Konstanten

### Verarbeitungskette
1. **High-Pass Filter** (20 Hz) - Entfernt unerwünschte Tieftonartefakte
2. **Kompression** (3:1 Ratio, -20dB Threshold) - Dynamikkontrolle
3. **LUFS-Normalisierung** (-10 LUFS) - Einheitliche Lautstärke
4. **Peak Limiter** (-1.0 dBTP) - Verhindert Clipping

## 🔧 Technische Details

### Abhängigkeiten
- `numpy` - Numerische Berechnungen
- `scipy` - Signalverarbeitung
- `soundfile` - Audio I/O
- `pyloudnorm` - LUFS-Messung

### Unterstützte Formate
- WAV (beliebiges Sample Rate, konvertiert zu 44.1kHz)
- MP3 (decoded zu WAV)

### Performance
- Typische Verarbeitungszeit: < 30 Sekunden für 3-5 Minuten Audio
- Speicherverbrauch: ~50-200 MB pro Datei
- CPU: Single-Threaded (parallele Verarbeitung für zukünftige Releases)

## 🐛 Fehlerbehebung

### Häufige Probleme
- **"Keine Dateien gefunden"**: Überprüfe, ob Dateien im `input/` Ordner liegen
- **"Import Error"**: Stelle sicher, dass alle Dependencies installiert sind
- **"Speicherfehler"**: Datei könnte zu groß sein (Max. 500 MB)

### Logs
Logs werden automatisch in `logs/mastering_YYYYMMDD_HHMMSS.log` gespeichert.

## 📈 Zukünftige Erweiterungen

### Phase 2
- [ ] GUI mit tkinter
- [ ] Preset-System (Rock, Pop, EDM)
- [ ] Spektrum-Analyse

### Phase 3
- [ ] Web-Interface
- [ ] Cloud-Integration
- [ ] Machine Learning Optimierung

## 📄 Lizenz

Dieses Projekt ist Open Source. Für kommerzielle Nutzung bitte kontaktieren.

## 🤝 Beitragen

Issues und Pull Requests sind willkommen!