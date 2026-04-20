"""
==============================================================================
DATEI: core/job_parser.py
PROJEKT: A2A-SIN-Worker-microworkers
ZWECK: Analysiert Job-Beschreibungen und extrahiert Anforderungen automatisch

WICHTIG FÜR ENTWICKLER:
Dieses Modul ist das "Auge" des Agents. Es liest Job-Titel und Beschreibungen
und entscheidet, welcher Job-Typ vorliegt. Fehler hier führen zu falscher
Ausführungsstrategie = Ablehnung durch Arbeitgeber!

Jeder Job-Typ auf Microworkers hat ein spezifisches Muster:
- TTV = Time To Verify (Suchen + Verweilen)
- Screenshot = Beweissicherung nötig
- Bonus = Zusätzliche Interaktion erforderlich
==============================================================================
"""

import re
from typing import Dict, List, Optional


class JobType:
    """
    WAS PASSIERT HIER: Definiert alle bekannten Job-Typen auf Microworkers
    WARUM NICHT X: Hardcodierte Strings sind fehleranfällig, daher als Klasse
    """
    
    # Suchmaschinen-Jobs (Bing/Google)
    SEARCH_AND_VOTE = "search_and_vote"           # Suchen + Abstimmen + Bewerten
    SEARCH_INTERACT_BONUS = "search_interact_bonus"  # Suchen + Interagieren + Bonus
    SEARCH_VISIT_SCREENSHOT = "search_visit_screenshot"  # Suchen + Besuchen + Screenshot
    SEARCH_VISIT_INFO = "search_visit_info"       # Suchen + Besuchen + Info erhalten
    
    # Recherche-Jobs
    WEB_RESEARCH = "web_research"                 # Doppelte Suche + Info beschaffen
    WORD_COUNT = "word_count"                     # Wörter zählen auf Seite
    DOWNLOAD_VERIFY = "download_verify"           # Herunterladen + Verifizieren
    
    # Social Media Jobs
    SOCIAL_FOLLOW = "social_follow"               # Facebook/Instagram folgen
    SOCIAL_CODE = "social_code"                   # Code von Social Media holen
    
    # E-Commerce Jobs
    CART_ADD = "cart_add"                         # Produkt in Warenkorb
    
    # Unbekannter Typ (Fallback)
    UNKNOWN = "unknown"


