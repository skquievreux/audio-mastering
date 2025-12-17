#!/usr/bin/env python3
"""
Audio Mastering Automation Tool

Batch-Verarbeitung von Audio-Dateien mit professioneller Mastering-Chain.
"""

import argparse
import logging
import sys
import threading
import webbrowser
import time
from datetime import datetime
from pathlib import Path

from config import INPUT_DIR, OUTPUT_DIR, LOGS_DIR
from batch_processor import BatchProcessor
from web_server import app


def setup_logging(log_level: str = "INFO") -> None:
    """Konfiguriert Logging"""
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Konsole-Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))

    # Datei-Handler
    log_filename = f"mastering_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_path = LOGS_DIR / log_filename
    LOGS_DIR.mkdir(exist_ok=True)

    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(log_format, date_format))

    # Root-Logger konfigurieren
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=[console_handler, file_handler]
    )


def parse_arguments() -> argparse.Namespace:
    """Parst Kommandozeilen-Argumente"""
    from audio_processor import MASTERING_PRESETS

    parser = argparse.ArgumentParser(
        description="Audio Mastering Automation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Beispiele:
  python mastering_tool.py                    # Standard-Ordner verwenden
  python mastering_tool.py -i ./my_input -o ./my_output  # Benutzerdefinierte Ordner
  python mastering_tool.py --verbose          # Detaillierte Ausgabe
  python mastering_tool.py --preset gentle    # Gentle Preset für Suno AI

Verfügbare Presets:
{chr(10).join(f"  {name}: {config['target_lufs']}dB LUFS" for name, config in MASTERING_PRESETS.items())}
        """
    )

    parser.add_argument(
        "-i", "--input",
        type=str,
        default=str(INPUT_DIR),
        help=f"Input-Ordner (Standard: {INPUT_DIR})"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default=str(OUTPUT_DIR),
        help=f"Output-Ordner (Standard: {OUTPUT_DIR})"
    )

    parser.add_argument(
        "--preset",
        type=str,
        default="suno",  # ← Geändert von 'default' zu 'suno'
        choices=list(MASTERING_PRESETS.keys()),
        help="Mastering-Preset verwenden (Standard: suno)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Detaillierte Ausgabe aktivieren"
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Anzahl paralleler Worker (Standard: 1)"
    )

    parser.add_argument(
        "--web",
        action="store_true",
        help="Webserver nach Verarbeitung starten"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port für Webserver (Standard: 8080)"
    )

    return parser.parse_args()


def validate_directories(input_dir: Path, output_dir: Path) -> bool:
    """Validiert Input/Output-Ordner"""
    if not input_dir.exists():
        print(f"❌ Fehler: Input-Ordner '{input_dir}' existiert nicht!")
        return False

    if not input_dir.is_dir():
        print(f"❌ Fehler: '{input_dir}' ist kein Ordner!")
        return False

    # Output-Ordner wird automatisch erstellt
    output_dir.mkdir(parents=True, exist_ok=True)

    return True


def start_web_server(port: int = 8080) -> None:
    """Webserver in separatem Thread starten"""
    def run_server():
        try:
            logger = logging.getLogger(__name__)
            logger.info(f"🌐 Webserver startet auf Port {port}")
            app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
        except Exception as e:
            logger.error(f"❌ Webserver-Fehler: {e}")

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Warte kurz, bis Server gestartet ist
    time.sleep(1)

    # Browser öffnen
    try:
        url = f"http://localhost:{port}"
        webbrowser.open(url)
        logger = logging.getLogger(__name__)
        logger.info(f"🌐 Browser geöffnet: {url}")
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"⚠️  Browser konnte nicht automatisch geöffnet werden: {e}")
        logger.info(f"🌐 Webserver läuft unter: http://localhost:{port}")


def main() -> int:
    """Hauptfunktion"""
    try:
        # Argumente parsen
        args = parse_arguments()

        # Logging einrichten
        log_level = "DEBUG" if args.verbose else "INFO"
        setup_logging(log_level)

        logger = logging.getLogger(__name__)
        logger.info("🎵 Audio Mastering Tool gestartet")

        # Pfade validieren
        input_dir = Path(args.input)
        output_dir = Path(args.output)

        if not validate_directories(input_dir, output_dir):
            return 1

        logger.info(f"Input-Ordner: {input_dir.absolute()}")
        logger.info(f"Output-Ordner: {output_dir.absolute()}")

        # Batch-Verarbeitung starten
        processor = BatchProcessor(input_dir, output_dir, preset=args.preset)
        results = processor.process_batch(max_workers=args.workers)

        # Report generieren und anzeigen
        report = processor.generate_report(results)
        print("\n" + report)

        # Erfolg/Failure basierend auf Ergebnissen
        if results['files_failed'] > 0:
            logger.warning(f"⚠️  {results['files_failed']} Dateien konnten nicht verarbeitet werden")
            return 1
        elif results['files_processed'] == 0:
            logger.warning("⚠️  Keine Dateien zur Verarbeitung gefunden")
            return 1
        else:
            logger.info(f"✅ {results['files_processed']} Dateien erfolgreich verarbeitet")

            # Webserver starten falls gewünscht
            if args.web:
                start_web_server(args.port)

                # Bei Webserver-Modus: Warte auf Benutzerabbruch
                try:
                    print(f"\n🌐 Webserver läuft auf http://localhost:{args.port}")
                    print("Drücke Ctrl+C zum Beenden...")
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n❌ Webserver beendet")
                    return 0

            return 0

    except KeyboardInterrupt:
        print("\n❌ Abbruch durch Benutzer")
        return 1
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"❌ Unerwarteter Fehler: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())