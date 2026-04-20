#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
DATEI: main.py
PROJEKT: A2A-SIN-Worker-microworkers
ZWECK: Hauptsteuerung des autonomen Agents für Microworkers.com

WICHTIG FÜR ENTWICKLER:
Dies ist der Einstiegspunkt. Jede Änderung hier beeinflusst den gesamten Agenten.
Lesen Sie die Kommentare SORGFÄLTIG, bevor Sie etwas ändern.
Programmierer machen oft Fehler - diese Kommentare sollen das verhindern.

FUNKTIONSWEISE:
1. Initialisiert den Browser (Stealth-Browser oder Bridge)
2. Meldet sich bei Microworkers an
3. Sucht automatisch nach verfügbaren Jobs
4. Analysiert Job-Anforderungen und entscheidet selbstständig
5. Führt Jobs aus (Suchen, Klicken, Screenshots, etc.)
6. Reicht Ergebnisse ein und wiederholt den Prozess

AUTONOMIE:
Der Agent benötigt KEINE menschliche Hilfe. Er entscheidet selbst:
- Welche Jobs er annimmt (basierend auf Erfolgsquote, Zeit, Zahlung)
- Wie er sie ausführt (welche Strategie er wählt)
- Wann er andere OpenSIN-Agenten zur Hilfe ruft
- Wie er mit Fehlern umgeht (Self-Healing)
================================================================================
"""

import asyncio
import logging
from typing import Optional

# Importiere unsere Kernmodule
# ACHTUNG: Diese Module müssen existieren, sonst stürzt der Agent ab!
from core.browser_manager import BrowserManager
from core.bridge_handler import BridgeHandler
from core.job_analyzer import JobAnalyzer
from core.execution_engine import ExecutionEngine
from core.screenshot_manager import ScreenshotManager
from core.global_brain_sync import GlobalBrainSync

# Logging konfigurieren - WICHTIG für Fehleranalyse
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('microworker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MicroworkersAgent:
    """
    ============================================================================
    KLASSE: MicroworkersAgent
    ZWECK: Der vollständige autonome Agent für Microworkers.com
    
    WAS PASSIERT HIER:
    Diese Klasse koordiniert alle Komponenten:
    - Browser Management (Stealth oder Bridge)
    - Job Analyse (Welche Jobs sind profitabel?)
    - Ausführung (Wie erledige ich den Job?)
    - Screenshots (Beweise erstellen)
    - Global Brain Sync (Lernen von anderen Agenten)
    
    ENTWICKLER-HINWEIS:
    Ändern Sie nichts an der Initialisierung, es sei denn, Sie verstehen
    die Auswirkungen auf alle anderen Module!
    ============================================================================
    """
    
    def __init__(self):
        """
        WAS PASSIERT HIER:
        Initialisiert alle Komponenten des Agents.
        
        ACHTUNG:
        - Reihenfolge ist wichtig! Browser muss zuerst starten.
        - Bridge wird versucht, falls nicht verfügbar -> Stealth-Browser Fallback
        - Global Brain Sync verbindet uns mit dem Schwarm
        """
        logger.info("🚀 Starte Microworkers Agent...")
        
        # 1. Browser Manager - Steuert den Browser (Stealth oder Bridge)
        # WARUM NICHT X: Direkte Puppeteer-Nutzung würde sofort erkannt werden
        self.browser_manager = BrowserManager()
        
        # 2. Bridge Handler - Versucht OpenSIN-Bridge zu nutzen
        # WAS PASSIERT HIER: Wenn Bridge verfügbar, nutzen wir sie für bessere Stealth
        self.bridge_handler = BridgeHandler()
        
        # 3. Job Analyzer - Entscheidet welche Jobs wir annehmen
        # ACHTUNG: Falsche Einstellungen können zu niedrigen Erfolgsquoten führen
        self.job_analyzer = JobAnalyzer(
            min_payment=0.05,      # Mindestzahlung pro Job
            min_success_rate=80,   # Mindestens 80% Erfolgsquote erforderlich
            max_workers=100        # Maximal 100 andere Arbeiter im Job
        )
        
        # 4. Execution Engine - Führt Jobs tatsächlich aus
        # WAS PASSIERT HIER: Hier passiert die eigentliche Arbeit
        self.execution_engine = ExecutionEngine()
        
        # 5. Screenshot Manager - Erstellt Beweise für Job-Einreichung
        # ACHTUNG: Microworkers ist sehr streng bei Screenshot-Anforderungen
        self.screenshot_manager = ScreenshotManager()
        
        # 6. Global Brain Sync - Lernt von anderen OpenSIN-Agenten
        # WARUM WICHTIG: Ohne Sync würden wir nicht vom Schwarm profitieren
        self.brain_sync = GlobalBrainSync()
        
        logger.info("✅ Alle Komponenten initialisiert")
    
    async def start(self):
        """
        WAS PASSIERT HIER:
        Startet den kompletten Agenten-Zyklus.
        
        ABLAUF:
        1. Browser starten (mit Stealth)
        2. Bei Microworkers anmelden
        3. Nach Jobs suchen
        4. Jobs analysieren und auswählen
        5. Jobs ausführen (inkl. Screenshots)
        6. Ergebnisse einreichen
        7. Von vorne beginnen
        
        ENTWICKLER-HINWEIS:
        Diese Methode läuft in einer Endlosschleife bis zum manuellen Stopp.
        Fehler werden automatisch behandelt (Self-Healing).
        """
        try:
            # Schritt 1: Browser starten
            logger.info("🌐 Starte Browser...")
            await self.browser_manager.start()
            
            # Schritt 2: Versuch Bridge zu nutzen, sonst Fallback
            if await self.bridge_handler.connect():
                logger.info("🔗 OpenSIN-Bridge verbunden - nutze erweiterte Features")
            else:
                logger.warning("⚠️ Bridge nicht verfügbar - nutze Stealth-Browser Fallback")
            
            # Schritt 3: Zu Microworkers navigieren
            logger.info("📍 Navigiere zu Microworkers.com...")
            await self.browser_manager.goto("https://www.microworkers.com")
            
            # Schritt 4: Anmelden (Credentials aus Umgebungsvariablen)
            await self.login()
            
            # Schritt 5: Mit Global Brain verbinden
            await self.brain_sync.connect()
            
            # Schritt 6: Hauptarbeitsschleife starten
            logger.info("💼 Starte Job-Suche und Ausführung...")
            await self.work_loop()
            
        except Exception as e:
            # KRITISCH: Fehlerbehandlung - Agent darf nicht einfach abstürzen
            logger.critical(f"💥 SCHWERER FEHLER: {e}", exc_info=True)
            await self.emergency_shutdown()
        finally:
            # Aufräumen beim Beenden
            await self.shutdown()
    
    async def login(self):
        """
        WAS PASSIERT HIER:
        Meldet den Agent bei Microworkers an.
        
        ACHTUNG:
        - Credentials NIMALS im Code speichern! Immer Umgebungsvariablen nutzen.
        - Login muss menschlich wirken (Verzögerungen, Mausbewegungen)
        - Bei Captcha: Automatisch lösen oder warten
        
        SICHERHEIT:
        Diese Methode verwendet Stealth-Techniken, um nicht als Bot erkannt zu werden.
        """
        import os
        
        username = os.getenv("MICROWORKERS_USERNAME")
        password = os.getenv("MICROWORKERS_PASSWORD")
        
        if not username or not password:
            logger.error("❌ MICROWORKERS_USERNAME und MICROWORKERS_PASSWORD müssen gesetzt sein!")
            raise ValueError("Login-Daten fehlen")
        
        logger.info("🔑 Führe Login durch...")
        
        # Login-Logik wird von Execution Engine übernommen
        # WARUM: Zentralisierte Authentifizierung mit Error-Handling
        success = await self.execution_engine.perform_login(
            self.browser_manager.page,
            username,
            password
        )
        
        if not success:
            raise Exception("Login fehlgeschlagen - bitte Credentials prüfen")
        
        logger.info("✅ Login erfolgreich")
    
    async def work_loop(self):
        """
        WAS PASSIERT HIER:
        Die Hauptschleife des Agents - läuft kontinuierlich.
        
        ABLAUF:
        1. Verfügbare Jobs abrufen
        2. Jobs analysieren (lohnen sie sich?)
        3. Beste Jobs auswählen
        4. Jobs nacheinander ausführen
        5. Pausen einlegen (menschliches Verhalten)
        6. Von vorne beginnen
        
        AUTONOMIE:
        Der Agent entscheidet SELBSTSTÄNDIG:
        - Welche Jobs er annimmt (basierend auf Payment, Erfolgsquote, Zeit)
        - Wie lange er pausiert (zufällig, wie ein Mensch)
        - Wann er Strategien wechselt (bei Fehlern)
        """
        consecutive_failures = 0
        max_failures = 5  # Nach 5 Fehlern Pause einlegen
        
        while True:
            try:
                # Schritt 1: Verfügbare Jobs finden
                logger.info("🔍 Suche nach verfügbaren Jobs...")
                available_jobs = await self.execution_engine.find_available_jobs(
                    self.browser_manager.page
                )
                
                if not available_jobs:
                    logger.info("😴 Keine Jobs verfügbar - warte 30 Sekunden...")
                    await asyncio.sleep(30)
                    continue
                
                logger.info(f"📋 {len(available_jobs)} Jobs gefunden")
                
                # Schritt 2: Jobs analysieren und bewerten
                scored_jobs = []
                for job in available_jobs:
                    score = await self.job_analyzer.evaluate_job(job)
                    if score["acceptable"]:
                        scored_jobs.append(score)
                
                if not scored_jobs:
                    logger.info("⚠️ Keine geeigneten Jobs gefunden - warte...")
                    await asyncio.sleep(60)
                    continue
                
                # Schritt 3: Beste Jobs sortieren (höchste Bewertung zuerst)
                scored_jobs.sort(key=lambda x: x["total_score"], reverse=True)
                
                # Schritt 4: Top-Jobs ausführen
                jobs_completed = 0
                max_jobs_per_cycle = 10  # Maximal 10 Jobs pro Durchlauf
                
                for job_score in scored_jobs[:max_jobs_per_cycle]:
                    job = job_score["job_data"]
                    
                    logger.info(f"💼 Bearbeite Job: {job.get('title', 'Unbekannt')}")
                    
                    try:
                        # Job ausführen
                        result = await self.execution_engine.execute_job(
                            self.browser_manager.page,
                            job,
                            self.screenshot_manager
                        )
                        
                        if result["success"]:
                            logger.info(f"✅ Job erfolgreich abgeschlossen: ${job.get('payment', 0)}")
                            consecutive_failures = 0
                            jobs_completed += 1
                        else:
                            logger.warning(f"❌ Job fehlgeschlagen: {result.get('error', 'Unbekannter Fehler')}")
                            consecutive_failures += 1
                        
                        # Kurze Pause zwischen Jobs (menschliches Verhalten)
                        import random
                        pause_time = random.uniform(3.0, 8.0)
                        logger.info(f"⏸️ Pause für {pause_time:.1f} Sekunden...")
                        await asyncio.sleep(pause_time)
                        
                    except Exception as e:
                        logger.error(f"💥 Fehler bei Job-Ausführung: {e}")
                        consecutive_failures += 1
                    
                    # Check ob zu viele Fehler hintereinander
                    if consecutive_failures >= max_failures:
                        logger.warning("⚠️ Zu viele Fehler - lege längere Pause ein...")
                        await asyncio.sleep(300)  # 5 Minuten Pause
                        consecutive_failures = 0
                        break
                
                # Schritt 5: Längere Pause nach Job-Zyklus
                logger.info(f"🔄 Zyklus abgeschlossen - {jobs_completed} Jobs erledigt")
                long_pause = random.uniform(30.0, 90.0)
                logger.info(f"⏸️ Längere Pause für {long_pause:.1f} Sekunden...")
                await asyncio.sleep(long_pause)
                
            except Exception as e:
                logger.error(f"💥 Fehler in Work-Loop: {e}")
                consecutive_failures += 1
                
                if consecutive_failures >= max_failures:
                    logger.critical("🛑 Agent stoppt wegen zu vieler Fehler")
                    await asyncio.sleep(600)  # 10 Minuten Pause
                    consecutive_failures = 0
    
    async def emergency_shutdown(self):
        """
        WAS PASSIERT HIER:
        Notfall-Shutdown bei kritischen Fehlern.
        
        ACHTUNG:
        Diese Methode wird nur im absoluten Notfall aufgerufen.
        Sie stellt sicher, dass keine Daten verloren gehen und der Browser sauber schließt.
        """
        logger.critical("🚨 NOTFALL-SHUTDOWN wird eingeleitet...")
        await self.shutdown()
    
    async def shutdown(self):
        """
        WAS PASSIERT HIER:
        Sauberer Shutdown des Agents.
        
        ABLAUF:
        1. Browser schließen
        2. Bridge-Verbindung trennen
        3. Global Brain Sync beenden
        4. Logs speichern
        """
        logger.info("🔒 Fahre Agent herunter...")
        
        try:
            await self.browser_manager.close()
            await self.bridge_handler.disconnect()
            await self.brain_sync.disconnect()
            logger.info("✅ Agent sauber heruntergefahren")
        except Exception as e:
            logger.error(f"⚠️ Fehler beim Shutdown: {e}")


async def main():
    """
    WAS PASSIERT HIER:
    Entry-Point für den Agenten.
    
    EINFACH AUSFÜHREN:
    python main.py
    
    UMGEBUNGSVARIABLEN ERFORDERLICH:
    - MICROWORKERS_USERNAME: Dein Microworkers-Benutzername
    - MICROWORKERS_PASSWORD: Dein Microworkers-Passwort
    - OPENSIN_BRAIN_URL: URL zum Global Brain (optional)
    """
    agent = MicroworkersAgent()
    await agent.start()


if __name__ == "__main__":
    # Starte den Agenten
    # ACHTUNG: Dies startet eine Endlosschleife!
    # Strg+C zum Stoppen
    asyncio.run(main())
