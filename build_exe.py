#!/usr/bin/env python3
"""
Build-Script für Audio Mastering Tool
Erstellt eine ausführbare EXE-Datei mit PyInstaller
"""

import os
import sys
import subprocess
from pathlib import Path

def build_exe():
    """Erstelle EXE mit PyInstaller"""
    print("🔨 Baue Audio Mastering Tool EXE...")

    # PyInstaller-Befehl
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # Einzelne EXE-Datei
        "--console",  # Konsole für Debugging (ändern zu --windowed für Release)
        "--name", "AudioMasteringTool",
        "--hidden-import", "scipy",
        "--hidden-import", "scipy.signal",
        "--hidden-import", "pyloudnorm",
        "--hidden-import", "soundfile",
        "--hidden-import", "numpy",
        "--hidden-import", "flask",
        "--hidden-import", "requests",
        "mastering_tool.py"
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ EXE erfolgreich erstellt!")
        print(f"📁 Ausgabe: dist/AudioMasteringTool.exe")

        # Prüfe Dateigröße
        exe_path = Path("dist/AudioMasteringTool.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📏 Größe: {size_mb:.1f} MB")
        else:
            print("❌ EXE-Datei nicht gefunden")

    except subprocess.CalledProcessError as e:
        print(f"❌ Build fehlgeschlagen: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

    return True

def create_installer():
    """Erstelle NSIS-Installer"""
    print("📦 Erstelle NSIS-Installer...")

    nsis_script = f"""
;NSIS Installer Script für Audio Mastering Tool
;Version 1.0.0

!include "MUI2.nsh"
!include "FileFunc.nsh"

Name "Audio Mastering Tool v1.0.0"
OutFile "AudioMasteringTool_Installer_v1.0.0.exe"
Unicode True
InstallDir "$PROGRAMFILES\\Audio Mastering Tool"
InstallDirRegKey HKCU "Software\\AudioMasteringTool" ""

;Modern UI Konfiguration
!define MUI_ABORTWARNING
!define MUI_ICON "icon.ico" ; Falls vorhanden
!define MUI_UNICON "icon.ico"

;Willkommens-Seite
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

;Sprachen
!insertmacro MUI_LANGUAGE "German"

Section "Audio Mastering Tool" SecApp
    SectionIn RO

    SetOutPath "$INSTDIR"

    ; Haupt-EXE kopieren
    File "dist\\AudioMasteringTool.exe"

    ; Zusätzliche Dateien
    CreateDirectory "$INSTDIR\\input"
    CreateDirectory "$INSTDIR\\output"
    CreateDirectory "$INSTDIR\\logs"

    ; Desktop-Verknüpfung erstellen
    CreateShortCut "$DESKTOP\\Audio Mastering Tool.lnk" "$INSTDIR\\AudioMasteringTool.exe"

    ; Startmenü-Verknüpfung
    CreateDirectory "$SMPROGRAMS\\Audio Mastering Tool"
    CreateShortCut "$SMPROGRAMS\\Audio Mastering Tool\\Audio Mastering Tool.lnk" "$INSTDIR\\AudioMasteringTool.exe"
    CreateShortCut "$SMPROGRAMS\\Audio Mastering Tool\\Uninstall.lnk" "$INSTDIR\\Uninstall.exe"

    ; Registry-Einträge
    WriteRegStr HKCU "Software\\AudioMasteringTool" "" $INSTDIR
    WriteUninstaller "$INSTDIR\\Uninstall.exe"

SectionEnd

Section "Uninstall"
    ; Desktop-Verknüpfung entfernen
    Delete "$DESKTOP\\Audio Mastering Tool.lnk"

    ; Startmenü entfernen
    Delete "$SMPROGRAMS\\Audio Mastering Tool\\Audio Mastering Tool.lnk"
    Delete "$SMPROGRAMS\\Audio Mastering Tool\\Uninstall.lnk"
    RMDir "$SMPROGRAMS\\Audio Mastering Tool"

    ; Programmdateien entfernen
    Delete "$INSTDIR\\AudioMasteringTool.exe"
    Delete "$INSTDIR\\Uninstall.exe"

    ; Ordner entfernen
    RMDir "$INSTDIR\\logs"
    RMDir "$INSTDIR\\output"
    RMDir "$INSTDIR\\input"
    RMDir "$INSTDIR"

    ; Registry bereinigen
    DeleteRegKey HKCU "Software\\AudioMasteringTool"
SectionEnd
"""

    # NSIS-Script speichern
    with open("installer.nsi", "w", encoding="utf-8") as f:
        f.write(nsis_script)

    print("📝 NSIS-Script erstellt: installer.nsi")

    # Installer kompilieren (falls makensis verfügbar)
    try:
        result = subprocess.run(["makensis", "installer.nsi"], check=True, capture_output=True, text=True)
        print("✅ Installer erfolgreich kompiliert!")
        print("📁 Ausgabe: AudioMasteringTool_Installer_v1.0.0.exe")
    except FileNotFoundError:
        print("⚠️  makensis nicht gefunden. Installer manuell kompilieren:")
        print("   makensis installer.nsi")
    except subprocess.CalledProcessError as e:
        print(f"❌ Installer-Kompilierung fehlgeschlagen: {e}")

if __name__ == "__main__":
    print("🚀 Audio Mastering Tool - Build & Package")
    print("=" * 50)

    # EXE bauen
    if build_exe():
        print()

        # Installer erstellen
        create_installer()

        print()
        print("🎉 Build abgeschlossen!")
        print("📦 Verwende 'AudioMasteringTool_Installer_v1.0.0.exe' für die Installation")
    else:
        print("❌ Build fehlgeschlagen!")
        sys.exit(1)