class JobParser:
    """
    WAS PASSIERT HIER: Hauptklasse zur Job-Analyse
    ACHTUNG: Dieses Modul entscheidet über Erfolg oder Ablehnung!
    
    ENTWICKLER-HINWEIS:
    - Immer neue Muster hinzufügen wenn Job-Typen scheitern
    - Regex-Patterns sind case-insensitive (Groß/Kleinschreibung egal)
    - Priorität: Spezifische Patterns zuerst, allgemeine danach
    """
    
    def __init__(self):
        """
        Initialisiert den Parser mit allen bekannten Mustern
        WAS PASSIERT HIER: Erstellt Pattern-Matching Regeln für jeden Job-Typ
        """
        
        # Pattern für Suchen + Abstimmen + Bewerten Jobs
        self.vote_patterns = [
            r'ttv.*abstimmen.*bewerten',
            r'suchen.*abstimmen.*bewertung',
            r'vote.*rate.*review',
            r'search.*vote.*honest.*review'
        ]
        
        # Pattern für Suchen + Interagieren + Bonus
        self.interact_bonus_patterns = [
            r'ttv.*interact.*bonus',
            r'suchen.*interagieren.*bonus',
            r'search.*interact.*bonus',
            r'bing.*int.*page.*bonus',
            r'google.*int.*page.*bonus'
        ]
        
        # Pattern für Jobs mit Screenshots
        self.screenshot_patterns = [
            r'screenshot',
            r'screenshots',
            r'bildevidence',
            r'proof.*image',
            r'4.*screenshots',  # Spezifisch: 4 Screenshots
            r'make.*screenshot'
        ]
        
        # Pattern für Wörter-Zählen Jobs
        self.wordcount_patterns = [
            r'wörter.*zählen',
            r'words.*count',
            r'count.*words',
            r'anzahl.*wörter'
        ]
        
        # Pattern für Download-Jobs
        self.download_patterns = [
            r'herunterladen.*bilder',
            r'download.*images',
            r'download.*files',
            r'12.*bilder.*download'
        ]
        
        # Pattern für Warenkorb-Jobs
        self.cart_patterns = [
            r'warenkorb',
            r'cart.*add',
            r'in.*den.*warenkorb',
            r'add.*to.*cart'
        ]
        
        # Pattern für Social Media Jobs
        self.social_patterns = [
            r'facebook.*besuchen.*code',
            r'follow.*us.*code',
            r'instagram.*follow',
            r'social.*media.*visit'
        ]
        
        # Pattern für Recherche-Jobs
        self.research_patterns = [
            r'recherche',
            r'research',
            r'information.*beschaffen',
            r'gather.*information',
            r'double.*search'
        ]
    
    def parse_job_title(self, title: str) -> Dict:
        """
        WAS PASSIERT HIER: Analysiert Job-Titel und erkennt Typ
        
        PARAMETER:
        - title: Der Job-Titel von Microworkers (z.B. "TTV - Abstimmen & Bewerten")
        
        RÜCKGABE:
        Dictionary mit:
        - job_type: Erkenneter Typ (aus JobType Klasse)
        - confidence: Wie sicher ist die Erkennung (0.0 bis 1.0)
        - requires_screenshot: Bool, ob Screenshots nötig sind
        - requires_bonus: Bool, ob Bonus-Aktion nötig ist
        - estimated_time: Geschätzte Zeit in Minuten
        
        ENTWICKLER-HINWEIS:
        Wenn confidence < 0.5, sollte der Agent den Job überspringen!
        """
        
        title_lower = title.lower()
        result = {
            'job_type': JobType.UNKNOWN,
            'confidence': 0.0,
            'requires_screenshot': False,
            'requires_bonus': False,
            'estimated_time': 5,  # Standard: 5 Minuten
            'keywords': []
        }
        
        # Check: Enthält Job Screenshot-Anforderung? (Priorität 1)
        if self._matches_any_pattern(title_lower, self.screenshot_patterns):
            result['requires_screenshot'] = True
            result['keywords'].append('screenshot')
            result['estimated_time'] += 2  # Extra Zeit für Screenshots
        
        # Check: Bonus vorhanden? (Priorität 2)
        if 'bonus' in title_lower or self._matches_any_pattern(title_lower, self.interact_bonus_patterns):
            result['requires_bonus'] = True
            result['keywords'].append('bonus')
        
        # Check: Vote/Abstimmen Jobs (Priorität 3)
        if self._matches_any_pattern(title_lower, self.vote_patterns):
            result['job_type'] = JobType.SEARCH_AND_VOTE
            result['confidence'] = 0.95
            result['keywords'].append('vote')
            result['estimated_time'] = 7
        
        # Check: Interact + Bonus Jobs (Priorität 4)
        elif self._matches_any_pattern(title_lower, self.interact_bonus_patterns):
            result['job_type'] = JobType.SEARCH_INTERACT_BONUS
            result['confidence'] = 0.90
            result['keywords'].append('interact')
            result['estimated_time'] = 7
        
        # Check: Wörter zählen (Priorität 5)
        elif self._matches_any_pattern(title_lower, self.wordcount_patterns):
            result['job_type'] = JobType.WORD_COUNT
            result['confidence'] = 0.92
            result['keywords'].append('wordcount')
            result['estimated_time'] = 3
        
        # Check: Download Jobs (Priorität 6)
        elif self._matches_any_pattern(title_lower, self.download_patterns):
            result['job_type'] = JobType.DOWNLOAD_VERIFY
            result['confidence'] = 0.88
            result['keywords'].append('download')
            result['estimated_time'] = 5
        
        # Check: Warenkorb Jobs (Priorität 7)
        elif self._matches_any_pattern(title_lower, self.cart_patterns):
            result['job_type'] = JobType.CART_ADD
            result['confidence'] = 0.85
            result['keywords'].append('cart')
            result['estimated_time'] = 4
        
        # Check: Social Media Jobs (Priorität 8)
        elif self._matches_any_pattern(title_lower, self.social_patterns):
            result['job_type'] = JobType.SOCIAL_FOLLOW
            result['confidence'] = 0.87
            result['keywords'].append('social')
            result['estimated_time'] = 3
        
        # Check: Recherche Jobs (Priorität 9)
        elif self._matches_any_pattern(title_lower, self.research_patterns):
            result['job_type'] = JobType.WEB_RESEARCH
            result['confidence'] = 0.83
            result['keywords'].append('research')
            result['estimated_time'] = 8
        
        # Fallback: Wenn "suchen" oder "search" enthalten ist
        elif 'suchen' in title_lower or 'search' in title_lower:
            if result['requires_screenshot']:
                result['job_type'] = JobType.SEARCH_VISIT_SCREENSHOT
                result['confidence'] = 0.75
            else:
                result['job_type'] = JobType.SEARCH_VISIT_INFO
                result['confidence'] = 0.70
        
        return result
    
    def _matches_any_pattern(self, text: str, patterns: List[str]) -> bool:
        """
        WAS PASSIERT HIER: Prüft ob Text auf eines der Patterns passt
        
        ACHTUNG:
        - Alle Patterns sind Regex
        - Case-insensitive Matching
        - Erster Treffer reicht für True
        
        PARAMETER:
        - text: Zu prüfender Text (bereits lowercase)
        - patterns: Liste von Regex-Pattern Strings
        
        RÜCKGABE:
        True wenn mindestens ein Pattern matcht, sonst False
        """
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def extract_search_query(self, description: str) -> Optional[str]:
        """
        WAS PASSIERT HIER: Extrahiert die Suchanfrage aus der Job-Beschreibung
        
        BEISPIEL:
        Beschreibung: "Suche bei Google nach 'beste Restaurants Berlin'"
        Rückgabe: "beste Restaurants Berlin"
        
        ENTWICKLER-HINWEIS:
        Wenn None zurückgegeben wird, muss der Agent manuell nachfragen
        oder den Job ablehnen!
        """
        
        # Pattern 1: Anführungszeichen extrahieren
        quoted_match = re.search(r"['\"](.*?)['\"]", description)
        if quoted_match:
            return quoted_match.group(1)
        
        # Pattern 2: Nach "suche nach" oder "search for"
        after_search = re.search(r'(?:suche|search).?(?:nach|for)[:\s]+([^.!?]+)', 
                                 description, re.IGNORECASE)
        if after_search:
            return after_search.group(1).strip()
        
        # Pattern 3: URL extrahieren falls vorhanden
        url_match = re.search(r'https?://[^\s]+', description)
        if url_match:
            return url_match.group(0)
        
        return None
    
    def get_execution_strategy(self, job_type: str) -> Dict:
        """
        WAS PASSIERT HIER: Gibt die Ausführungsstrategie für Job-Typ zurück
        
        RÜCKGABE:
        Dictionary mit Schritten die der Agent ausführen muss
        
        WICHTIG:
        Diese Strategie wird direkt vom Main-Agenten ausgeführt!
        Fehler hier = kompletter Job-Fail!
        """
        
        strategies = {
            JobType.SEARCH_AND_VOTE: {
                'steps': [
                    'open_search_engine',
                    'perform_search',
                    'click_first_result',
                    'wait_random_30_to_60_seconds',
                    'find_voting_widget',
                    'cast_vote',
                    'write_review_if_required',
                    'submit_proof'
                ],
                'requires_human_behavior': True,
                'min_wait_time': 45
            },
            
            JobType.SEARCH_INTERACT_BONUS: {
                'steps': [
                    'open_search_engine',
                    'perform_search',
                    'click_specific_result',
                    'scroll_page_slowly',
                    'interact_with_element',
                    'wait_on_page_60_seconds',
                    'claim_bonus',
                    'submit_proof'
                ],
                'requires_human_behavior': True,
                'min_wait_time': 60
            },
            
            JobType.SEARCH_VISIT_SCREENSHOT: {
                'steps': [
                    'open_search_engine',
                    'perform_search',
                    'click_result',
                    'wait_on_page',
                    'take_screenshot_full_page',
                    'save_screenshot_with_timestamp',
                    'upload_screenshot',
                    'submit_proof'
                ],
                'requires_screenshot': True,
                'min_wait_time': 40
            },
            
            JobType.WORD_COUNT: {
                'steps': [
                    'navigate_to_url',
                    'select_all_text',
                    'count_words_programmatically',
                    'verify_count_twice',
                    'enter_word_count',
                    'submit_proof'
                ],
                'requires_screenshot': False,
                'min_wait_time': 20
            },
            
            JobType.DOWNLOAD_VERIFY: {
                'steps': [
                    'navigate_to_url',
                    'find_download_links',
                    'download_all_files',
                    'verify_download_complete',
                    'take_screenshot_of_downloads',
                    'submit_proof'
                ],
                'requires_screenshot': True,
                'min_wait_time': 90  # Downloads brauchen Zeit
            },
            
            JobType.CART_ADD: {
                'steps': [
                    'navigate_to_product_page',
                    'select_options_if_any',
                    'click_add_to_cart',
                    'wait_for_confirmation',
                    'take_screenshot_of_cart',
                    'do_not_checkout',
                    'submit_proof'
                ],
                'requires_screenshot': True,
                'min_wait_time': 30
            },
            
            JobType.SOCIAL_FOLLOW: {
                'steps': [
                    'navigate_to_social_url',
                    'check_if_logged_in',
                    'click_follow_button',
                    'wait_for_confirmation',
                    'extract_code_if_required',
                    'submit_proof'
                ],
                'requires_screenshot': False,
                'min_wait_time': 15
            },
            
            JobType.WEB_RESEARCH: {
                'steps': [
                    'perform_first_search',
                    'extract_information',
                    'perform_second_search',
                    'cross_reference_info',
                    'compile_answer',
                    'submit_proof'
                ],
                'requires_screenshot': False,
                'min_wait_time': 120  # Recherche braucht Zeit
            }
        }
        
        # Fallback für unbekannte Typen
        if job_type not in strategies:
            return {
                'steps': ['manual_review_required'],
                'error': f'Unknown job type: {job_type}',
                'requires_human_intervention': True
            }
        
        return strategies[job_type]


