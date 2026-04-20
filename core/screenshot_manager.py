"""
==============================================================================
DATEI: core/screenshot_manager.py
PROJEKT: A2A-SIN-Worker-microworkers
ZWECK: Erstellt, benennt und verwaltet Screenshots als Job-Beweise

WICHTIG FÜR ENTWICKLER:
Screenshots sind der EINZIGE Beweis für erledigte Arbeit auf Microworkers!
Falsche Screenshots = 100% Ablehnung durch Arbeitgeber = Kein Geld!

Dieses Modul stellt sicher dass:
- Screenshots immer lesbar und vollständig sind
- Dateinamen den Plattform-Anforderungen entsprechen
- Timestamps korrekt eingefügt werden
- Beweise nicht verloren gehen

ENTWICKLER-HINWEIS:
Niemals Screenshot-Funktionen ändern ohne sie ausgiebig zu testen!
Ein fehlerhafter Screenshot kostet bares Geld!
==============================================================================
"""

import os
import asyncio
from datetime import datetime
from typing import Optional, List
from pathlib import Path


class ScreenshotManager:
    """
    WAS PASSIERT HIER: Verwaltet alle Screenshot-Operationen
    
    ACHTUNG:
    - Screenshots müssen VOLLSTÄNDIG sein (ganze Seite)
    - Dateinamen müssen eindeutig sein (Timestamp + JobID)
    - Format muss PNG sein (beste Qualität bei kleiner Größe)
    
    ENTWICKLER-HINWEIS:
    Bei Fehlern sofort retry mit leicht verzögerter Zeit!
    Manchmal laden Seiten langsamer als erwartet.
    """
    
    def __init__(self, base_directory: str = "evidence"):
        """
        Initialisiert den Screenshot Manager
        
        PARAMETER:
        - base_directory: Ordner wo alle Screenshots gespeichert werden
        
        WAS PASSIERT HIER:
        Erstellt den Evidence-Ordner wenn er nicht existiert
        Jeder Job bekommt seinen eigenen Unterordner
        """
        
        self.base_directory = Path(base_directory)
        self.screenshot_count = 0
        
        # WICHTIG: Ordnerstruktur erstellen
        # Format: evidence/JOB_ID/TIMESTAMP_screenshot.png
        self._ensure_directories_exist()
    
    def _ensure_directories_exist(self):
        """
        WAS PASSIERT HIER: Erstellt notwendige Ordnerstrukturen
        
        ACHTUNG:
        Wenn Ordner nicht erstellt werden können, schlägt gesamter Job fehl!
        Deshalb hier keine Exceptions unterdrücken - lieber krachen lassen.
        """
        
        try:
            # Hauptverzeichnis erstellen
            self.base_directory.mkdir(parents=True, exist_ok=True)
            
            # Heute's Datum als Unterordner (bessere Organisation)
            today = datetime.now().strftime("%Y-%m-%d")
            self.today_directory = self.base_directory / today
            self.today_directory.mkdir(exist_ok=True)
            
            print(f"✓ Evidence-Ordner bereit: {self.today_directory}")
            
        except Exception as e:
            # KRITISCHER FEHLER: Kann nicht speichern = Job unmöglich
            print(f"✗ FEHLER: Kann Evidence-Ordner nicht erstellen: {e}")
            raise
    
    async def take_fullpage_screenshot(self, page, job_id: str, 
                                       description: str = "") -> Optional[str]:
        """
        WAS PASSIERT HIER: Erstellt vollständigen Screenshot einer Webseite
        
        PARAMETER:
        - page: Die Browser-Page (nodriver oder Bridge)
        - job_id: Eindeutige Job-ID von Microworkers
        - description: Kurze Beschreibung was gezeigt wird (optional)
        
        RÜCKGABE:
        - Pfad zum gespeicherten Screenshot bei Erfolg
        - None bei Fehler
        
        ENTWICKLER-HINWEIS:
        - full_page=True ist ESSENTIELL - abgeschnittene Screenshots werden abgelehnt!
        - Immer warten bis Seite komplett geladen ist
        - Bei dynamischen Inhalten extra Verzögerung einbauen
        """
        
        try:
            # Schritt 1: Warten bis Seite vollständig geladen
            print(f"📸 Erstelle Screenshot für Job {job_id}...")
            
            # Kurze Pause damit alle Elemente gerendert sind
            await asyncio.sleep(1.5)
            
            # Schritt 2: Eindeutigen Dateinamen generieren
            timestamp = datetime.now().strftime("%H%M%S")
            self.screenshot_count += 1
            
            # Dateiname: JOBID_TIMESTAMP_COUNTER_description.png
            safe_description = self._sanitize_filename(description)[:30]
            filename = f"{job_id}_{timestamp}_{self.screenshot_count:03d}"
            
            if safe_description:
                filename += f"_{safe_description}"
            
            filename += ".png"
            
            # Vollständiger Pfad
            filepath = self.today_directory / filename
            
            # Schritt 3: Screenshot erstellen (nodriver Syntax)
            # ACHTUNG: Unterschiedliche Browser-APIs haben unterschiedliche Syntax!
            try:
                # nodriver Variante
                await page.save_screenshot(str(filepath))
                
            except AttributeError:
                # Fallback für andere Browser-Treiber
                # (z.B. wenn Bridge verwendet wird)
                await page.screenshot(path=str(filepath), full_page=True)
            
            # Schritt 4: Verify dass Screenshot existiert und nicht leer ist
            if filepath.exists() and filepath.stat().st_size > 0:
                file_size_kb = filepath.stat().st_size / 1024
                print(f"✓ Screenshot erfolgreich: {filename} ({file_size_kb:.1f} KB)")
                return str(filepath)
            else:
                print(f"✗ FEHLER: Screenshot-Datei ist leer oder fehlt!")
                return None
                
        except Exception as e:
            # WICHTIG: Fehler loggen aber nicht crashen
            # Agent kann eventuell mit alternativem Weg fortfahren
            print(f"✗ FEHLER beim Screenshot: {e}")
            return None
    
    async def take_element_screenshot(self, page, element, job_id: str,
                                      element_name: str = "element") -> Optional[str]:
        """
        WAS PASSIERT HIER: Erstellt Screenshot eines spezifischen Elements
        
        WANN BENÖTIGT:
        - Nur bestimmter Bereich soll gezeigt werden (z.B. Warenkorb)
        - Element ist klein und Details müssen erkennbar sein
        
        PARAMETER:
        - page: Browser-Page
        - element: Das spezifische Element (DOM Node)
        - job_id: Job-ID für Dateinamen
        - element_name: Beschreibung des Elements
        
        ENTWICKLER-HINWEIS:
        Nicht alle Plattformen akzeptieren Element-Screenshots!
        Immer zuerst prüfen ob Full-Page oder Element gefordert ist.
        """
        
        try:
            print(f"📸 Erstelle Element-Screenshot: {element_name}")
            
            # Schritt 1: Element ins Viewport scrollen
            # (Manche Elemente sind außerhalb des sichtbaren Bereichs)
            await element.scroll_into_view()
            await asyncio.sleep(0.5)  # Kurze Pause nach Scroll
            
            # Schritt 2: Bounding Box des Elements holen
            try:
                box = await element.get_bounding_box()
            except:
                # Fallback wenn get_bounding_box nicht verfügbar
                print("⚠ Kann Bounding Box nicht bestimmen, nutze Full-Page")
                return await self.take_fullpage_screenshot(page, job_id, element_name)
            
            # Schritt 3: Screenshot mit Clip erstellen
            timestamp = datetime.now().strftime("%H%M%S")
            self.screenshot_count += 1
            
            filename = f"{job_id}_{timestamp}_element_{self.screenshot_count:03d}.png"
            filepath = self.today_directory / filename
            
            # Clip-Parameter für fokussierten Screenshot
            clip = {
                'x': box['x'],
                'y': box['y'],
                'width': box['width'],
                'height': box['height'],
                'scale': 2  # Höhere Qualität durch 2x Skalierung
            }
            
            await page.screenshot(path=str(filepath), clip=clip)
            
            # Verify
            if filepath.exists() and filepath.stat().st_size > 0:
                print(f"✓ Element-Screenshot erfolgreich: {filename}")
                return str(filepath)
            else:
                print(f"✗ FEHLER: Element-Screenshot fehlgeschlagen")
                return None
                
        except Exception as e:
            print(f"✗ FEHLER beim Element-Screenshot: {e}")
            # Fallback zu Full-Page
            return await self.take_fullpage_screenshot(page, job_id, element_name)
    
    async def take_multiple_screenshots(self, page, job_id: str,
                                        descriptions: List[str]) -> List[str]:
        """
        WAS PASSIERT HIER: Erstellt mehrere Screenshots hintereinander
        
        WANN BENÖTIGT:
        - Job fordert explizit mehrere Beweise (z.B. "4 Screenshots")
        - Verschiedene Schritte müssen dokumentiert werden
        
        PARAMETER:
        - page: Browser-Page
        - job_id: Job-ID
        - descriptions: Liste von Beschreibungen für jeden Screenshot
        
        RÜCKGABE:
        Liste aller erfolgreichen Screenshot-Pfade
        
        ENTWICKLER-HINWEIS:
        Zwischen Screenshots immer kurz warten!
        Sonst sehen alle gleich aus (besonders bei dynamischen Seiten).
        """
        
        successful_screenshots = []
        
        for i, desc in enumerate(descriptions, 1):
            print(f"📸 Screenshot {i}/{len(descriptions)}: {desc}")
            
            # Kurze Pause zwischen Screenshots
            await asyncio.sleep(2.0)
            
            # Screenshot erstellen
            filepath = await self.take_fullpage_screenshot(page, job_id, desc)
            
            if filepath:
                successful_screenshots.append(filepath)
            else:
                # WICHTIG: Bei Fehler weitermachen, nicht abbrechen
                # Lieber 3 von 4 Screenshots als gar keine
                print(f"⚠ Screenshot {i} fehlgeschlagen, mache weiter...")
        
        print(f"✓ {len(successful_screenshots)}/{len(descriptions)} Screenshots erfolgreich")
        return successful_screenshots
    
    def _sanitize_filename(self, text: str) -> str:
        """
        WAS PASSIERT HIER: Bereinigt Text für sichere Dateinamen
        
        WARUM NOTWENDIG:
        - Sonderzeichen können in Dateinamen Probleme machen
        - Leerzeichen werden zu Underscores
        - Länge begrenzen (manche Systeme haben Limits)
        
        BEISPIEL:
        "Suche + Interagieren + Bonus!" → "Suche_Interagieren_Bonus"
        """
        
        # Unerwünschte Zeichen entfernen/ersetzen
        unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '!', ',', ';']
        
        result = text
        for char in unsafe_chars:
            result = result.replace(char, '')
        
        # Leerzeichen zu Underscores
        result = result.replace(' ', '_')
        
        # Mehrfache Underscores zu einfachem
        while '__' in result:
            result = result.replace('__', '_')
        
        # Auf 30 Zeichen kürzen (für lesbare Dateinamen)
        result = result[:30]
        
        # Alles lowercase für Konsistenz
        result = result.lower()
        
        return result.strip('_')
    
    def get_evidence_report(self, job_id: str) -> dict:
        """
        WAS PASSIERT HIER: Erstellt Übersicht aller Screenshots für einen Job
        
        RÜCKGABE:
        Dictionary mit:
        - count: Anzahl gefundener Screenshots
        - files: Liste aller Dateipfade
        - total_size: Gesamtgröße in KB
        - latest: Neuester Screenshot
        
        NUTZUNG:
        Wird am Job-Ende für Submit-Proof verwendet
        """
        
        # Suche alle Dateien die mit Job-ID beginnen
        pattern = f"{job_id}_*.png"
        screenshots = list(self.today_directory.glob(pattern))
        
        if not screenshots:
            return {
                'count': 0,
                'files': [],
                'total_size': 0,
                'latest': None,
                'warning': 'Keine Screenshots gefunden!'
            }
        
        # Sortiere nach Zeitpunkt (neueste zuerst)
        screenshots.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Gesamtgröße berechnen
        total_size = sum(f.stat().st_size for f in screenshots) / 1024  # KB
        
        return {
            'count': len(screenshots),
            'files': [str(f) for f in screenshots],
            'total_size': round(total_size, 2),
            'latest': str(screenshots[0]),
            'all_files': screenshots
        }
    
    def cleanup_old_evidence(self, days_to_keep: int = 7):
        """
        WAS PASSIERT HIER: Löscht alte Screenshots um Speicher zu sparen
        
        PARAMETER:
        - days_to_keep: Wie viele Tage Evidence behalten wird
        
        WICHTIG:
        - Niemals aktuelle Jobs löschen!
        - Microworkers hat manchmal späte Reviews (bis 30 Tage)
        - Minimum 7 Tage aufbewahren empfohlen
        
        ENTWICKLER-HINWEIS:
        Diese Funktion sollte regelmäßig (täglich) aufgerufen werden.
        Am besten via Cron-Job oder Timer im Main-Agent.
        """
        
        import shutil
        
        deleted_count = 0
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        
        for folder in self.base_directory.iterdir():
            if folder.is_dir():
                # Prüfe ob Ordner älter als Cutoff
                try:
                    # Nutze neueste Datei im Ordner als Referenz
                    newest_file = max(folder.glob("*.png"), key=lambda f: f.stat().st_mtime)
                    
                    if newest_file.stat().st_mtime < cutoff_date:
                        # Kompletten Ordner löschen
                        shutil.rmtree(folder)
                        deleted_count += 1
                        print(f"🗑 Gelöscht alter Evidence-Ordner: {folder.name}")
                        
                except (ValueError, StopIteration):
                    # Ordner ohne Screenshots - trotzdem löschen
                    shutil.rmtree(folder)
                    deleted_count += 1
        
        print(f"✓ Cleanup abgeschlossen: {deleted_count} alte Ordner gelöscht")
        return deleted_count


