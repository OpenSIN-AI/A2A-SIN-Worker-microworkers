"""
================================================================================
DATEI: code_extraction_solver.py
PROJEKT: A2A-SIN-Worker-microworkers
ZWECK: Extrahiert Codes von Webseiten (Facebook, Email, etc.)

WICHTIG FÜR ENTWICKLER:
Codes müssen präzise extrahiert werden! Falsche Codes = Ablehnung!
================================================================================
"""

import asyncio
import re
from typing import Dict, Any, Optional
from ..core.browser_manager import BrowserManager
from ..core.screenshot_manager import ScreenshotManager

class CodeExtractionSolver:
    """Modul zur Extraktion von Bestätigungscodes."""
    
    def __init__(self, browser_manager: BrowserManager, screenshot_manager: ScreenshotManager):
        self.browser_manager = browser_manager
        self.screenshot_manager = screenshot_manager
        
    async def solve(self, job_details: Dict[str, Any]) -> bool:
        """Extrahiert Code von Ziel-URL."""
        try:
            url = job_details.get('url')
            if not url:
                return False
            
            page = await self.browser_manager.get_current_page()
            await page.goto(url, timeout=30000)
            await asyncio.sleep(3.0)
            
            # Code extrahieren (verschiedene Patterns)
            code = await self._extract_code(page)
            
            if code:
                # Screenshot als Beweis
                await self.screenshot_manager.capture_final_evidence(
                    task_type="code_extraction",
                    status="completed",
                    metadata={"code": code}
                )
                print(f"[CodeExtraction] ✅ Code gefunden: {code}")
                return True
            
            return False
        except Exception as e:
            print(f"[CodeExtraction] FEHLER: {str(e)}")
            return False
    
    async def _extract_code(self, page) -> Optional[str]:
        """Extrahiert Code aus Seiteninhalt."""
        content = await page.evaluate("document.body.innerText")
        
        # Pattern für alphanumerische Codes (4-8 Zeichen)
        patterns = [
            r'\b[A-Z0-9]{4,8}\b',  # Großbuchstaben + Zahlen
            r'Code[:\s]*([A-Z0-9]{4,8})',  # "Code: ABC123"
            r'confirmation[:\s]*([A-Z0-9]{4,8})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return None