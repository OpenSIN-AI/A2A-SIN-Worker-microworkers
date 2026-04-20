"""
================================================================================
DATEI: screenshot_solver.py
PROJEKT: A2A-SIN-Worker-microworkers
ZWECK: Löst "Screenshot-Aufgaben" auf Microworkers.com
       (Suchen -> Seite besuchen -> Screenshots erstellen -> hochladen)

WICHTIG FÜR ENTWICKLER:
Screenshot-Qualität und -Anzahl sind kritisch für die Abnahme!
Falsche Implementierung führt zu 100% Ablehnungsrate.
JEDEN Kommentar lesen vor Änderungen!

AUTOR: OpenSIN AI Team
LIZENZ: Proprietary (OpenSIN Konzern)
================================================================================
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, Any, List
from ..core.browser_manager import BrowserManager
from ..core.screenshot_manager import ScreenshotManager

class ScreenshotSolver:
    """Spezialisiertes Modul für Screenshot-basierte Microworkers-Jobs."""
    
    def __init__(self, browser_manager: BrowserManager, screenshot_manager: ScreenshotManager):
        self.browser_manager = browser_manager
        self.screenshot_manager = screenshot_manager
        
    async def solve(self, job_details: Dict[str, Any]) -> bool:
        """Hauptmethode zur Lösung einer Screenshot-Aufgabe."""
        try:
            target_urls = job_details.get('urls', [])
            required_count = job_details.get('screenshot_count', 1)
            
            if not target_urls:
                return False
            
            for i, url in enumerate(target_urls[:10]):
                await self._navigate_and_capture(url, i)
            
            await self.screenshot_manager.capture_final_evidence(
                task_type="screenshot_task", status="completed"
            )
            return True
        except Exception as e:
            print(f"[ScreenshotSolver] FEHLER: {str(e)}")
            return False
    
    async def _navigate_and_capture(self, url: str, index: int) -> bool:
        """Navigiert zu URL und erstellt Screenshot."""
        try:
            page = await self.browser_manager.get_current_page()
            await page.goto(url, timeout=30000)
            await asyncio.sleep(2.0)
            
            filename = f"screenshot_{index}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = f"/tmp/screenshots/{filename}"
            os.makedirs("/tmp/screenshots", exist_ok=True)
            
            await page.screenshot(filepath=filepath, full_page=True)
            return os.path.exists(filepath) and os.path.getsize(filepath) > 0
        except Exception:
            return False