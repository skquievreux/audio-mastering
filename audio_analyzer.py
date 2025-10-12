"""
Analyse-Tool für Vorher/Nachher Vergleich
Erstellt detaillierte Reports und visualisiert Änderungen
"""

import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from pathlib import Path
import json


class AudioAnalyzer:
    """Detaillierte Audio-Analyse"""

    def __init__(self):
        self.meter_44k = pyln.Meter(44100)
        self.meter_48k = pyln.Meter(48000)

    def analyze_file(self, filepath):
        """Vollständige Analyse einer Audio-Datei"""
        audio, sr = sf.read(filepath)

        # Meter wählen
        meter = self.meter_44k if sr == 44100 else self.meter_48k

        # LUFS Messung
        lufs_integrated = meter.integrated_loudness(audio)

        # Peak Messungen
        peak_sample = np.max(np.abs(audio))
        peak_db = 20 * np.log10(peak_sample + 1e-10)

        # RMS (Root Mean Square)
        rms = np.sqrt(np.mean(audio ** 2))
        rms_db = 20 * np.log10(rms + 1e-10)

        # Crest Factor (Dynamik-Indikator)
        crest_factor = peak_sample / (rms + 1e-10)
        crest_factor_db = 20 * np.log10(crest_factor)

        # Stereo-Analyse
        if audio.ndim == 2:
            # Stereo Width
            mid = (audio[:, 0] + audio[:, 1]) / 2
            side = (audio[:, 0] - audio[:, 1]) / 2

            mid_rms = np.sqrt(np.mean(mid ** 2))
            side_rms = np.sqrt(np.mean(side ** 2))

            stereo_width = side_rms / (mid_rms + 1e-10)

            # Balance
            left_rms = np.sqrt(np.mean(audio[:, 0] ** 2))
            right_rms = np.sqrt(np.mean(audio[:, 1] ** 2))
            balance = (right_rms - left_rms) / (right_rms + left_rms + 1e-10)
        else:
            stereo_width = 0
            balance = 0

        # Clipping Detection
        clipped_samples = np.sum(np.abs(audio) >= 0.99)
        clipping_percentage = (clipped_samples / audio.size) * 100

        return {
            'filename': Path(filepath).name,
            'sample_rate': sr,
            'duration_sec': len(audio) / sr,
            'channels': audio.shape[1] if audio.ndim == 2 else 1,

            # Lautstärke
            'lufs_integrated': round(lufs_integrated, 2),
            'peak_db': round(peak_db, 2),
            'rms_db': round(rms_db, 2),

            # Dynamik
            'crest_factor_db': round(crest_factor_db, 2),

            # Stereo
            'stereo_width': round(stereo_width, 3),
            'balance': round(balance, 3),

            # Qualität
            'clipped_samples': int(clipped_samples),
            'clipping_percentage': round(clipping_percentage, 4),
            'is_clipped': clipping_percentage > 0.01
        }

    def compare_files(self, original_path, mastered_path):
        """Vergleiche Original vs. Mastered"""
        orig = self.analyze_file(original_path)
        mast = self.analyze_file(mastered_path)

        return {
            'original': orig,
            'mastered': mast,
            'delta': {
                'lufs_db': round(mast['lufs_integrated'] - orig['lufs_integrated'], 2),
                'peak_db': round(mast['peak_db'] - orig['peak_db'], 2),
                'rms_db': round(mast['rms_db'] - orig['rms_db'], 2),
                'crest_factor_db': round(mast['crest_factor_db'] - orig['crest_factor_db'], 2),
            }
        }

    def batch_compare(self, input_folder, output_folder):
        """Vergleiche alle Dateien in beiden Ordnern"""
        input_path = Path(input_folder)
        output_path = Path(output_folder)

        comparisons = []

        for orig_file in input_path.glob("*.wav"):
            # Finde gemasterte Version
            mastered_name = orig_file.stem + "_mastered.wav"
            mastered_file = output_path / mastered_name

            if not mastered_file.exists():
                print(f"⚠️  Keine gemasterte Version für {orig_file.name}")
                continue

            print(f"🔍 Vergleiche: {orig_file.name}")
            comparison = self.compare_files(str(orig_file), str(mastered_file))
            comparisons.append(comparison)

        return comparisons

    def print_comparison_report(self, comparisons):
        """Drucke übersichtlichen Vergleichs-Report"""
        print("\n" + "="*100)
        print("📊 DETAILLIERTER VORHER/NACHHER VERGLEICH")
        print("="*100)

        for comp in comparisons:
            orig = comp['original']
            mast = comp['mastered']
            delta = comp['delta']

            print(f"\n📁 {orig['filename']}")
            print(f"{'─'*100}")

            # Lautstärke
            print(f"\n  📈 LAUTSTÄRKE:")
            print(f"     LUFS:  {orig['lufs_integrated']:>7.2f} dB  →  {mast['lufs_integrated']:>7.2f} dB  (Δ {delta['lufs_db']:>+6.2f} dB)")
            print(f"     Peak:  {orig['peak_db']:>7.2f} dB  →  {mast['peak_db']:>7.2f} dB  (Δ {delta['peak_db']:>+6.2f} dB)")
            print(f"     RMS:   {orig['rms_db']:>7.2f} dB  →  {mast['rms_db']:>7.2f} dB  (Δ {delta['rms_db']:>+6.2f} dB)")

            # Dynamik
            print(f"\n  🎚️  DYNAMIK:")
            print(f"     Crest Factor: {orig['crest_factor_db']:>5.2f} dB  →  {mast['crest_factor_db']:>5.2f} dB  (Δ {delta['crest_factor_db']:>+5.2f} dB)")

            # Stereo
            if orig['channels'] == 2:
                print(f"\n  🔊 STEREO:")
                print(f"     Width:   {orig['stereo_width']:>5.3f}  →  {mast['stereo_width']:>5.3f}")
                print(f"     Balance: {orig['balance']:>+5.3f}  →  {mast['balance']:>+5.3f}")

            # Qualität
            print(f"\n  ✅ QUALITÄT:")
            print(f"     Original Clipping:  {orig['is_clipped']} ({orig['clipped_samples']} Samples)")
            print(f"     Mastered Clipping:  {mast['is_clipped']} ({mast['clipped_samples']} Samples)")

            # Warnung bei Problemen
            if mast['is_clipped'] and mast['clipping_percentage'] > 0.1:
                print(f"     ⚠️  WARNUNG: Signifikantes Clipping erkannt! ({mast['clipping_percentage']:.2f}%)")

            if delta['crest_factor_db'] < -3:
                print(f"     ⚠️  WARNUNG: Dynamik stark reduziert ({delta['crest_factor_db']:.1f} dB)")

        print("\n" + "="*100)

        # Zusammenfassung
        avg_lufs_delta = np.mean([c['delta']['lufs_db'] for c in comparisons])
        avg_crest_delta = np.mean([c['delta']['crest_factor_db'] for c in comparisons])

        print(f"\n📊 DURCHSCHNITT ÜBER ALLE DATEIEN:")
        print(f"   LUFS Erhöhung:        {avg_lufs_delta:>+6.2f} dB")
        print(f"   Dynamik-Veränderung:  {avg_crest_delta:>+6.2f} dB")

        # Empfehlungen
        print(f"\n💡 EMPFEHLUNGEN:")
        if avg_crest_delta < -2:
            print("   ⚠️  Dynamik wird stark komprimiert - erwäge sanfteres Preset")
        if any(c['mastered']['is_clipped'] for c in comparisons):
            print("   ⚠️  Clipping erkannt - True Peak Ceiling erhöhen auf -1.5 dBTP")
        else:
            print("   ✅ Keine Qualitätsprobleme erkannt")

        print("="*100 + "\n")

    def export_json(self, comparisons, output_file):
        """Exportiere Analyse als JSON"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comparisons, f, indent=2)
        print(f"💾 Analyse gespeichert: {output_file}")


# ===== NUTZUNG =====

if __name__ == "__main__":
    analyzer = AudioAnalyzer()

    # Pfade anpassen
    INPUT_FOLDER = r"C:\CODE\GIT\Audio-Mastering\input"
    OUTPUT_FOLDER = r"C:\CODE\GIT\Audio-Mastering\output"

    # Batch-Vergleich
    comparisons = analyzer.batch_compare(INPUT_FOLDER, OUTPUT_FOLDER)

    # Report ausgeben
    analyzer.print_comparison_report(comparisons)

    # JSON exportieren (optional)
    # analyzer.export_json(comparisons, "mastering_analysis.json")