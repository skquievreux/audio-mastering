
;NSIS Installer Script für Audio Mastering Tool
;Version 1.0.0

!include "MUI2.nsh"
!include "FileFunc.nsh"

Name "Audio Mastering Tool v1.0.0"
OutFile "AudioMasteringTool_Installer_v1.0.0.exe"
Unicode True
InstallDir "$PROGRAMFILES\Audio Mastering Tool"
InstallDirRegKey HKCU "Software\AudioMasteringTool" ""

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
    File "dist\AudioMasteringTool.exe"

    ; Zusätzliche Dateien
    CreateDirectory "$INSTDIR\input"
    CreateDirectory "$INSTDIR\output"
    CreateDirectory "$INSTDIR\logs"

    ; Desktop-Verknüpfung erstellen
    CreateShortCut "$DESKTOP\Audio Mastering Tool.lnk" "$INSTDIR\AudioMasteringTool.exe"

    ; Startmenü-Verknüpfung
    CreateDirectory "$SMPROGRAMS\Audio Mastering Tool"
    CreateShortCut "$SMPROGRAMS\Audio Mastering Tool\Audio Mastering Tool.lnk" "$INSTDIR\AudioMasteringTool.exe"
    CreateShortCut "$SMPROGRAMS\Audio Mastering Tool\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

    ; Registry-Einträge
    WriteRegStr HKCU "Software\AudioMasteringTool" "" $INSTDIR
    WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

Section "Uninstall"
    ; Desktop-Verknüpfung entfernen
    Delete "$DESKTOP\Audio Mastering Tool.lnk"

    ; Startmenü entfernen
    Delete "$SMPROGRAMS\Audio Mastering Tool\Audio Mastering Tool.lnk"
    Delete "$SMPROGRAMS\Audio Mastering Tool\Uninstall.lnk"
    RMDir "$SMPROGRAMS\Audio Mastering Tool"

    ; Programmdateien entfernen
    Delete "$INSTDIR\AudioMasteringTool.exe"
    Delete "$INSTDIR\Uninstall.exe"

    ; Ordner entfernen
    RMDir "$INSTDIR\logs"
    RMDir "$INSTDIR\output"
    RMDir "$INSTDIR\input"
    RMDir "$INSTDIR"

    ; Registry bereinigen
    DeleteRegKey HKCU "Software\AudioMasteringTool"
SectionEnd
