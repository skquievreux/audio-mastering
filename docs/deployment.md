---
description: "Deployment durchführen"
---

**Optimierter Prompt für das Einchecken und Publizieren eines Python Audio-Mastering Tools mit NSIS-Installer und Cloudflare Deployment**

Bitte führe die folgenden Schritte aus, um dein Python Audio-Mastering Tool einzucecken und zu veröffentlichen. Passe die Schritte basierend auf der Versionsart (Patch, Minor, Major) an, wobei Patch-Releases schneller und mit weniger Sorgfalt durchgeführt werden sollen. Folge der Reihenfolge, um einen reibungslosen Prozess zu gewährleisten, und frage mich nach der Versionsart, bevor du beginnst.

1. **Versionsart festlegen**:
   - Frage mich: „Welche Art von Version ist dies? Wähle eine der folgenden Optionen:
     - **Major** (z. B. 2.0.0): Für Breaking Changes oder große neue Features.
     - **Minor** (z. B. 1.1.0): Für neue Features ohne Breaking Changes.
     - **Patch** (z. B. 1.0.1): Für Bugfixes oder kleine Änderungen."
   - Basierend auf meiner Antwort, passe die Sorgfalt der folgenden Schritte an:
     - **Patch**: Minimale Dokumentation, keine umfassende Überprüfung von Abhängigkeiten oder Infrastruktur, fokussiere auf schnelles Deployment.
     - **Minor/Major**: Vollständige Überprüfung, umfassende Dokumentation und Tests.

2. **Infrastruktur-Check**:
   - **Für Minor/Major**:
     - Überprüfe die Python-Version (≥ 3.8) und pip-Version.
     - Stelle sicher, dass die virtuelle Umgebung korrekt eingerichtet ist.
     - Verifiziere, dass alle Dependencies in requirements.txt aktuell sind.
     - Überprüfe die PyInstaller-Version und NSIS-Installation.
     - Stelle sicher, dass Cloudflare-Storage Zugangsdaten konfiguriert sind.
   - **Für Patch**: Überspringe diesen Schritt, es sei denn, es gibt Hinweise auf Infrastrukturprobleme.

3. **Versionsupdate von veralteten Paketen**:
   - **Für Minor/Major**:
     - Führe `pip list --outdated` aus, um veraltete Pakete zu identifizieren.
     - Aktualisiere veraltete Pakete mit `pip install --upgrade package-name`. Prüfe bei größeren Versionssprüngen die Changelogs auf Breaking Changes.
     - Stelle sicher, dass alle Audio-Processing Libraries (numpy, scipy, soundfile, pyloudnorm) kompatibel sind.
     - Führe nach dem Update Tests aus (siehe Schritt 6), um Kompatibilität sicherzustellen.
     - Dokumentiere größere Versionsupdates im CHANGELOG.md (siehe Schritt 4).
   - **Für Patch**: Überspringe diesen Schritt, es sei denn, ein veraltetes Paket verursacht den Bug.

