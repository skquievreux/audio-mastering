"""
Batch-Verarbeitung für mehrere Audio-Dateien
"""

from pathlib import Path
from typing import List, Dict, Optional
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import INPUT_DIR, OUTPUT_DIR, LOGS_DIR, SUPPORTED_EXTENSIONS, MASTERED_SUFFIX
from audio_processor import AudioProcessor

logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    Verwaltet Batch-Verarbeitung von Audio-Dateien:
    - Findet alle unterstützten Dateien im Input-Ordner
    - Verarbeitet sie parallel oder sequentiell
    - Sammelt Ergebnisse für Report
    """

    def __init__(self, input_dir: Path = INPUT_DIR, output_dir: Path = OUTPUT_DIR, preset: str = 'default'):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.processor = AudioProcessor(preset=preset)

        # Erstelle Output-Ordner falls nicht vorhanden
        self.output_dir.mkdir(exist_ok=True)

    def discover_files(self) -> List[Path]:
        """Findet alle unterstützten Audio-Dateien im Input-Ordner"""
        if not self.input_dir.exists():
            logger.warning(f"Input-Ordner {self.input_dir} existiert nicht")
            return []

        files = []
        for ext in SUPPORTED_EXTENSIONS:
            files.extend(self.input_dir.glob(f"*{ext}"))
            files.extend(self.input_dir.glob(f"*{ext.upper()}"))

        return sorted(list(set(files)))  # Entferne Duplikate und sortiere

    def process_batch(self, max_workers: int = 1) -> Dict[str, any]:
        """
        Verarbeitet alle Dateien im Batch

        Args:
            max_workers: Anzahl paralleler Worker (1 = sequentiell)

        Returns:
            Dict mit Ergebnissen und Statistiken
        """
        files = self.discover_files()
        if not files:
            logger.warning("Keine Audio-Dateien im Input-Ordner gefunden")
            return {
                'files_processed': 0,
                'files_failed': 0,
                'total_time_sec': 0.0,
                'avg_time_per_file': 0.0,
                'results': [],
                'errors': []
            }

        logger.info(f"Starte Batch-Verarbeitung von {len(files)} Dateien")

        results = []
        errors = []
        start_time = time.time()

        if max_workers == 1:
            # Sequentiell verarbeiten
            for i, input_file in enumerate(files, 1):
                logger.info(f"Verarbeite {i}/{len(files)}: {input_file.name}")
                try:
                    result = self._process_single_file(input_file)
                    results.append(result)
                except Exception as e:
                    error_info = {
                        'file': str(input_file),
                        'error': str(e)
                    }
                    errors.append(error_info)
                    logger.error(f"Fehler bei {input_file.name}: {e}")
        else:
            # Parallel verarbeiten (für zukünftige Erweiterung)
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(self._process_single_file, f) for f in files]
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        # Fehler-Handling für parallele Verarbeitung
                        errors.append({'error': str(e)})

        total_time = time.time() - start_time

        summary = {
            'files_processed': len(results),
            'files_failed': len(errors),
            'total_time_sec': round(total_time, 2),
            'avg_time_per_file': round(total_time / len(files), 2) if files else 0,
            'results': results,
            'errors': errors
        }

        logger.info(f"Batch-Verarbeitung abgeschlossen: {len(results)} erfolgreich, {len(errors)} Fehler")
        return summary

    def _process_single_file(self, input_file: Path) -> Dict[str, any]:
        """Verarbeitet eine einzelne Datei"""
        # Output-Dateiname generieren
        stem = input_file.stem
        suffix = input_file.suffix.lower()
        output_filename = f"{stem}{MASTERED_SUFFIX}{suffix}"
        output_path = self.output_dir / output_filename

        # Verarbeiten
        result = self.processor.process_file(str(input_file), str(output_path))

        # Zusätzliche Metadaten
        result.update({
            'input_file': str(input_file),
            'output_file': str(output_path),
            'original_size_mb': round(input_file.stat().st_size / (1024*1024), 2),
            'output_size_mb': round(output_path.stat().st_size / (1024*1024), 2) if output_path.exists() else 0
        })

        return result

    def generate_report(self, batch_results: Dict[str, any]) -> str:
        """Generiert einen detaillierten Report mit Vorher/Nachher Analyse"""
        results = batch_results['results']
        errors = batch_results['errors']

        report_lines = []
        report_lines.append("=" * 100)
        report_lines.append("🎵 AUDIO MASTERING BATCH REPORT - DETAILLIERT")
        report_lines.append("=" * 100)
        report_lines.append("")

        # Zusammenfassung
        report_lines.append("📊 ZUSAMMENFASSUNG:")
        report_lines.append(f"  ✅ Verarbeitete Dateien: {batch_results['files_processed']}")
        report_lines.append(f"  ❌ Fehlerhafte Dateien: {batch_results['files_failed']}")
        report_lines.append(f"  ⏱️  Gesamtzeit: {batch_results['total_time_sec']} Sekunden")
        report_lines.append(f"  📈 Durchschnitt pro Datei: {batch_results['avg_time_per_file']} Sekunden")
        report_lines.append("")

        if results:
            report_lines.append("🎛️  VERARBEITETE DATEIEN:")
            report_lines.append("-" * 100)

            for result in results:
                filename = Path(result['input_file']).name
                orig = result['original']
                final = result['final']

                report_lines.append(f"📁 {filename}")
                report_lines.append(f"   Original: LUFS {orig['lufs']}dB | Peak {orig['peak_dbtp']}dBTP | RMS {orig['rms_db']}dB | Dyn {orig['dynamic_range']}dB")
                report_lines.append(f"   Final:    LUFS {final['lufs']}dB | Peak {final['peak_dbtp']}dBTP | RMS {final['rms_db']}dB | Dyn {final['dynamic_range']}dB")
                report_lines.append(f"   Δ:        LUFS {round(final['lufs'] - orig['lufs'], 1)}dB | Peak {round(final['peak_dbtp'] - orig['peak_dbtp'], 1)}dB | RMS {round(final['rms_db'] - orig['rms_db'], 1)}dB")
                report_lines.append(f"   Dauer: {result['duration_sec']:.1f}s | Kanäle: {result['channels']} | Preset: {result.get('preset_used', 'unknown')}")
                report_lines.append("")

        if errors:
            report_lines.append("❌ FEHLER:")
            report_lines.append("-" * 80)
            for error in errors:
                report_lines.append(f"  📁 {error.get('file', 'Unbekannt')}: {error['error']}")
            report_lines.append("")

        # Detaillierte Analyse falls nur eine Datei
        if len(results) == 1:
            result = results[0]
            report_lines.append("🔍 DETAILLIERTER VERARBEITUNGSVERLAUF:")
            report_lines.append("-" * 80)

            steps = result.get('processing_steps', {})
            orig = result['original']

            report_lines.append("1. ORIGINAL")
            report_lines.append(f"   LUFS: {orig['lufs']}dB | Peak: {orig['peak_dbtp']}dBTP | RMS: {orig['rms_db']}dB")
            report_lines.append("")

            if 'high_pass' in steps and steps['high_pass']:
                hp = steps['high_pass']
                report_lines.append("2. NACH HIGH-PASS FILTER (20Hz)")
                report_lines.append(f"   LUFS: {hp['lufs']}dB (Δ{round(hp['lufs'] - orig['lufs'], 1)}dB)")
                report_lines.append("")

            if 'compression' in steps and steps['compression']:
                comp = steps['compression']
                prev = steps.get('high_pass', orig)
                report_lines.append("3. NACH KOMPRESSION")
                report_lines.append(f"   LUFS: {comp['lufs']}dB (Δ{round(comp['lufs'] - prev['lufs'], 1)}dB)")
                report_lines.append("")

            if 'lufs_norm' in steps:
                lufs = steps['lufs_norm']
                prev = steps.get('compression', steps.get('high_pass', orig))
                report_lines.append("4. NACH LUFS-NORMALISIERUNG")
                report_lines.append(f"   LUFS: {lufs['lufs']}dB (Δ{round(lufs['lufs'] - prev['lufs'], 1)}dB)")
                report_lines.append("")

            if 'limiter' in steps:
                lim = steps['limiter']
                prev = steps.get('lufs_norm', orig)
                report_lines.append("5. NACH PEAK-LIMITER")
                report_lines.append(f"   Peak: {lim['peak_dbtp']}dBTP (Δ{round(lim['peak_dbtp'] - prev['peak_dbtp'], 1)}dB)")
                report_lines.append("")

        report_lines.append("=" * 100)

        return "\n".join(report_lines)