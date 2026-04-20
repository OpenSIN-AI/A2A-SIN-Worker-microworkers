"""
================================================================================
DATEI: social_media_solver.py
PROJEKT: A2A-SIN-Worker-microworkers
ZWECK: Social Media Tasks (Follow, Like, Share, Subscribe)

WICHTIG FÜR ENTWICKLER:
Social Media Plattformen haben strenge Bot-Erkennung!
Langsame, menschliche Aktionen sind kritisch!
================================================================================
"""

import asyncio
import random
from typing import Dict, Any
from ..core.browser_manager import BrowserManager
from ..core.screenshot_manager import ScreenshotManager

class SocialMediaSolver:
    """Modul für Social Media Interaktionen."""
    
    def __init__(self, browser_manager: BrowserManager, screenshot_manager: ScreenshotManager):
        self.browser_manager = browser_manager
        self.screenshot_manager = screenshot_manager
        
    async def solve(self, job_details: Dict[str, Any]) -> bool:
        """Führt Social Media Task aus (Follow/Like/Share)."""
        try:
            url = job_details.get('url')
            action = job_details.get('action', 'follow')  # follow, like, share, subscribe
            
            if not url:
                return False
            
            page = await self.browser_manager.get_current_page()
            await page.goto(url, timeout=30000)
            
            # Menschliche Wartezeit (5-10 Sekunden)
            await asyncio.sleep(random.uniform(5.0, 10.0))
            
            # Aktion durchführen
            if action == 'follow':
                success = await self._follow(page)
            elif action == 'like':
                success = await self._like(page)
            elif action == 'subscribe':
                success = await self._subscribe(page)
            else:
                success = await self._generic_interact(page)
            
            if success:
                await self.screenshot_manager.capture_final_evidence(
                    task_type="social_media",
                    status="completed",
                    metadata={"action": action}
                )
                print(f"[SocialMedia] ✅ {action} erfolgreich!")
                return True
            
            return False
        except Exception as e:
            print(f"[SocialMedia] FEHLER: {str(e)}")
            return False
    
    async def _follow(self, page) -> bool:
        """Klickt Follow-Button."""
        selectors = [
            '[data-testid="Follow"]',
            '.FollowButton',
            'button[class*="follow"]',
            '[aria-label*="Follow"]',
        ]
        return await self._click_any(page, selectors)
    
    async def _like(self, page) -> bool:
        """Klickt Like-Button."""
        selectors = [
            '[data-testid="Like"]',
            '.LikeButton',
            'button[class*="like"]',
            '[aria-label*="Like"]',
        ]
        return await self._click_any(page, selectors)
    
    async def _subscribe(self, page) -> bool:
        """Klickt Subscribe-Button."""
        selectors = [
            '#subscribe-button',
            '.SubscribeButton',
            'button[class*="subscribe"]',
            'yt-subscribe-button',
        ]
        return await self._click_any(page, selectors)
    
    async def _generic_interact(self, page) -> bool:
        """Generische Interaktion als Fallback."""
        # Einfach scrollen und warten als minimale Interaktion
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2.0)
        return True
    
    async def _click_any(self, page, selectors: list) -> bool:
        """Versucht mehrere Selektoren nacheinander."""
        for selector in selectors:
            try:
                element = await page.select_first(selector)
                if element:
                    await asyncio.sleep(random.uniform(1.0, 2.5))
                    await element.click()
                    return True
            except Exception:
                continue
        return False