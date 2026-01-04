"""
Konfiguration für Audio Mastering Tool
"""

from pathlib import Path

# Version
VERSION = "1.3.0"

# Audio-Standards
TARGET_LUFS = -10.0
TRUE_PEAK_CEILING_DBTP = -1.0
SAMPLE_RATE = 44100
BIT_DEPTH = 16

# Version
VERSION = "1.1.1"

# Default-Preset (für Suno AI optimiert)
DEFAULT_PRESET = 'suno'

# Filter-Parameter
HIGH_PASS_FREQ = 20  # Hz

# Kompression-Parameter
COMPRESSION_RATIO = 3.0  # 3:1
COMPRESSION_THRESHOLD_DB = -20.0

# Pfad-Konfiguration
INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
LOGS_DIR = Path("logs")

# Datei-Suffixe
MASTERED_SUFFIX = "_mastered"
SUPPORTED_EXTENSIONS = {'.wav', '.mp3'}

# Performance
MAX_FILE_SIZE_MB = 500