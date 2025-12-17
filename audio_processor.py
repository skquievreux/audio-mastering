"""
Audio-Verarbeitungsklasse für Mastering-Chain
"""

import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from scipy import signal
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Genre-spezifische Mastering-Presets
MASTERING_PRESETS = {
    'default': {
        'target_lufs': -10.0,
        'true_peak': -1.0,
        'comp_threshold': -15,  # Weniger aggressiv
        'comp_ratio': 2.0,      # Weniger aggressiv (statt 2.5)
        'comp_attack': 15,      # Sanfter
        'comp_release': 200,    # Länger
        'use_compression': True
    },

    'gentle': {
        # Für bereits gut gemixte Songs (Suno AI oft schon gut!)
        'target_lufs': -10.0,
        'true_peak': -1.0,
        'comp_threshold': -15,
        'comp_ratio': 2.0,
        'comp_attack': 15,
        'comp_release': 200,
        'use_compression': False  # Nur LUFS + Limiter
    },

    'suno': {
        # Speziell für Suno AI Songs - keine Kompression, nur LUFS + Limiter
        'target_lufs': -10.0,
        'true_peak': -1.0,
        'comp_threshold': -20,  # Nicht verwendet
        'comp_ratio': 1.0,      # Nicht verwendet
        'comp_attack': 20,      # Nicht verwendet
        'comp_release': 200,    # Nicht verwendet
        'use_compression': False  # Keine Kompression für Suno AI
    },

    'aggressive': {
        # Für laute Genres (EDM, Rock)
        'target_lufs': -8.0,
        'true_peak': -1.0,
        'comp_threshold': -10,
        'comp_ratio': 4.0,
        'comp_attack': 5,
        'comp_release': 100,
        'use_compression': True
    },

    'dynamic': {
        # Für Jazz, Klassik (mehr Dynamik)
        'target_lufs': -14.0,
        'true_peak': -1.0,
        'comp_threshold': -18,
        'comp_ratio': 1.5,
        'comp_attack': 20,
        'comp_release': 300,
        'use_compression': True
    },

    'podcast': {
        # Für Sprache
        'target_lufs': -16.0,
        'true_peak': -1.0,
        'comp_threshold': -20,
        'comp_ratio': 3.0,
        'comp_attack': 5,
        'comp_release': 100,
        'use_compression': True
    }
}


def get_preset(name='suno'):
    """Lade Preset nach Name"""
    return MASTERING_PRESETS.get(name, MASTERING_PRESETS['suno'])