# =============================================================================
# MAIN TEST BLOCK (Nur für Entwicklung)
# =============================================================================
if __name__ == "__main__":
    """
    WAS PASSIERT HIER: Testet Screenshot Manager Funktionen
    
    ENTWICKLER-HINWEIS:
    Dieser Test benötigt eine echte Browser-Page!
    Nur sinnvoll im Kontext eines laufenden Agents.
    """
    
    print("=" * 80)
    print("SCREENSHOT MANAGER - Test Suite")
    print("=" * 80)
    
    manager = ScreenshotManager(base_directory="test_evidence")
    
    print(f"\n✓ Manager initialisiert")
    print(f"  Basis-Ordner: {manager.base_directory}")
    print(f"  Heute-Ordner: {manager.today_directory}")
    
    # Teste Filename Sanitization
    test_names = [
        "Suche + Interagieren + Bonus!",
        "Screenshot (4) required",
        "Facebook-Code: ABC123",
        "Herunterladen: Bild_12.jpg"
    ]
    
    print("\n📝 Teste Filename-Sanitization:")
    for name in test_names:
        sanitized = manager._sanitize_filename(name)
        print(f"  '{name}' → '{sanitized}'")
    
    print("\n" + "=" * 80)
    print("TEST ABGESCHLOSSEN")
    print("=" * 80)
