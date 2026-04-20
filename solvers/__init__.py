# ==============================================================================
# DATEI: solvers/__init__.py
# PROJEKT: A2A-SIN-Worker-microworkers
# ZWECK: Initialisiert alle Job-Solver Module
#
# WICHTIG FÜR ENTWICKLER:
# Hier werden alle spezialisierten Solver für verschiedene Job-Typen exportiert.
# Jeder Solver ist auf eine bestimmte Aufgabe spezialisiert.
# ==============================================================================

from .search_solver import SearchSolver
from .screenshot_solver import ScreenshotSolver
from .vote_review_solver import VoteReviewSolver
from .code_extraction_solver import CodeExtractionSolver
from .social_media_solver import SocialMediaSolver

__all__ = [
    'SearchSolver',
    'ScreenshotSolver', 
    'VoteReviewSolver',
    'CodeExtractionSolver',
    'SocialMediaSolver'
]