class AudioProcessor:
    """
    Verarbeitet einzelne Audio-Dateien durch die Mastering-Chain:
    1. High-Pass Filter (20 Hz)
    2. Kompression (konfigurierbar)
    3. LUFS-Normalisierung
    4. Peak Limiter
    """

    def __init__(self,
                 target_lufs: float = -10.0,
                 true_peak_ceiling: float = -1.0,
                 sample_rate: int = 44100,
                 preset: str = 'suno'):
        # Speichere Preset-Name für Logging
        self._preset_name = preset

        # Lade Preset falls angegeben
        if preset != 'suno':
            config = get_preset(preset)
            self.target_lufs = config['target_lufs']
            self.true_peak_ceiling = config['true_peak']
            self.use_compression = config['use_compression']
            self.comp_threshold = config['comp_threshold']
            self.comp_ratio = config['comp_ratio']
            logger.info(f"🎛️ Verwende Preset '{preset}': LUFS {self.target_lufs}dB, Kompression {'Ja' if self.use_compression else 'Nein'}")
        else:
            self.target_lufs = target_lufs
            self.true_peak_ceiling = true_peak_ceiling
            self.use_compression = False  # Suno AI Standard: keine Kompression
            self.comp_threshold = -20.0  # Default
            self.comp_ratio = 1.0  # Default
            logger.info(f"🎛️ Verwende Suno AI Preset: LUFS {self.target_lufs}dB, Kompression Nein")

        self.sample_rate = sample_rate
        self.meter = pyln.Meter(sample_rate)

    def analyze_audio(self, audio: np.ndarray, step_name: str = "Analyse") -> dict:
        """Führt vollständige Audio-Analyse durch"""
        try:
            lufs = self.meter.integrated_loudness(audio)
            peak_linear = np.max(np.abs(audio))
            peak_db = 20 * np.log10(peak_linear + 1e-10)
            peak_dbtp = self._measure_true_peak(audio)

            # Zusätzliche Metriken
            rms = np.sqrt(np.mean(audio**2))
            crest_factor = peak_db - 20 * np.log10(rms + 1e-10)

            return {
                'lufs': round(lufs, 2),
                'peak_db': round(peak_db, 2),
                'peak_dbtp': round(peak_dbtp, 2),
                'rms_db': round(20 * np.log10(rms + 1e-10), 2),
                'crest_factor': round(crest_factor, 2),
                'dynamic_range': round(peak_db - 20 * np.log10(rms + 1e-10), 2)
            }
        except Exception as e:
            logger.warning(f"Analyse fehlgeschlagen bei {step_name}: {e}")
            return {'lufs': 0, 'peak_db': 0, 'peak_dbtp': 0, 'rms_db': 0, 'crest_factor': 0, 'dynamic_range': 0}

    def process_file(self, input_path: str, output_path: str) -> dict:
        """
        Verarbeitet eine einzelne Audio-Datei mit detaillierter Analyse und Logging

        Args:
            input_path: Pfad zur Input-Datei
            output_path: Pfad zur Output-Datei

        Returns:
            Dict mit Messwerten und Verarbeitungsdetails
        """
        try:
            logger.info(f"🔍 Starte Verarbeitung von {input_path}")

            # 1. Audio laden
            audio, sr = sf.read(input_path)
            logger.info(f"📂 Datei geladen: {audio.shape}, {sr}Hz, Dauer: {len(audio)/sr:.1f}s")

            # Resample falls nötig
            if sr != self.sample_rate:
                logger.info(f"🔄 Resample von {sr}Hz auf {self.sample_rate}Hz")
                audio = self._resample_audio(audio, sr, self.sample_rate)
                sr = self.sample_rate

            # VORHER-Analyse
            original_analysis = self.analyze_audio(audio, "Original")
            logger.info(f"📊 ORIGINAL - LUFS: {original_analysis['lufs']}dB, Peak: {original_analysis['peak_dbtp']}dBTP, RMS: {original_analysis['rms_db']}dB")

            # 2. High-Pass Filter
            logger.info("🎛️  Schritt 1: High-Pass Filter (20Hz)")
            audio = self._apply_high_pass(audio, sr)
            hp_analysis = self.analyze_audio(audio, "Nach High-Pass")
            logger.info(f"   → LUFS: {hp_analysis['lufs']}dB (Δ{round(hp_analysis['lufs'] - original_analysis['lufs'], 2)}dB)")

            # 3. LUFS-Normalisierung (mit intelligentem Anti-Clipping)
            logger.info(f"📏 Schritt 2: LUFS-Normalisierung auf {self.target_lufs}dB")
            audio = self._normalize_lufs_smart(audio, self.target_lufs)
            lufs_analysis = self.analyze_audio(audio, "Nach LUFS-Norm")
            logger.info(f"   → LUFS: {lufs_analysis['lufs']}dB (Δ{round(lufs_analysis['lufs'] - hp_analysis['lufs'], 2)}dB)")

            # 4. Kompression (falls aktiviert - NACH Normalisierung!)
            if self.use_compression:
                logger.info(f"🗜️  Schritt 3: Kompression ({self.comp_ratio}:1 @ {self.comp_threshold}dB)")
                audio = self._apply_compression(audio, self.comp_ratio, self.comp_threshold)
                comp_analysis = self.analyze_audio(audio, "Nach Kompression")
                logger.info(f"   → LUFS: {comp_analysis['lufs']}dB (Δ{round(comp_analysis['lufs'] - lufs_analysis['lufs'], 2)}dB)")
            else:
                logger.info("🗜️  Schritt 3: Kompression übersprungen (Preset: gentle/suno)")
                comp_analysis = lufs_analysis

            # 5. Peak Limiter (NACH Kompression für korrekte Reihenfolge!)
            logger.info(f"🔊 Schritt 4: Peak Limiter ({self.true_peak_ceiling}dBTP)")
            audio = self._apply_peak_limiter(audio)
            limiter_analysis = self.analyze_audio(audio, "Nach Limiter")
            logger.info(f"   → Peak: {limiter_analysis['peak_dbtp']}dBTP (Δ{round(limiter_analysis['peak_dbtp'] - comp_analysis['peak_dbtp'], 2)}dB)")

            # 6. Speichern
            logger.info(f"💾 Speichere als {output_path}")
            sf.write(output_path, audio, sr, subtype='PCM_16')

            # Finale Analyse
            final_analysis = self.analyze_audio(audio, "Final")
            logger.info(f"✅ VERARBEITUNG ABGESCHLOSSEN")
            logger.info(f"   Original → Final: LUFS {original_analysis['lufs']}dB → {final_analysis['lufs']}dB")
            logger.info(f"   Peak: {original_analysis['peak_dbtp']}dBTP → {final_analysis['peak_dbtp']}dBTP")
            logger.info(f"   Dynamik: {original_analysis['dynamic_range']}dB → {final_analysis['dynamic_range']}dB")

            results = {
                'original': original_analysis,
                'final': final_analysis,
                'processing_steps': {
                    'high_pass': hp_analysis,
                    'lufs_norm': lufs_analysis,
                    'compression': comp_analysis if self.use_compression else None,
                    'limiter': limiter_analysis
                },
                'duration_sec': len(audio) / sr,
                'channels': audio.shape[1] if audio.ndim == 2 else 1,
                'sample_rate': sr,
                'preset_used': getattr(self, '_preset_name', 'custom')
            }

            return results

        except Exception as e:
            logger.error(f"❌ Fehler bei Verarbeitung von {input_path}: {str(e)}")
            raise

    def _resample_audio(self, audio: np.ndarray, from_sr: int, to_sr: int) -> np.ndarray:
        """Resample Audio auf Ziel-Sample-Rate"""
        if audio.ndim == 1:
            return signal.resample(audio, int(len(audio) * to_sr / from_sr))
        else:
            return np.column_stack([
                signal.resample(audio[:, 0], int(len(audio) * to_sr / from_sr)),
                signal.resample(audio[:, 1], int(len(audio) * to_sr / from_sr))
            ])

    def _apply_high_pass(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """High-Pass Filter bei 20 Hz"""
        sos = signal.butter(4, 20, 'hp', fs=sr, output='sos')

        if audio.ndim == 1:
            return signal.sosfilt(sos, audio)
        else:
            return np.column_stack([
                signal.sosfilt(sos, audio[:, 0]),
                signal.sosfilt(sos, audio[:, 1])
            ])

    def _apply_compression(self, audio: np.ndarray, ratio: float = 3.0, threshold_db: float = -20.0) -> np.ndarray:
        """Einfache Kompression"""
        audio_db = 20 * np.log10(np.abs(audio) + 1e-10)
        over_threshold = audio_db > threshold_db
        compressed_db = np.where(over_threshold,
                                threshold_db + (audio_db - threshold_db) / ratio,
                                audio_db)
        compressed_linear = 10 ** (compressed_db / 20)
        return np.sign(audio) * compressed_linear

    def _normalize_lufs(self, audio: np.ndarray) -> np.ndarray:
        """Normalisiere auf Ziel-LUFS"""
        try:
            loudness = self.meter.integrated_loudness(audio)
            return pyln.normalize.loudness(audio, loudness, self.target_lufs)
        except Exception as e:
            logger.warning(f"LUFS-Normalisierung fehlgeschlagen: {e}, verwende Original")
            return audio

    def _normalize_lufs_smart(self, audio: np.ndarray, target_lufs: float) -> np.ndarray:
        """Intelligente LUFS-Normalisierung mit Soft-Limiting"""
        try:
            # Original-Lautstärke messen
            original_loudness = self.meter.integrated_loudness(audio)

            # Berechne benötigte Verstärkung
            gain_db = target_lufs - original_loudness

            # Test-Normalisierung
            test_audio = audio * 10 ** (gain_db / 20)

            # Prüfe True Peak nach Normalisierung
            test_peak = self._measure_true_peak(test_audio)

            if test_peak > self.true_peak_ceiling:
                # Zu viel Gain - verwende Soft-Limiting Strategie
                # Berechne maximal möglichen Gain ohne Clipping
                max_safe_gain_db = gain_db - (test_peak - self.true_peak_ceiling) - 0.5  # 0.5dB Headroom
                max_safe_gain_linear = 10 ** (max_safe_gain_db / 20)

                logger.info(f"🛡️  Smart Limiting: Peak {test_peak:.1f}dBTP > {self.true_peak_ceiling}dBTP, Gain auf {max_safe_gain_db:.1f}dB begrenzt")
                audio = audio * max_safe_gain_linear

                # Nach-Normalisierung falls noch nicht nah genug am Ziel
                current_loudness = self.meter.integrated_loudness(audio)
                if abs(current_loudness - target_lufs) > 1.0:  # Mehr als 1dB Abweichung
                    remaining_gain_db = target_lufs - current_loudness
                    # Begrenze Nach-Normalisierung auf 2dB
                    remaining_gain_db = max(-2.0, min(2.0, remaining_gain_db))
                    audio = audio * 10 ** (remaining_gain_db / 20)
                    logger.info(f"🔄 Nach-Normalisierung: +{remaining_gain_db:.1f}dB für genauere Zielerreichung")

                return audio
            else:
                # Normalisierung sicher möglich
                return pyln.normalize.loudness(audio, original_loudness, target_lufs)

        except Exception as e:
            logger.warning(f"Intelligente LUFS-Normalisierung fehlgeschlagen: {e}, verwende Original")
            return audio

    def _apply_peak_limiter(self, audio: np.ndarray) -> np.ndarray:
        """Peak Limiter für True Peak"""
        ceiling_linear = 10 ** (self.true_peak_ceiling / 20)
        return np.clip(audio, -ceiling_linear, ceiling_linear)

    def _measure_true_peak(self, audio: np.ndarray) -> float:
        """Messe True Peak in dBTP"""
        peak_linear = np.max(np.abs(audio))
        if peak_linear == 0:
            return -float('inf')
        return 20 * np.log10(peak_linear)


# Erweiterte Nutzung:
if __name__ == "__main__":
    print("Verfügbare Presets:")
    for name, config in MASTERING_PRESETS.items():
        print(f"\n{name}:")
        print(f"  Target LUFS: {config['target_lufs']}")
        print(f"  Kompression: {'Ja' if config['use_compression'] else 'Nein'}")
        if config['use_compression']:
            print(f"  Ratio: {config['comp_ratio']}:1")