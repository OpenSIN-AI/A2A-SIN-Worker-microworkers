#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
DATEI: bridge_handler.py
PROJEKT: A2A-SIN-Worker-microworkers
ZWECK: Verwaltet die Verbindung zur OpenSIN-Bridge (falls verfuegbar)

WICHTIG FUER ENTWICKLER:
Dieses Modul entscheidet, ob die Bridge genutzt wird oder der Direktmodus.
Falsche Handhabung kann dazu fuehren, dass der Agent nicht mehr funktioniert.
================================================================================
"""

import asyncio
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class BridgeHandler:
    """Verwaltet die Verbindung zur OpenSIN-Browser-Bridge."""
    
    def __init__(self):
        self.bridge_available = False
        self.bridge_session = None
        self.fallback_mode = False
        
    async def check_bridge_availability(self) -> bool:
        """Prueft ob OpenSIN-Bridge erreichbar ist."""
        try:
            logger.info("Pruefe OpenSIN-Bridge Verfuegbarkeit...")
            from websockets import connect
            
            async with connect("ws://localhost:9222", close_timeout=3) as websocket:
                await websocket.send('{"id": 1, "method": "Browser.getVersion"}')
                response = await asyncio.wait_for(websocket.recv(), timeout=3)
                
                if response:
                    self.bridge_available = True
                    self.fallback_mode = False
                    logger.info("OpenSIN-Bridge verfuegbar!")
                    return True
        except Exception as e:
            logger.warning(f"Bridge nicht erreichbar: {e}")
            self.bridge_available = False
            self.fallback_mode = True
            return False
            
    async def get_browser_instance(self):
        """Gibt Browser-Instanz zurueck (Bridge oder Fallback)."""
        if self.bridge_available and not self.fallback_mode:
            logger.info("Nutze OpenSIN-Bridge Modus")
            return await self._connect_to_bridge()
        else:
            logger.info("Nutze Direktmodus (nodriver)")
            return await self._start_fallback_browser()
            
    async def _connect_to_bridge(self):
        """Verbindet mit existierender Bridge."""
        try:
            import nodriver as uc
            browser = await uc.start(headless=False)
            self.bridge_session = browser
            return browser
        except Exception as e:
            logger.error(f"Bridge-Verbindung fehlgeschlagen: {e}")
            self.fallback_mode = True
            return await self._start_fallback_browser()
            
    async def _start_fallback_browser(self):
        """Startet lokalen Browser als Fallback."""
        try:
            import nodriver as uc
            config = {
                "headless": False,
                "sandbox": False,
                "disable_blink_features": "AutomationControlled"
            }
            browser = await uc.start(config)
            return browser
        except Exception as e:
            logger.critical(f"Fallback-Browser Start fehlgeschlagen: {e}")
            raise
