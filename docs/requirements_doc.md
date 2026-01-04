# Audio Mastering Automation - Anforderungsdokument

## Projektziel
Automatisierte Mastering-Pipeline für Suno AI generierte Songs mit Batch-Verarbeitung und professionellen Audio-Standards.

---

## 1. Funktionale Anforderungen

### 1.1 Kernfunktionalität
- **F1.1** Batch-Verarbeitung aller Audio-Dateien in einem Input-Ordner
- **F1.2** Unterstützung von WAV und MP3 Format als Input
- **F1.3** Export als WAV 16-bit/44.1kHz (Streaming-Standard)
- **F1.4** Automatische Ordner-Erstellung für Output

### 1.2 Audio-Verarbeitungskette
Die Mastering-Chain muss folgende Schritte in dieser Reihenfolge durchführen:

1. **High-Pass Filter** (20 Hz) - Entfernt Subsonic-Rumpeln
2. **Kompression** - Dynamikkontrolle (Threshold: -20dB, Ratio: 3:1)
3. **LUFS Normalisierung** - Ziel-Lautstärke setzen (-10 LUFS Standard)
4. **Peak Limiter** - Hard Limit bei -1.0 dBTP (True Peak)

### 1.3 Qualitätssicherung
- **F3.1** LUFS-Messung (Integrated Loudness)
- **F3.2** True Peak Messung in dBTP
- **F3.3** Detaillierter Report nach Verarbeitung
- **F3.4** Fehlerbehandlung mit aussagekräftigen Meldungen

### 1.4 Benutzerfreundlichkeit
- **F4.1** Einfache Konfiguration über Konstanten im Script
- **F4.2** Fortschrittsanzeige während Verarbeitung
- **F4.3** Zusammenfassender Report am Ende
- **F4.4** Optional: GUI für Nicht-Programmierer

---

## 2. Nicht-Funktionale Anforderungen

### 2.1 Performance
- **NF1.1** Verarbeitung von 3-5 Minuten Audio in unter 30 Sekunden
- **NF1.2** Speichereffizienz: Max. 500 MB RAM pro Datei
- **NF1.3** Möglichkeit für parallele Verarbeitung mehrerer Dateien

### 2.2 Qualität
- **NF2.1** Keine hörbaren Artefakte durch Verarbeitung
- **NF2.2** LUFS-Genauigkeit: ±0.5 LU vom Zielwert
- **NF2.3** True Peak Compliance: Keine Werte über -1.0 dBTP

### 2.3 Wartbarkeit
- **NF3.1** Modularer Code mit klaren Verantwortlichkeiten
- **NF3.2** Gut dokumentierte Funktionen
- **NF3.3** Einfache Anpassung von Mastering-Parametern

### 2.4 Plattform
- **NF4.1** Windows 10/11 Kompatibilität
- **NF4.2** Python 3.8+ erforderlich
- **NF4.3** Minimale externe Dependencies

---

## 3. Technische Spezifikationen

### 3.1 Audio-Standards

| Parameter | Wert | Begründung |
|-----------|------|------------|
| Sample Rate | 44100 Hz | CD-Qualität, Streaming-Standard |
| Bit Depth | 16-bit | Ausreichend für Streaming, kleinere Dateien |
| Target LUFS | -10.0 LUFS | Moderne Musik-Standards |
| True Peak Ceiling | -1.0 dBTP | Verhindert Inter-Sample Peaks |
| Compression Ratio | 3:1 | Balance zwischen Kontrolle und Natürlichkeit |
| Compression Threshold | -20 dB | Erfasst laute Passagen |

### 3.2 Technologie-Stack

**Kernbibliotheken:**
- `pyloudnorm` - ITU-R BS.1770-4 konforme LUFS-Messung
- `soundfile` - Audio I/O mit libsndfile
- `numpy` - Numerische Berechnungen
- `scipy` - Signal Processing (Filter, Kompression)

**Optional:**
- `pydub` - Alternative Audio-Verarbeitung
- `tkinter` - GUI Framework (Python Standard Library)

### 3.3 Dateistruktur
```
projekt/
├── mastering_tool.py          # Haupt-Script
├── requirements.txt           # Python Dependencies
├── config.yaml               # Konfigurationsdatei (optional)
├── README.md                 # Dokumentation
├── input/                    # Input-Ordner
│   └── song1.wav
├── output/                   # Output-Ordner
│   └── song1_mastered.wav
└── logs/                     # Log-Dateien
    └── mastering_YYYYMMDD.log
```

---

## 4. User Stories

### US1: Batch-Verarbeitung
**Als** Musikproduzent  
**möchte ich** mehrere Suno-Songs auf einmal mastern  
**damit** ich Zeit spare und konsistente Ergebnisse erhalte

