#!/usr/bin/env python3
"""
Performance Benchmark für Audio Mastering Tool
Vergleicht Performance vor/nach Library-Upgrades
"""

import time
import numpy as np
import scipy
from audio_processor import AudioProcessor
from pathlib import Path
import tempfile
import soundfile as sf
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_audio(duration_sec=10, sample_rate=44100, frequency=440):
    """Erstellt Test-Audio für Benchmarking"""
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec))
    # Stereo-Signal mit unterschiedlicher Frequenz pro Kanal
    audio = np.column_stack([
        np.sin(2 * np.pi * frequency * t),
        np.sin(2 * np.pi * frequency * 1.5 * t)
    ])
    return audio.astype(np.float32)

def benchmark_processing():
    """Führt Performance-Benchmark durch"""
    logger.info("🚀 Starte Performance-Benchmark...")
    
    # Test-Audio erstellen
    test_audio = create_test_audio(duration_sec=30)  # 30 Sekunden für aussagekräftige Ergebnisse
    
    # Temporäre Dateien
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        input_path = f.name
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        output_path = f.name
    
    try:
        # Test-Audio speichern
        sf.write(input_path, test_audio, 44100)
        logger.info(f"📁 Test-Datei erstellt: {Path(input_path).name} ({len(test_audio)/44100:.1f}s)")
        
        # Processor erstellen
        processor = AudioProcessor(preset='suno')
        
        # Benchmark durchführen
        start_time = time.time()
        result = processor.process_file(input_path, output_path)
        end_time = time.time()
        
        processing_time = end_time - start_time
        audio_duration = len(test_audio) / 44100
        realtime_factor = audio_duration / processing_time
        
        logger.info("📊 BENCHMARK ERGEBNISSE:")
        logger.info(f"   Audio-Dauer: {audio_duration:.1f}s")
        logger.info(f"   Verarbeitungszeit: {processing_time:.2f}s")
        logger.info(f"   Realtime-Faktor: {realtime_factor:.2f}x")
        logger.info(f"   Geschwindigkeit: {'Echtzeit+' if realtime_factor > 1 else 'Langsamer als Echtzeit'}")
        
        # Performance-Klassifikation
        if realtime_factor > 2.0:
            logger.info("🏆 EXZELLENT: Sehr schnelle Verarbeitung")
        elif realtime_factor > 1.0:
            logger.info("✅ GUT: Echtzeit-Verarbeitung möglich")
        else:
            logger.info("⚠️  LANGSAM: Optimierung empfohlen")
            
        return {
            'processing_time': processing_time,
            'audio_duration': audio_duration,
            'realtime_factor': realtime_factor,
            'numpy_version': np.__version__,
            'result': result
        }
        
    finally:
        # Aufräumen
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)

def benchmark_memory():
    """Testet Memory-Performance mit großen Arrays"""
    logger.info("🧠 Teste Memory-Performance...")
    
    # Große Arrays für Memory-Test
    sizes = [44100 * 60 * i for i in [1, 5, 10]]  # 1, 5, 10 Minuten Audio
    
    for size in sizes:
        try:
            # Array-Operationen
            start = time.time()
            
            # Test: Resampling (wichtig für Audio-Processing)
            from scipy.signal import resample_poly
            test_array = np.random.randn(size).astype(np.float32)
            resampled = resample_poly(test_array, 44100, 48000)  # 44.1kHz → 48kHz
            
            end = time.time()
            duration = end - start
            size_mb = size * 4 / (1024 * 1024)  # float32 = 4 bytes
            
            logger.info(f"   {size_mb:.1f}MB Array: {duration:.2f}s ({size_mb/duration:.1f}MB/s)")
            
        except MemoryError:
            logger.info(f"   {size/44100/60:.1f}min Array: Memory Error")
            break

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🎵 AUDIO MASTERING PERFORMANCE BENCHMARK")
    logger.info("=" * 60)
    
    # Library-Versionen anzeigen
    logger.info("📚 AKTUELLE LIBRARY-VERSIONEN:")
    logger.info(f"   NumPy: {np.__version__}")
    logger.info(f"   SciPy: {scipy.__version__}")
    
    try:
        import pyloudnorm
        logger.info(f"   pyloudnorm: {pyloudnorm.__version__}")
    except:
        logger.info("   pyloudnorm: Nicht verfügbar")
    
    logger.info("")
    
    # Benchmarks durchführen
    processing_result = benchmark_processing()
    logger.info("")
    benchmark_memory()
    
    logger.info("")
    logger.info("✅ Benchmark abgeschlossen!")
    logger.info(f"   Key Metric: {processing_result['realtime_factor']:.2f}x Echtzeit")