#!/usr/bin/env python3
"""
Einfacher Webserver für Audio-Vergleich
"""

from flask import Flask, render_template_string, send_from_directory, request, jsonify
from pathlib import Path
import json
import os
import threading
from werkzeug.utils import secure_filename
from werkzeug.security import safe_join
from audio_analyzer import AudioAnalyzer
from batch_processor import BatchProcessor
from audio_processor import MASTERING_PRESETS
from config import MAX_FILE_SIZE_MB
import shutil

app = Flask(__name__)

# Pfade
INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")

# Erlaubte Dateiendungen
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'aiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_app_version():
    """Ermittle die App-Version aus verschiedenen Quellen"""
    try:
        # Versuche aus config.py zu lesen
        from config import VERSION
        return VERSION
    except:
        try:
            # Versuche aus requirements.txt zu lesen
            with open('requirements.txt', 'r') as f:
                for line in f:
                    if 'audio-mastering' in line.lower():
                        return line.split('==')[-1].strip()
        except:
            pass
    return "1.0.0"  # Fallback


def analyze_audio_for_preset(audio_path):
    """Analysiere Audio-Datei und schlage Preset vor"""
    try:
        analyzer = AudioAnalyzer()
        stats = analyzer.analyze_file(audio_path)

        lufs = stats['original_lufs']

        # Preset-Empfehlungen basierend auf LUFS
        if lufs > -12:
            return "gentle", "Sanfte Bearbeitung für bereits laute Aufnahmen"
        elif lufs > -16:
            return "default", "Standard-Mastering für moderate Lautheit"
        elif lufs > -20:
            return "dynamic", "Dynamische Bearbeitung für leise Aufnahmen"
        else:
            return "aggressive", "Intensive Bearbeitung für sehr leise Aufnahmen"
    except:
        return "default", "Standard-Preset bei Analysefehler"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎵 Audio Mastering Vergleich</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }

        .comparison-grid {
            display: grid;
            gap: 30px;
            padding: 30px;
        }

        .comparison-item {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            border-left: 5px solid #4facfe;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .comparison-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        .file-title {
            font-size: 1.4em;
            font-weight: bold;
            color: #333;
            margin-bottom: 20px;
            text-align: center;
        }

        .audio-section {
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
        }

        .audio-player {
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .audio-label {
            font-weight: bold;
            color: #666;
            margin-bottom: 10px;
            text-align: center;
        }

        .audio-label.original {
            color: #e74c3c;
        }

        .audio-label.mastered {
            color: #27ae60;
        }

        audio {
            width: 100%;
            margin-bottom: 10px;
        }

        .controls {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-top: 15px;
            flex-wrap: wrap;
        }

        button {
            background: #4facfe;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.2s;
        }

        button:hover {
            background: #00c6fb;
        }

        .switch-btn {
            background: #95a5a6;
            color: white;
            border: 2px solid #7f8c8d;
        }

        .switch-btn.active {
            background: #3498db;
            border-color: #2980b9;
            box-shadow: 0 0 10px rgba(52, 152, 219, 0.3);
        }

        .switch-btn:hover {
            background: #34495e;
        }

        .switch-btn.active:hover {
            background: #2980b9;
        }

        .play-btn {
            background: #27ae60;
        }

        .play-btn:hover {
            background: #229954;
        }

        .stop-btn {
            background: #e74c3c;
        }

        .stop-btn:hover {
            background: #c0392b;
        }

        .ab-test {
            background: #9b59b6;
            animation: none;
        }

        .ab-test:hover {
            background: #8e44ad;
        }

        .ab-test.testing {
            animation: pulse 0.5s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        .stats {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }

        .stats h4 {
            margin-bottom: 10px;
            color: #333;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
        }

        .stat-item {
            text-align: center;
        }

        .stat-value {
            font-size: 1.2em;
            font-weight: bold;
            color: #4facfe;
        }

        .stat-label {
            font-size: 0.9em;
            color: #666;
        }

        .no-files {
            text-align: center;
            padding: 50px;
            color: #666;
        }

        @media (max-width: 768px) {
            .audio-section {
                grid-template-columns: 1fr;
            }

            .header h1 {
                font-size: 2em;
            }

            .controls {
                flex-direction: column;
                align-items: center;
            }

            button {
                width: 200px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 Audio Mastering Vergleich</h1>
            <p>Vergleiche Original- und gemasterte Dateien | Qualitätskontrolle</p>
            <div class="version-info">Version {{ version }}</div>
        </div>

        <!-- Upload-Bereich -->
        <div class="upload-section" style="padding: 30px; background: #f8f9fa; border-bottom: 1px solid #e9ecef;">
            <h3 style="margin-bottom: 20px; color: #333;">📁 Dateien hochladen</h3>

            <!-- Drag & Drop Zone -->
            <div id="dropZone" class="drop-zone" style="border: 2px dashed #4facfe; border-radius: 10px; padding: 40px; text-align: center; margin-bottom: 20px; background: #f0f8ff; transition: all 0.3s;">
                <div class="drop-content">
                    <div style="font-size: 48px; margin-bottom: 10px;">📤</div>
                    <div style="font-size: 18px; margin-bottom: 10px;">Ziehe Dateien hierher oder klicke zum Auswählen</div>
                    <div style="color: #666; font-size: 14px;">Unterstützt: WAV, MP3, FLAC, AIFF</div>
                </div>
                <input type="file" id="fileInput" name="file" accept=".wav,.mp3,.flac,.aiff" multiple style="display: none;">
            </div>

            <!-- Upload-Buttons -->
            <div class="upload-controls" style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
                <button type="button" onclick="document.getElementById('fileInput').click()" class="play-btn">📁 Dateien auswählen</button>
                <button type="button" onclick="processFiles()" class="ab-test" id="processBtn" disabled>🎛️ Mastering starten</button>
                <select id="presetSelect" style="padding: 10px; border-radius: 5px; border: 1px solid #ddd;">
                    <option value="auto">🤖 Automatisch (empfohlen)</option>
                    <option value="default">🎵 Standard</option>
                    <option value="gentle">🌸 Sanft</option>
                    <option value="aggressive">🔥 Intensiv</option>
                    <option value="dynamic">🎼 Dynamisch</option>
                    <option value="podcast">🎙️ Podcast</option>
                </select>
            </div>

            <!-- Upload-Status -->
            <div id="uploadStatus" style="margin-top: 20px;"></div>

            <!-- Hochgeladene Dateien -->
            <div id="uploadedFiles" style="margin-top: 20px;"></div>
        </div>

        <div id="content">
            <div class="comparison-grid">
                {% for file in files %}
                <div class="comparison-item">
                    <div class="file-title">🎵 {{ file.name }}</div>

                    <div class="audio-section">
                        <div class="audio-player">
                            <div class="audio-label" id="label-{{ file.name }}">🎤 ORIGINAL</div>
                            <audio id="audio-{{ file.name }}" controls preload="metadata">
                                <source id="source-original-{{ file.name }}" src="/audio/input/{{ file.name }}" type="audio/wav">
                                <source id="source-mastered-{{ file.name }}" src="/audio/output/{{ file.mastered_name }}" type="audio/wav">
                                Ihr Browser unterstützt das Audio-Element nicht.
                            </audio>
                        </div>
                    </div>

                    <div class="controls">
                        <button id="btn-original-{{ file.name }}" class="switch-btn active" onclick="switchTo('{{ file.name }}', 'original')">🎤 ORIGINAL</button>
                        <button id="btn-mastered-{{ file.name }}" class="switch-btn" onclick="switchTo('{{ file.name }}', 'mastered')">🎛️ MASTERED</button>
                        <button class="play-btn" onclick="togglePlay('{{ file.name }}')">▶️ PLAY</button>
                        <button class="stop-btn" onclick="stopAudio('{{ file.name }}')">⏹️ STOP</button>
                        <button class="ab-test" onclick="abTest('{{ file.name }}')">🔄 A/B TEST</button>
                        <button class="stop-btn" onclick="deleteMastered('{{ file.mastered_name }}')" style="background: #e74c3c;">🗑️ LÖSCHEN</button>
                    </div>

                    <div class="stats">
                        <h4>📊 Verarbeitungsstatistik</h4>
                        <div class="stats-grid">
                            <div class="stat-item">
                                <div class="stat-value">{{ "%.1f"|format(file.stats.original_lufs) }} dB</div>
                                <div class="stat-label">Original LUFS</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">{{ "%.1f"|format(file.stats.final_lufs) }} dB</div>
                                <div class="stat-label">Final LUFS</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">{{ "%+.1f"|format(file.stats.delta_lufs) }} dB</div>
                                <div class="stat-label">LUFS Δ</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">{{ "%.1f"|format(file.stats.final_peak) }} dBTP</div>
                                <div class="stat-label">Peak (begrenzt)</div>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    <script>
        // Audio-Steuerung für A/B-Vergleich
        const audioStates = {}; // Speichert den Zustand für jeden Track

        function initializeAudio(filename) {
            if (!audioStates[filename]) {
                audioStates[filename] = {
                    currentSource: 'original',
                    isPlaying: false,
                    abTestInterval: null
                };
            }
        }

        function switchTo(filename, source) {
            initializeAudio(filename);

            const audio = document.getElementById(`audio-${filename}`);
            const btnOriginal = document.getElementById(`btn-original-${filename}`);
            const btnMastered = document.getElementById(`btn-mastered-${filename}`);
            const label = document.getElementById(`label-${filename}`);

            if (!audio) return;

            // Aktuelle Position speichern
            const currentTime = audio.currentTime;
            const wasPlaying = !audio.paused;

            // Buttons aktualisieren
            btnOriginal.classList.toggle('active', source === 'original');
            btnMastered.classList.toggle('active', source === 'mastered');

            // Label aktualisieren
            if (source === 'original') {
                label.innerHTML = '🎤 ORIGINAL';
                label.className = 'audio-label original';
            } else {
                label.innerHTML = '🎛️ MASTERED';
                label.className = 'audio-label mastered';
            }

            // Audio-Source wechseln (über src-Attribut)
            const sourceOriginal = document.getElementById(`source-original-${filename}`);
            const sourceMastered = document.getElementById(`source-mastered-${filename}`);

            if (source === 'original') {
                audio.src = sourceOriginal.src;
            } else {
                audio.src = sourceMastered.src;
            }

            // Position wiederherstellen und Wiedergabe fortsetzen
            audio.addEventListener('loadedmetadata', function onLoaded() {
                audio.currentTime = currentTime;
                if (wasPlaying) {
                    audio.play();
                }
                audio.removeEventListener('loadedmetadata', onLoaded);
            });

            audioStates[filename].currentSource = source;
            console.log(`🔄 ${filename}: Zu ${source} gewechselt (Position: ${currentTime.toFixed(1)}s)`);
        }

        function togglePlay(filename) {
            initializeAudio(filename);

            const audio = document.getElementById(`audio-${filename}`);
            const playBtn = document.querySelector(`[onclick*="togglePlay('${filename}')"]`);

            if (!audio) return;

            if (audio.paused) {
                audio.play();
                playBtn.innerHTML = '⏸️ PAUSE';
                audioStates[filename].isPlaying = true;
            } else {
                audio.pause();
                playBtn.innerHTML = '▶️ PLAY';
                audioStates[filename].isPlaying = false;
            }
        }

        function stopAudio(filename) {
            initializeAudio(filename);

            const audio = document.getElementById(`audio-${filename}`);
            const playBtn = document.querySelector(`[onclick*="togglePlay('${filename}')"]`);

            if (audio) {
                audio.pause();
                audio.currentTime = 0;
                playBtn.innerHTML = '▶️ PLAY';
                audioStates[filename].isPlaying = false;
            }

            // A/B-Test stoppen falls aktiv
            stopAbTest(filename);
        }

        function abTest(filename) {
            initializeAudio(filename);

            const abBtn = document.querySelector(`[onclick*="abTest('${filename}')"]`);

            if (audioStates[filename].abTestInterval) {
                // A/B-Test stoppen
                stopAbTest(filename);
                abBtn.innerHTML = '🔄 A/B TEST';
                abBtn.classList.remove('testing');
            } else {
                // A/B-Test starten
                startAbTest(filename);
                abBtn.innerHTML = '⏹️ STOP A/B';
                abBtn.classList.add('testing');
            }
        }

        function startAbTest(filename) {
            const audio = document.getElementById(`audio-${filename}`);
            if (!audio) return;

            // Stelle sicher, dass Audio spielt
            if (audio.paused) {
                togglePlay(filename);
            }

            let switchCount = 0;
            audioStates[filename].abTestInterval = setInterval(() => {
                switchCount++;
                const nextSource = switchCount % 2 === 0 ? 'original' : 'mastered';
                switchTo(filename, nextSource);

                // Stoppe nach 10 Wechseln (20 Sekunden bei 2s Intervall)
                if (switchCount >= 10) {
                    stopAbTest(filename);
                    const abBtn = document.querySelector(`[onclick*="abTest('${filename}')"]`);
                    abBtn.innerHTML = '🔄 A/B TEST';
                    abBtn.classList.remove('testing');
                }
            }, 2000); // Alle 2 Sekunden wechseln
        }

        function stopAbTest(filename) {
            if (audioStates[filename] && audioStates[filename].abTestInterval) {
                clearInterval(audioStates[filename].abTestInterval);
                audioStates[filename].abTestInterval = null;
            }
        }

        function stopAll() {
            const allAudio = document.querySelectorAll('audio');
            allAudio.forEach(audio => {
                audio.pause();
                audio.currentTime = 0;
            });

            // Alle Play-Buttons zurücksetzen
            const playBtns = document.querySelectorAll('[onclick*="togglePlay"]');
            playBtns.forEach(btn => {
                btn.innerHTML = '▶️ PLAY';
            });

            // Alle A/B-Tests stoppen
            Object.keys(audioStates).forEach(filename => {
                stopAbTest(filename);
                const abBtn = document.querySelector(`[onclick*="abTest('${filename}')"]`);
                if (abBtn) {
                    abBtn.innerHTML = '🔄 A/B TEST';
                    abBtn.classList.remove('testing');
                }
            });
        }

        // Upload-Funktionalität
        let uploadedFiles = [];

        // Drag & Drop Funktionalität
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');

        dropZone.addEventListener('click', () => {
            fileInput.click();
        });

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = '#00c6fb';
            dropZone.style.background = '#e6f7ff';
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.style.borderColor = '#4facfe';
            dropZone.style.background = '#f0f8ff';
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = '#4facfe';
            dropZone.style.background = '#f0f8ff';

            const files = e.dataTransfer.files;
            handleFiles(files);
        });

        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });

        function handleFiles(files) {
            const statusDiv = document.getElementById('uploadStatus');
            const uploadedDiv = document.getElementById('uploadedFiles');

            if (files.length === 0) {
                statusDiv.innerHTML = '<span style="color: #e74c3c;">❌ Bitte wählen Sie Dateien aus.</span>';
                return;
            }

            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                formData.append('file', files[i]);
            }

            statusDiv.innerHTML = '<span style="color: #f39c12;">⏳ Lade hoch...</span>';

            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    uploadedFiles = data.files;
                    statusDiv.innerHTML = '<span style="color: #27ae60;">✅ ' + data.message + '</span>';

                    // Zeige hochgeladene Dateien mit Preset-Vorschlägen
                    let html = '<h4>Hochgeladene Dateien:</h4><ul>';
                    data.files.forEach(file => {
                        html += `<li><strong>${file.filename}</strong> - Empfohlen: <span style="color: #4facfe;">${file.preset}</span> (${file.reason})</li>`;
                    });
                    html += '</ul>';
                    uploadedDiv.innerHTML = html;

                    // Aktiviere Process-Button
                    document.getElementById('processBtn').disabled = false;
                } else {
                    statusDiv.innerHTML = '<span style="color: #e74c3c;">❌ Fehler: ' + data.error + '</span>';
                }
            })
            .catch(error => {
                statusDiv.innerHTML = '<span style="color: #e74c3c;">❌ Upload-Fehler: ' + error.message + '</span>';
            });
        }

        // Mastering-Verarbeitung starten
        function processFiles() {
            const statusDiv = document.getElementById('uploadStatus');
            const presetSelect = document.getElementById('presetSelect');
            const preset = presetSelect.value === 'auto' ? uploadedFiles[0]?.preset || 'default' : presetSelect.value;

            statusDiv.innerHTML = '<span style="color: #f39c12;">🎛️ Mastering wird gestartet...</span>';

            const formData = new FormData();
            formData.append('preset', preset);

            fetch('/process', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    statusDiv.innerHTML = '<span style="color: #27ae60;">✅ ' + data.message + '</span>';
                    setTimeout(() => {
                        location.reload();
                    }, 2000);
                } else {
                    statusDiv.innerHTML = '<span style="color: #e74c3c;">❌ Fehler: ' + data.error + '</span>';
                }
            })
            .catch(error => {
                statusDiv.innerHTML = '<span style="color: #e74c3c;">❌ Verarbeitungsfehler: ' + error.message + '</span>';
            });
        }

        // Löschen-Funktion
        function deleteMastered(filename) {
            if (!confirm(`Möchten Sie "${filename}" wirklich löschen?`)) {
                return;
            }

            fetch(`/delete/${filename}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    location.reload();
                } else {
                    alert('Fehler: ' + data.error);
                }
            })
            .catch(error => {
                alert('Lösch-Fehler: ' + error.message);
            });
        }

        // Audio-Event-Listener für Button-Synchronisation
        document.addEventListener('DOMContentLoaded', () => {
            const allAudio = document.querySelectorAll('audio');
            allAudio.forEach(audio => {
                const filename = audio.id.replace('audio-', '');

                audio.addEventListener('play', () => {
                    const playBtn = document.querySelector(`[onclick*="togglePlay('${filename}')"]`);
                    if (playBtn) playBtn.innerHTML = '⏸️ PAUSE';
                    audioStates[filename].isPlaying = true;
                });

                audio.addEventListener('pause', () => {
                    const playBtn = document.querySelector(`[onclick*="togglePlay('${filename}')"]`);
                    if (playBtn) playBtn.innerHTML = '▶️ PLAY';
                    audioStates[filename].isPlaying = false;
                });

                audio.addEventListener('ended', () => {
                    const playBtn = document.querySelector(`[onclick*="togglePlay('${filename}')"]`);
                    if (playBtn) playBtn.innerHTML = '▶️ PLAY';
                    audioStates[filename].isPlaying = false;
                    stopAbTest(filename);
                });
            });

            console.log('🎵 A/B Audio-Vergleich geladen');
        });

        // Tastatur-Shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === ' ') {
                e.preventDefault();
                // Toggle Play/Pause für ersten Track
                const firstAudio = document.querySelector('audio');
                if (firstAudio) {
                    const filename = firstAudio.id.replace('audio-', '');
                    togglePlay(filename);
                }
            }
            if (e.key === 'Escape') {
                stopAll();
            }
            if (e.key === '1') {
                // Zu Original wechseln
                const firstAudio = document.querySelector('audio');
                if (firstAudio) {
                    const filename = firstAudio.id.replace('audio-', '');
                    switchTo(filename, 'original');
                }
            }
            if (e.key === '2') {
                // Zu Mastered wechseln
                const firstAudio = document.querySelector('audio');
                if (firstAudio) {
                    const filename = firstAudio.id.replace('audio-', '');
                    switchTo(filename, 'mastered');
                }
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Hauptseite mit Audio-Vergleich"""
    try:
        # Audio-Dateien finden und analysieren
        analyzer = AudioAnalyzer()
        comparisons = analyzer.batch_compare(str(INPUT_DIR), str(OUTPUT_DIR))

        # Daten für Template vorbereiten
        files_data = []
        for comp in comparisons:
            orig = comp['original']
            mast = comp['mastered']
            delta = comp['delta']

            files_data.append({
                'name': orig['filename'],
                'mastered_name': orig['filename'].replace('.wav', '_mastered.wav'),
                'stats': {
                    'original_lufs': orig['lufs_integrated'],
                    'final_lufs': mast['lufs_integrated'],
                    'original_peak': orig['peak_db'],
                    'final_peak': mast['peak_db'],
                    'delta_lufs': delta['lufs_db'],
                    'delta_peak': delta['peak_db']
                }
            })

        return render_template_string(HTML_TEMPLATE, files=files_data, version=get_app_version())

    except Exception as e:
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 50px; text-align: center;">
            <h1>❌ Fehler beim Laden</h1>
            <p>{str(e)}</p>
            <p><a href="#" onclick="window.location.reload()">🔄 Neu laden</a></p>
        </body>
        </html>
        """

@app.route('/audio/<folder>/<filename>')
def serve_audio(folder, filename):
    """Audio-Dateien ausliefern (mit Security-Validierung)"""
    # Security: Filename sanitization gegen Path Traversal
    filename = secure_filename(filename)

    if not filename:
        return "Ungültiger Dateiname", 400

    if folder == 'input':
        # Security: safe_join verhindert Directory Traversal
        file_path = safe_join(str(INPUT_DIR), filename)
        if file_path and Path(file_path).exists():
            return send_from_directory(INPUT_DIR, filename)
    elif folder == 'output':
        file_path = safe_join(str(OUTPUT_DIR), filename)
        if file_path and Path(file_path).exists():
            return send_from_directory(OUTPUT_DIR, filename)

    return "Datei nicht gefunden", 404


@app.route('/upload', methods=['POST'])
def upload_file():
    """Datei-Upload über Weboberfläche (mit Größen-Validierung)"""
    if 'file' not in request.files:
        return jsonify({'error': 'Keine Datei ausgewählt'}), 400

    files = request.files.getlist('file')
    uploaded_files = []

    for file in files:
        if file.filename == '':
            continue

        # Security & Validation: Dateigrößen-Check
        file.seek(0, os.SEEK_END)
        size_bytes = file.tell()
        size_mb = size_bytes / (1024 * 1024)
        file.seek(0)

        if size_mb > MAX_FILE_SIZE_MB:
            return jsonify({
                'error': f'{file.filename} ist zu groß ({size_mb:.1f}MB > {MAX_FILE_SIZE_MB}MB)'
            }), 413

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = INPUT_DIR / filename

            # Speichere Datei
            file.save(file_path)

            # Analysiere Datei für Preset-Vorschlag
            try:
                preset, reason = analyze_audio_for_preset(file_path)
            except Exception as e:
                # Fallback bei Analyse-Fehler
                preset, reason = 'default', 'Standard (Analyse fehlgeschlagen)'

            uploaded_files.append({
                'filename': filename,
                'preset': preset,
                'reason': reason,
                'size_mb': round(size_mb, 2)
            })
        else:
            return jsonify({'error': f'Dateityp von {file.filename} nicht erlaubt'}), 400

    if not uploaded_files:
        return jsonify({'error': 'Keine gültigen Dateien hochgeladen'}), 400

    return jsonify({
        'success': True,
        'files': uploaded_files,
        'message': f'{len(uploaded_files)} Dateien erfolgreich hochgeladen'
    })


@app.route('/process', methods=['POST'])
def process_files():
    """Starte Mastering-Verarbeitung über Weboberfläche"""
    try:
        preset = request.form.get('preset', 'default')

        # Batch-Verarbeitung starten
        processor = BatchProcessor(INPUT_DIR, OUTPUT_DIR, preset=preset)
        results = processor.process_batch(max_workers=1)

        # Seite neu laden lassen
        return jsonify({
            'success': True,
            'message': f'{results["files_processed"]} Dateien mit Preset "{preset}" verarbeitet',
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Lösche eine gemasterte Datei"""
    try:
        # Security: Filename sanitization
        filename = secure_filename(filename)

        # Sicherstellen, dass es eine gemasterte Datei ist
        if not filename.endswith('_mastered.wav'):
            return jsonify({'error': 'Nur gemasterte Dateien können gelöscht werden'}), 400

        file_path = OUTPUT_DIR / filename
        if file_path.exists():
            file_path.unlink()
            return jsonify({'success': True, 'message': f'{filename} gelöscht'})
        else:
            return jsonify({'error': 'Datei nicht gefunden'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🎵 Starte Audio-Vergleich Webserver...")
    print("📱 Öffne http://localhost:5000 in deinem Browser")
    print("❌ Zum Beenden: Ctrl+C")
    app.run(debug=True, host='0.0.0.0', port=5000)