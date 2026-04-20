"""
================================================================================
DATEI: vote_review_solver.py
PROJEKT: A2A-SIN-Worker-microworkers
ZWECK: Löst "Vote & Review" Aufgaben auf Microworkers.com
       (Suchen -> Webseite finden -> Abstimmen -> Bewertung schreiben)

WICHTIG FÜR ENTWICKLER:
Dieses Modul simuliert menschliches Abstimmungs- und Bewertungsverhalten.
Falsche Implementierung führt zu sofortiger Ablehnung der Arbeit!
Lesen Sie JEDEN Kommentar, bevor Sie Änderungen vornehmen.

AUTOR: OpenSIN AI Team
LIZENZ: Proprietary (OpenSIN Konzern)
================================================================================
"""

import asyncio
import random
from typing import Optional, Dict, Any
from ..core.browser_manager import BrowserManager
from ..core.screenshot_manager import ScreenshotManager

class VoteReviewSolver:
    """
    WAS PASSIERT HIER: 
    Spezialisiertes Modul zum Lösen von Vote & Review Tasks.
    
    WARUM NICHT X: 
    Einfaches Klicken reicht nicht - Plattformen prüfen Verweildauer,
    Mausbewegungen während des Lesens und Textqualität der Bewertung.
    
    ANWENDUNG:
    solver = VoteReviewSolver(browser_manager, screenshot_manager)
    await solver.solve(job_details)
    """
    
    def __init__(self, browser_manager: BrowserManager, screenshot_manager: ScreenshotManager):
        """
        WAS PASSIERT HIER:
        Initialisiert den Solver mit notwendigen Komponenten.
        
        PARAMETER:
        - browser_manager: Steuert den Stealth-Browser
        - screenshot_manager: Erstellt Beweisscreenshots
        
        ENTWICKLER-HINWEIS:
        Niemals None-Werte hier zulassen! Sonst crasht alles später.
        """
        self.browser_manager = browser_manager
        self.screenshot_manager = screenshot_manager
        self.min_review_length = 50  # Mindestzeichen pro Bewertung
        self.max_review_length = 300  # Maximalzeichen pro Bewertung
        
    async def solve(self, job_details: Dict[str, Any]) -> bool:
        """
        WAS PASSIERT HIER:
        Hauptmethode zur Lösung einer Vote & Review Aufgabe.
        
        ABLAUF:
        1. Suchbegriff aus Job-Details extrahieren
        2. Zielwebseite über Suchmaschine finden
        3. Auf Seite navigieren und verweilen (menschlich)
        4. Voting-Element finden und klicken
        5. Bewertungstext generieren und eingeben
        6. Absenden und Screenshots erstellen
        
        PARAMETER:
        - job_details: Dictionary mit Keywords, Voting-Typ, etc.
        
        RÜCKGABEWERT:
        - True bei Erfolg, False bei Misserfolg
        
        ACHTUNG:
        Bei False MUSS der Caller einen Retry-Versuch starten!
        """
        try:
            print(f"[VoteReview] Starte Lösung für Job: {job_details.get('title', 'Unbekannt')}")
            
            # Schritt 1: Keyword extrahieren
            keyword = job_details.get('keyword') or job_details.get('search_term')
            if not keyword:
                print("[VoteReview] FEHLER: Kein Keyword gefunden!")
                return False
            
            # Schritt 2: Suche durchführen
            print(f"[VoteReview] Suche nach: {keyword}")
            search_success = await self._perform_search(keyword)
            if not search_success:
                return False
            
            # Schritt 3: Voting durchführen
            voting_success = await self._perform_voting()
            if not voting_success:
                return False
            
            # Schritt 4: Bewertung schreiben
            review_success = await self._write_review(job_details)
            if not review_success:
                return False
            
            # Schritt 5: Beweise sichern
            await self.screenshot_manager.capture_final_evidence(
                task_type="vote_review",
                status="completed"
            )
            
            print("[VoteReview] ✅ Aufgabe erfolgreich abgeschlossen!")
            return True
            
        except Exception as e:
            print(f"[VoteReview] ❌ KRITISCHER FEHLER: {str(e)}")
            await self.screenshot_manager.capture_error_screenshot(error=str(e))
            return False
    
    async def _perform_search(self, keyword: str) -> bool:
        """
        WAS PASSIERT HIER:
        Führt eine natürliche Suchmaschinenanfrage durch.
        
        WARUM KOMPLEX:
        Direktes Aufrufen der URL wird erkannt. Echte Nutzer suchen!
        
        ACHTUNG:
        - Verweildauer auf Suchergebnisseite: 3-8 Sekunden
        - Menschliche Mausbewegung zum Klick erforderlich
        """
        try:
            page = await self.browser_manager.get_current_page()
            
            # Google-Suche (oder Bing je nach Job-Anforderung)
            search_url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}"
            await page.goto(search_url)
            
            # Menschliche Verweildauer simulieren
            await asyncio.sleep(random.uniform(3.0, 8.0))
            
            # Erstes organisches Ergebnis finden und klicken
            # ACHTUNG: Selector kann sich ändern! Immer testen!
            first_result = await page.select_first('div.g a[href^="http"]')
            if not first_result:
                print("[VoteReview] Kein Suchergebnis gefunden!")
                return False
            
            await first_result.click()
            await asyncio.sleep(random.uniform(2.0, 5.0))  # Warten auf Seitenload
            
            print("[VoteReview] Suche erfolgreich durchgeführt")
            return True
            
        except Exception as e:
            print(f"[VoteReview] Suchfehler: {str(e)}")
            return False
    
    async def _perform_voting(self) -> bool:
        """
        WAS PASSIERT HIER:
        Findet und klickt das Voting-Element (Sterne, Daumen, etc.)
        
        ENTWICKLER-HINWEIS:
        Voting-Elemente haben unterschiedliche Selektoren je nach Plattform!
        Diese Liste muss ständig aktualisiert werden.
        """
        try:
            page = await self.browser_manager.get_current_page()
            
            # Liste möglicher Voting-Selektoren (priorisiert)
            voting_selectors = [
                'input[type="radio"][name*="rating"]',  # Radio Buttons
                '.star-rating a',  # Sterne-Links
                '[aria-label*="rate"]',  # ARIA Labels
                '.vote-button',  # Generische Klasse
                'button[class*="vote"]',  # Vote Buttons
                '[data-action*="vote"]',  # Data-Attribute
            ]
            
            for selector in voting_selectors:
                try:
                    voting_element = await page.select_first(selector)
                    if voting_element:
                        # Menschliche Verzögerung vor dem Klick
                        await asyncio.sleep(random.uniform(1.5, 3.5))
                        
                        # Element ins Viewport scrollen
                        await voting_element.scroll_into_view()
                        await asyncio.sleep(random.uniform(0.5, 1.5))
                        
                        # Klicken mit human_mouse aus Bridge/Stealth
                        await self.browser_manager.human_click_element(voting_element)
                        
                        print(f"[VoteReview] Voting erfolgreich mit Selector: {selector}")
                        return True
                        
                except Exception:
                    continue  # Nächsten Selector versuchen
            
            print("[VoteReview] KEIN Voting-Element gefunden!")
            return False
            
        except Exception as e:
            print(f"[VoteReview] Voting-Fehler: {str(e)}")
            return False
    
    async def _write_review(self, job_details: Dict[str, Any]) -> bool:
        """
        WAS PASSIERT HIER:
        Generiert und submittert eine menschenähnliche Bewertung.
        
        WARUM NICHT X:
        Copy-Paste Texte werden erkannt! Jeder Text muss unikate sein.
        
        ACHTUNG:
        - Tippgeschwindigkeit variieren (menschlich)
        - Keine perfekten Sätze (Menschen machen kleine Fehler)
        - Länge an Job-Anforderungen anpassen
        """
        try:
            page = await self.browser_manager.get_current_page()
            
            # Textarea finden (verschiedene Selektoren)
            textarea_selectors = [
                'textarea[name*="review"]',
                'textarea[placeholder*="review"]',
                'textarea[class*="comment"]',
                '#review-text',
                '.review-textarea',
            ]
            
            textarea = None
            for selector in textarea_selectors:
                textarea = await page.select_first(selector)
                if textarea:
                    break
            
            if not textarea:
                print("[VoteReview] Kein Textfeld für Bewertung gefunden!")
                return False
            
            # Bewertungstext generieren
            review_text = self._generate_human_review(job_details)
            
            # Ins Viewport scrollen
            await textarea.scroll_into_view()
            await asyncio.sleep(random.uniform(1.0, 2.0))
            
            # Text eingeben (menschliche Tippgeschwindigkeit)
            await self.browser_manager.human_type(textarea, review_text)
            
            # Submit Button finden und klicken
            submit_success = await self._submit_review()
            return submit_success
            
        except Exception as e:
            print(f"[VoteReview] Review-Fehler: {str(e)}")
            return False
    
    def _generate_human_review(self, job_details: Dict[str, Any]) -> str:
        """
        WAS PASSIERT HIER:
        Generiert einen einzigartigen, menschenähnlichen Bewertungstext.
        
        STRATEGIE:
        - Verwende Keywords aus dem Job
        - Baue zufällige Phrasen ein
        - Variiere Satzlängen
        - Füge persönliche Note hinzu
        
        ENTWICKLER-HINWEIS:
        Diese Methode sollte zukünftig durch KI-Textgenerierung ersetzt werden!
        """
        templates_positive = [
            "Tolle Erfahrung! {keyword} hat meine Erwartungen übertroffen.",
            "Sehr zufrieden mit {keyword}. Kann ich nur empfehlen!",
            "{keyword} funktioniert einwandfrei. Gerne wieder.",
            "Bin begeistert von {keyword}. Alles bestens gelaufen.",
            "Super Service bei {keyword}. Sehr empfehlenswert!",
        ]
        
        templates_neutral = [
            "{keyword} ist okay. Nichts Besonderes, aber erfüllt den Zweck.",
            "Durchschnittliche Erfahrung mit {keyword}. Geht so.",
            "{keyword} funktioniert, könnte aber besser sein.",
            "Gemischte Gefühle bei {keyword}. Teils gut, teils weniger.",
        ]
        
        # Zufällige Auswahl
        if random.random() > 0.3:  # 70% positive Bewertungen
            template = random.choice(templates_positive)
        else:
            template = random.choice(templates_neutral)
        
        # Keyword einsetzen
        keyword = job_details.get('keyword', 'Das Produkt')
        review = template.format(keyword=keyword)
        
        # Zufällige Ergänzung für mehr Natürlichkeit
        additions = [
            " Würde ich nochmal machen.",
            " Hat gut geklappt.",
            " Bin zufrieden.",
            " Alles wie beschrieben.",
            ""
        ]
        review += random.choice(additions)
        
        return review
    
    async def _submit_review(self) -> bool:
        """
        WAS PASSIERT HIER:
        Findet und klickt den Submit-Button für die Bewertung.
        
        ACHTUNG:
        Oft gibt es Captchas oder Bestätigungsdialoge!
        """
        try:
            page = await self.browser_manager.get_current_page()
            
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button[class*="submit"]',
                '.submit-review',
                '#submit-btn',
                'button:contains("Submit")',
                'button:contains("Absenden")',
            ]
            
            for selector in submit_selectors:
                try:
                    submit_btn = await page.select_first(selector)
                    if submit_btn:
                        await asyncio.sleep(random.uniform(1.0, 2.5))
                        await self.browser_manager.human_click_element(submit_btn)
                        print("[VoteReview] Bewertung erfolgreich abgesendet!")
                        return True
                except Exception:
                    continue
            
            print("[VoteReview] Kein Submit-Button gefunden!")
            return False
            
        except Exception as e:
            print(f"[VoteReview] Submit-Fehler: {str(e)}")
            return False