4. **Versionlog aktualisieren**:
   - **Für Minor/Major**:
     - Öffne die CHANGELOG.md-Datei (oder erstelle eine, falls sie fehlt).
     - Füge einen neuen Eintrag für die aktuelle Version hinzu (z. B. ## [x.y.z] - 2025-10-12).
     - Liste alle Änderungen, neuen Features, Bugfixes, aktualisierte Pakete oder Breaking Changes detailliert auf.
     - Stelle sicher, dass der Eintrag klar, prägnant und für andere Entwickler verständlich ist.
   - **Für Patch**:
     - Füge einen kurzen Eintrag im CHANGELOG.md hinzu, der nur den Bugfix oder die kleine Änderung beschreibt.

5. **Dokumentation aktualisieren**:
   - **Für Minor/Major**:
     - Überprüfe die README.md-Datei und andere Dokumentationsdateien.
     - Aktualisiere die Dokumentation, um neue Features, Konfigurationsänderungen, aktualisierte Abhängigkeiten oder wichtige Hinweise zu reflektieren.
     - Stelle sicher, dass Installations-, Einrichtungs- und Nutzungsanweisungen aktuell sind.
   - **Für Patch**: Überspringe diesen Schritt, es sei denn, der Bugfix erfordert eine kleine Dokumentationsänderung.

6. **Tests durchführen**:
   - **Für Minor/Major**:
     - Führe das Tool mit Test-Audio-Dateien aus, um die Funktionalität zu verifizieren.
     - Teste die Webserver-Funktionalität und A/B-Vergleichsfeatures.
     - Überprüfe die Audio-Qualität der Verarbeitung mit verschiedenen Dateiformaten.
     - Stelle sicher, dass alle Kernfunktionen (Batch-Processing, LUFS-Normalisierung, etc.) korrekt arbeiten.
   - **Für Patch**:
     - Führe nur Tests aus, die direkt mit dem Bugfix zusammenhängen.
     - Überspringe umfassende Tests, um Zeit zu sparen.

7. **Build-Prozess**:
   - **Für alle Versionen**:
     - Führe `python build_exe.py` aus, um die EXE mit PyInstaller zu erstellen.
     - Überprüfe die Build-Ausgabe auf Warnungen oder Fehler.
     - Teste die erstellte EXE lokal, um sicherzustellen, dass sie funktioniert.
     - Führe `makensis installer.nsi` aus, um den NSIS-Installer zu kompilieren.
     - Behebe alle Probleme während des Builds oder der Installation.
   - **Für Patch**: Halte die Überprüfung minimal, konzentriere dich nur auf kritische Build-Fehler.

8. **Versionsnummer aktualisieren**:
   - Basierend auf meiner Antwort in Schritt 1, aktualisiere die Versionsnummer in build_exe.py und installer.nsi:
     - Major: Erhöhe Major-Version (z. B. 1.0.0 → 2.0.0)
     - Minor: Erhöhe Minor-Version (z. B. 1.0.0 → 1.1.0)
     - Patch: Erhöhe Patch-Version (z. B. 1.0.0 → 1.0.1)

9. **Code einchecken**:
   - Führe `git add .` aus, um alle geänderten Dateien zu stagen.
   - Erstelle einen Commit mit einer klaren Nachricht:
     - **Für Minor/Major**: Beschreibe die Änderungen und die neue Versionsnummer detailliert.
     - **Für Patch**: Halte die Nachricht kurz.
   - Pushe die Änderungen in das Remote-Repository mit `git push origin main`.

10. **Deployment auf Cloudflare**:
    - Lade die EXE-Datei und den Installer in deinen Cloudflare Storage-Account hoch.
    - Aktualisiere die latest.json-Datei mit der neuen Version, Download-URLs und SHA256-Hashes.
    - Stelle sicher, dass die Dateien öffentlich zugänglich sind.
    - Teste die Download-URLs, um sicherzustellen, dass sie funktionieren.

11. **Testen des Deployments**:
    - **Für Minor/Major**:
      - Installiere das Tool auf verschiedenen Windows-Systemen.
      - Teste die Update-Funktionalität mit dem updater.py-Script.
      - Überprüfe die Audio-Qualität und Funktionalität auf verschiedenen Systemen.
      - Teste die Webserver-Funktionalität und A/B-Vergleichsfeatures.
    - **Für Patch**:
      - Führe nur Tests aus, die mit dem Bugfix zusammenhängen.
      - Überspringe umfassende Tests, um Zeit zu sparen.

12. **Abschluss**:
    - Überprüfe, ob alle Schritte erfolgreich abgeschlossen wurden.
    - Informiere mich über den Status des Deployments und die Ergebnisse der Tests.
    - Falls Fehler auftreten, gib eine kurze Beschreibung des Problems und schlage Lösungen vor.

**Frage**: Welche Art von Version ist dies? (Major, Minor, Patch)