# =============================================================================
# MAIN TEST BLOCK (Nur für Entwicklung, wird im Produktivbetrieb nicht genutzt)
# =============================================================================
if __name__ == "__main__":
    """
    WAS PASSIERT HIER: Testet den Parser mit Beispiel-Jobs
    
    ENTWICKLER-HINWEIS:
    Nutze diesen Block um neue Pattern zu testen bevor sie live gehen!
    """
    
    parser = JobParser()
    
    test_jobs = [
        "TTV – Abstimmen & Bewerten: Suchen + Abstimmen + Ehrliche Bewertung",
        "TTV-Bng Int Page: Suchen + Interagieren + Bonus",
        "TTV-Out-Page: Suchen + Interagieren + Screenshot + Bonus",
        "Transfers: Suchen + Besuchen + Wörter zählen",
        "Seite: Suchen + Besuchen + Herunterladen 12 Bilder + Screenshot",
        "Produkt: In den Warenkorb + Screenshot",
        "Facebook-Beitrag: Besuchen Sie uns und erhalten Sie den Code."
    ]
    
    print("=" * 80)
    print("JOB PARSER TEST - Microworkers")
    print("=" * 80)
    
    for job_title in test_jobs:
        result = parser.parse_job_title(job_title)
        print(f"\nJob: {job_title}")
        print(f"  Typ: {result['job_type']}")
        print(f"  Sicherheit: {result['confidence']*100:.1f}%")
        print(f"  Screenshot nötig: {'JA' if result['requires_screenshot'] else 'NEIN'}")
        print(f"  Bonus nötig: {'JA' if result['requires_bonus'] else 'NEIN'}")
        print(f"  Geschätzte Zeit: {result['estimated_time']} min")
        
        strategy = parser.get_execution_strategy(result['job_type'])
        print(f"  Schritte: {len(strategy.get('steps', []))}")
    
    print("\n" + "=" * 80)
    print("TEST ABGESCHLOSSEN")
    print("=" * 80)