**Akzeptanzkriterien:**
- Alle WAV/MP3-Dateien im Input-Ordner werden verarbeitet
- Output-Dateien haben Suffix "_mastered"
- Fortschritt wird in Echtzeit angezeigt
- Report zeigt LUFS und Peak-Werte aller Dateien

### US2: Qualitätskontrolle
**Als** Musikproduzent  
**möchte ich** die LUFS- und Peak-Werte jeder Datei sehen  
**damit** ich die Qualität des Masterings überprüfen kann

**Akzeptanzkriterien:**
- LUFS-Wert wird auf 0.1 genau angezeigt
- Peak-Wert in dBTP wird angezeigt
- Report kann gespeichert werden
- Vergleich mit Original-Werten möglich

### US3: Einfache Konfiguration
**Als** Benutzer ohne Audio-Expertise  
**möchte ich** nur Input/Output-Ordner angeben müssen  
**damit** ich das Tool ohne Fachwissen nutzen kann

**Akzeptanzkriterien:**
- Nur 2 Pfade müssen angegeben werden
- Sinnvolle Defaults für alle Audio-Parameter
- Fehlermeldungen sind verständlich
- Optional: Drag & Drop Interface

---

## 5. Technische Constraints

### 5.1 Einschränkungen
- Python 3.8+ erforderlich (wegen Type Hints)
- Windows-spezifische Pfade unterstützen (Backslashes)
- Maximale Dateigröße: 500 MB (ca. 1h Audio)
- Nur Mono/Stereo (kein Surround)

### 5.2 Abhängigkeiten

**requirements.txt:**
```
numpy>=1.21.0
scipy>=1.7.0
soundfile>=0.11.0
pyloudnorm>=0.1.0
```

---

## 6. Testfälle

### TC1: Standard-Verarbeitung
**Input:** 3-Minuten WAV-Datei, -15 LUFS  
**Erwartetes Ergebnis:**  
- Output: WAV 16-bit/44100Hz
- LUFS: -10.0 ±0.5
- True Peak: ≤ -1.0 dBTP
- Keine hörbaren Artefakte

### TC2: Leise Datei
**Input:** WAV mit -25 LUFS  
**Erwartetes Ergebnis:**  
- Lautstärke wird erhöht auf -10 LUFS
- Kein Clipping
- Dynamik bleibt erhalten

### TC3: Bereits laute Datei
**Input:** WAV mit -5 LUFS  
**Erwartetes Ergebnis:**  
- Lautstärke wird reduziert auf -10 LUFS
- True Peak bleibt unter -1.0 dBTP
- Kein Pumping-Effekt

### TC4: Batch mit gemischten Formaten
**Input:** 5 Dateien (3x WAV, 2x MP3)  
**Erwartetes Ergebnis:**  
- Alle 5 Dateien werden verarbeitet
- Konsistente Lautstärke über alle Dateien
- Report zeigt alle 5 Dateien

### TC5: Fehlerbehandlung
**Input:** Defekte/korrupte Audio-Datei  
**Erwartetes Ergebnis:**  
- Klare Fehlermeldung
- Verarbeitung der anderen Dateien läuft weiter
- Fehler im Report dokumentiert

---

## 7. Code-Beispiel: Minimale Implementation

```python
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from pathlib import Path
from scipy import signal

class SimpleMaster:
    def __init__(self, target_lufs=-10.0):
        self.target_lufs = target_lufs
        
    def process(self, input_file, output_file):
        # Laden
        audio, sr = sf.read(input_file)
        
        # 1. High-Pass Filter (20 Hz)
        sos = signal.butter(4, 20, 'hp', fs=sr, output='sos')
        if audio.ndim == 2:
            audio = np.column_stack([
                signal.sosfilt(sos, audio[:, 0]),
                signal.sosfilt(sos, audio[:, 1])
            ])
        else:
            audio = signal.sosfilt(sos, audio)
        
        # 2. LUFS Normalisierung
        meter = pyln.Meter(sr)
        loudness = meter.integrated_loudness(audio)
        audio = pyln.normalize.loudness(audio, loudness, self.target_lufs)
        
        # 3. Peak Limiter (-1.0 dBTP)
        audio = np.clip(audio, -0.891, 0.891)  # -1.0 dBTP ≈ 0.891 linear
        
        # Speichern
        sf.write(output_file, audio, sr, subtype='PCM_16')
        
        return {
            'lufs': meter.integrated_loudness(audio),
            'peak': 20 * np.log10(np.max(np.abs(audio)))
        }

# Verwendung
master = SimpleMaster(target_lufs=-10.0)
result = master.process('input/song.wav', 'output/song_mastered.wav')
print(f"LUFS: {result['lufs']:.1f}, Peak: {result['peak']:.1f} dB")
```

---

