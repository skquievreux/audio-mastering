#!/usr/bin/env python3
"""
Auto-Updater für Audio Mastering Tool
Lädt neue Releases von Cloudflare/Webserver herunter
"""

import requests
import json
import os
import sys
from pathlib import Path
import subprocess
import tempfile
import hashlib

class Updater:
    """Verwaltet automatische Updates"""

    def __init__(self, update_url="https://your-cloudflare-url.com/releases/"):
        self.update_url = update_url
        self.version_file = Path("version.json")
        self.current_version = self._get_current_version()

    def _get_current_version(self):
        """Lese aktuelle Version"""
        if self.version_file.exists():
            try:
                with open(self.version_file, 'r') as f:
                    data = json.load(f)
                    return data.get('version', '1.0.0')
            except:
                pass
        return '1.0.0'

    def check_for_updates(self):
        """Prüfe auf verfügbare Updates"""
        try:
            response = requests.get(f"{self.update_url}latest.json", timeout=10)
            response.raise_for_status()

            latest_info = response.json()
            latest_version = latest_info['version']

            if self._compare_versions(latest_version, self.current_version) > 0:
                print(f"📦 Update verfügbar: {self.current_version} → {latest_version}")
                return latest_info
            else:
                print(f"✅ Aktuellste Version: {self.current_version}")
                return None

        except Exception as e:
            print(f"⚠️  Update-Check fehlgeschlagen: {e}")
            return None

    def _compare_versions(self, v1, v2):
        """Vergleiche Versionsnummern"""
        def parse_version(v):
            return [int(x) for x in v.split('.')]

        v1_parts = parse_version(v1)
        v2_parts = parse_version(v2)

        for i in range(max(len(v1_parts), len(v2_parts))):
            v1_part = v1_parts[i] if i < len(v1_parts) else 0
            v2_part = v2_parts[i] if i < len(v2_parts) else 0

            if v1_part > v2_part:
                return 1
            elif v1_part < v2_part:
                return -1

        return 0

    def download_update(self, update_info):
        """Lade Update herunter"""
        try:
            download_url = update_info['download_url']
            expected_hash = update_info.get('sha256')

            print(f"⬇️  Lade Update herunter: {download_url}")

            response = requests.get(download_url, stream=True, timeout=60)
            response.raise_for_status()

            # Temporäre Datei
            with tempfile.NamedTemporaryFile(delete=False, suffix='.exe') as temp_file:
                temp_path = temp_file.name

                # Download mit Fortschritt
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0

                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(".1f")

            # Hash prüfen falls verfügbar
            if expected_hash:
                actual_hash = self._calculate_hash(temp_path)
                if actual_hash != expected_hash:
                    os.unlink(temp_path)
                    raise ValueError("Hash-Verifikation fehlgeschlagen!")

            print("✅ Download abgeschlossen")
            return temp_path

        except Exception as e:
            print(f"❌ Download fehlgeschlagen: {e}")
            return None

    def _calculate_hash(self, file_path):
        """Berechne SHA256-Hash"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def install_update(self, installer_path):
        """Installiere Update"""
        try:
            print("🔄 Starte Installation...")

            # Installer ausführen
            result = subprocess.run([installer_path, '/S'], check=True)

            # Version aktualisieren
            new_version = self._extract_version_from_installer(installer_path)
            if new_version:
                self._update_version_file(new_version)

            print("✅ Update erfolgreich installiert!")
            return True

        except Exception as e:
            print(f"❌ Installation fehlgeschlagen: {e}")
            return False

    def _extract_version_from_installer(self, installer_path):
        """Extrahiere Version aus Installer-Namen"""
        filename = Path(installer_path).name
        # Beispiel: AudioMasteringTool_Installer_v1.1.0.exe
        if 'v' in filename:
            version_part = filename.split('v')[1].split('.')[0:3]
            return '.'.join(version_part)
        return None

    def _update_version_file(self, new_version):
        """Aktualisiere Version-Datei"""
        version_data = {
            'version': new_version,
            'updated_at': str(Path(__file__).stat().st_mtime)
        }

        with open(self.version_file, 'w') as f:
            json.dump(version_data, f, indent=2)

    def run_update_check(self):
        """Führe vollständigen Update-Check durch"""
        print("🔍 Prüfe auf Updates...")

        update_info = self.check_for_updates()
        if not update_info:
            return False

        # Benutzer fragen (in GUI-Version)
        # Hier automatisch updaten
        installer_path = self.download_update(update_info)
        if not installer_path:
            return False

        success = self.install_update(installer_path)

        # Temporäre Datei aufräumen
        try:
            os.unlink(installer_path)
        except:
            pass

        return success

# ===== VERWENDUNG =====

if __name__ == "__main__":
    # Cloudflare URL anpassen
    updater = Updater("https://your-cloudflare-url.com/releases/")

    if updater.run_update_check():
        print("🎉 Update erfolgreich!")
    else:
        print("ℹ️  Kein Update verfügbar oder Update fehlgeschlagen")