## 8. Prompt für AI-Implementierung

```markdown
Erstelle eine Python-Anwendung für automatisches Audio-Mastering mit folgenden Anforderungen:

FUNKTIONALITÄT:
- Batch-Verarbeitung von WAV/MP3-Dateien aus Input-Ordner
- Mastering-Chain: High-Pass (20Hz) → Kompression (3:1, -20dB) → LUFS-Norm (-10) → Limiter (-1dBTP)
- Export als WAV 16-bit/44.1kHz
- Detaillierter Report mit LUFS und Peak-Werten

TECHNOLOGIE:
- Python 3.8+
- Libraries: pyloudnorm, soundfile, numpy, scipy
- Modularer OOP-Ansatz
- Type Hints verwenden

BENUTZERFREUNDLICHKEIT:
- Einfache Konfiguration (nur Input/Output-Pfade)
- Fortschrittsanzeige während Verarbeitung
- Fehlerbehandlung mit klaren Meldungen
- Tabellen-formatierter Abschluss-Report

CODE-QUALITÄT:
- Docstrings für alle Funktionen
- Kommentare für komplexe Audio-Verarbeitung
- Saubere Trennung: Audio-Processing / File-Handling / UI
- Erweiterbar für zukünftige Features (z.B. GUI)

ZUSÄTZLICH:
- Erstelle requirements.txt
- Füge Beispiel-Konfiguration als Konstanten hinzu
- Implementiere Logging in Datei (optional)
- Main-Block mit if __name__ == "__main__"

WICHTIG:
- True Peak Messung korrekt implementieren (Inter-Sample Peaks)
- LUFS-Messung nach ITU-R BS.1770-4 Standard
- Stereo-Kanäle korrekt behandeln
- Performance: Große Dateien (>100MB) effizient verarbeiten
```

---

## 9. Risiken & Mitigation

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| Artefakte durch Over-Compression | Mittel | Hoch | Sanfte Ratio (3:1), Visual Feedback |
| Performance bei großen Dateien | Mittel | Mittel | Chunk-basierte Verarbeitung |
| Inkorrekte LUFS-Messung | Niedrig | Hoch | Validierte Library (pyloudnorm) |
| Inter-Sample Peaks | Mittel | Mittel | True Peak Limiter mit Oversampling |
| User macht falsche Einstellungen | Hoch | Mittel | Sinnvolle Defaults, Validierung |

---

## 10. Zukünftige Erweiterungen

### Phase 2 (Optional)
- [ ] GUI mit tkinter oder PyQt
- [ ] Vorher/Nachher Audio-Player
- [ ] Spektrum-Analyse Visualisierung
- [ ] Preset-System (Rock, Pop, EDM, etc.)
- [ ] Parallele Verarbeitung (Multiprocessing)

### Phase 3 (Nice-to-have)
- [ ] Web-Interface mit Flask
- [ ] Cloud-Integration (S3, Dropbox)
- [ ] Automatische Genre-Erkennung
- [ ] Machine Learning für adaptive Kompression
- [ ] VST-Plugin Export

---

## 11. Auslieferung

**Minimale Deliverables:**
1. `mastering_tool.py` - Haupt-Script
2. `requirements.txt` - Dependencies
3. `README.md` - Anleitung
4. `example_config.py` - Konfigurations-Template

**Optional:**
5. `.bat` Starter-Script für Windows
6. Beispiel-Audio-Dateien
7. Unit-Tests
8. Performance-Benchmark

---

## Anhang A: LUFS-Referenzwerte

| Genre | Typische LUFS | Empfehlung |
|-------|---------------|------------|
| Pop/Rock | -8 bis -10 | -9 LUFS |
| EDM/Electronic | -6 bis -8 | -7 LUFS |
| Hip-Hop | -7 bis -9 | -8 LUFS |
| Jazz/Akustik | -12 bis -14 | -13 LUFS |
| Classical | -16 bis -20 | -18 LUFS |
| Podcast | -16 bis -19 | -16 LUFS |

**Standard für Suno AI Output:** -10 LUFS (guter Kompromiss)

---

## Anhang B: Streaming-Plattform Standards

| Plattform | Target LUFS | Normalisierung | Kommentar |
|-----------|-------------|----------------|-----------|
| Spotify | -14 LUFS | Ja (default) | Loud-Mode: -11 LUFS |
| Apple Music | -16 LUFS | Ja (opt-in) | Sound Check Feature |
| YouTube | -14 LUFS | Ja | Automatisch |
| Tidal | -14 LUFS | Ja | HiFi-Qualität |
| SoundCloud | -13 bis -11 | Optional | Nutzer-einstellbar |

**Empfehlung:** Master auf -10 LUFS → Plattformen normalisieren runter (besser als hochnormalisieren)
