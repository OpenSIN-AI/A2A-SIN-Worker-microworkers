# A2A-SIN-Worker-microworkers

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![OpenSIN AI](https://img.shields.io/badge/OpenSIN-AI-orange)](https://github.com/OpenSIN-AI)

## 🚀 Vollautonomer Agent für Microworkers.com

**Dieser Agent erledigt komplett selbstständig bezahlte Mikro-Jobs auf Microworkers.com – ohne menschliches Eingreifen.**

---

## 📋 INHALT

- [Features](#-features)
- [Architektur](#-architektur)
- [Installation](#-installation)
- [Konfiguration](#-konfiguration)
- [Nutzung](#-nutzung)
- [Job-Typen](#-job-typen)
- [Fehlerbehandlung](#-fehlerbehandlung)
- [Integration](#-integration)

---

## ✨ FEATURES

| Feature | Beschreibung | Vorteil |
|---------|--------------|---------|
| **🤖 Vollautonom** | Entscheidet selbst welche Jobs angenommen werden | Kein menschliches Eingreifen nötig |
| **🎯 Intelligente Job-Auswahl** | Bewertet Jobs nach Payment, Erfolgsquote, Zeit | Maximiert Profit bei minimalem Risiko |
| **🥷 Stealth-Modus** | Nutzt nodriver + menschliche Mausbewegungen | Umgeht Bot-Erkennung effektiv |
| **🔄 Self-Healing** | Automatische Fehlerbehandlung und Retry-Logik | Läuft stabil auch bei Problemen |
| **📸 Screenshot-Automatik** | Erstellt Beweise genau nach Plattform-Anforderungen | Vermeidet Job-Ablehnungen |
| **🧠 Global Brain Sync** | Lernt von anderen OpenSIN-Agenten | Verbessert sich kontinuierlich |
| **🔗 Bridge-Fallback** | Nutzt OpenSIN-Bridge wenn verfügbar | Beste Performance durch Hybrid-Ansatz |

---

## 🏗 ARCHITEKTUR

```
┌─────────────────────────────────────────────────────────────┐
│                    A2A-SIN-Worker                            │
│                   (Microworkers Edition)                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Browser    │  │    Bridge    │  │  Job Analyzer│      │
│  │   Manager    │  │   Handler    │  │              │      │
│  │              │  │              │  │              │      │
│  │  - nodriver  │  │  - Connect   │  │  - Scoring   │      │
│  │  - Stealth   │  │  - Fallback  │  │  - Filter    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Execution   │  │   Screenshot │  │ Global Brain │      │
│  │   Engine     │  │   Manager    │  │    Sync      │      │
│  │              │  │              │  │              │      │
│  │  - Login     │  │  - Capture   │  │  - Learning  │      │
│  │  - Execute   │  │  - Validate  │  │  - Sharing   │      │
│  │  - Submit    │  │  - Store     │  │  - Strategy  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Microworkers   │
                    │      .com       │
                    └─────────────────┘
```

---

## 📦 INSTALLATION

### Voraussetzungen

- **Python 3.9 oder höher**
- **Google Chrome** (aktuelle Version)
- **Git**

### Schritt-für-Schritt

```bash
# 1. Repository klonen
git clone https://github.com/OpenSIN-AI/A2A-SIN-Worker-microworkers.git
cd A2A-SIN-Worker-microworkers

# 2. Virtuelle Umgebung erstellen (empfohlen)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. Umgebungsvariablen konfigurieren (siehe Konfiguration)
cp .env.example .env
# Bearbeite .env mit deinen Credentials
```

---

## ⚙ KONFIGURATION

### Umgebungsvariablen (.env Datei)

Erstellen Sie eine `.env` Datei im Hauptverzeichnis:

```bash
# Microworkers Login-Daten
MICROWORKERS_USERNAME=dein_benutzername
MICROWORKERS_PASSWORD=dein_sicheres_passwort

# Optional: OpenSIN Infrastruktur
OPENSIN_BRAIN_URL=https://brain.opensin.ai
OPENSIN_BRIDGE_ENABLED=true

# Agent Einstellungen
MIN_PAYMENT=0.05          # Mindestzahlung pro Job in USD
MIN_SUCCESS_RATE=80       # Mindestens 80% Erfolgsquote
MAX_JOBS_PER_CYCLE=10     # Maximal 10 Jobs pro Durchlauf
PAUSE_MIN=3               # Minimale Pause zwischen Jobs (Sekunden)
PAUSE_MAX=8               # Maximale Pause zwischen Jobs (Sekunden)
```

### WICHTIGE HINWEISE

⚠️ **Sicherheit:**
- Speichern Sie NIEMALS Passwörter im Code!
- Nutzen Sie immer Umgebungsvariablen
- Fügen Sie `.env` zu `.gitignore` hinzu

⚠️ **Performance:**
- Stellen Sie sicher, dass Ihr System mindestens 4GB RAM hat
- Chrome benötigt ausreichend Ressourcen für Stealth-Modus

---

## 🚀 NUTZUNG

### Einfacher Start

```bash
# Aktiviere virtuelle Umgebung
source venv/bin/activate

# Starte den Agenten
python main.py
```

### Der Agent wird nun:

1. ✅ Browser mit Stealth-Einstellungen starten
2. ✅ Sich bei Microworkers anmelden
3. ✅ Nach verfügbaren Jobs suchen
4. ✅ Jobs analysieren und bewerten
5. ✅ Profitable Jobs auswählen und ausführen
6. ✅ Screenshots als Beweise erstellen
7. ✅ Ergebnisse einreichen
8. ✅ Von vorne beginnen (Endlosschleife)

### Stoppen des Agents

Drücken Sie `Strg+C` im Terminal für einen sauberen Shutdown.

---

## 💼 JOB-TYPEN

Der Agent unterstützt alle gängigen Microworkers-Job-Typen:

| Job-Typ | Beschreibung | Agent-Fähigkeit |
|---------|--------------|-----------------|
| **TTV – Suchen + Abstimmen + Bewerten** | Google/Bing Suche, dann Bewertung | ✅ Vollautomatisch |
| **TTV – Suchen + Interagieren + Bonus** | Webseite besuchen, interagieren | ✅ Vollautomatisch |
| **TTV – Suchen + Screenshot** | Beweis-Screenshot erforderlich | ✅ Auto-Screenshot |
| **Web-Recherche** | Informationen finden und teilen | ✅ Mit OCR-Unterstützung |
| **Produkt in Warenkorb** | E-Commerce Aufgaben | ✅ Mit Validierung |
| **Social Media Tasks** | Facebook, Instagram, etc. | ✅ Mit Login-Handling |
| **Downloads + Screenshots** | Dateien herunterladen + beweisen | ✅ Auto-Download |

### Intelligente Job-Bewertung

Der Agent bewertet jeden Job nach:

```python
Score = (Payment * 40%) + (Erfolgsquote * 30%) + (Verfügbarkeit * 20%) + (Zeit * 10%)
```

Nur Jobs mit einem Score > 70% werden angenommen.

---

## 🛡 FEHLERBEHANDLUNG

### Self-Healing Mechanismen

| Fehler | Reaktion | Ergebnis |
|--------|----------|----------|
| Login fehlgeschlagen | 3 Retry-Versuche mit Pause | Dann Alarm |
| Job nicht auffindbar | Alternative Strategie versuchen | Oder überspringen |
| Screenshot fehlgeschlagen | Retry mit anderem Format | Beweis trotzdem erstellen |
| Bridge nicht verfügbar | Fallback zu nodriver | Weitermachen ohne Unterbrechung |
| Zu viele Fehler hintereinander | 5 Minuten Pause einlegen | Dann neu versuchen |

### Logging

Alle Aktionen werden protokolliert in:
- `microworker.log` (detaillierte Logs)
- Console Output (Echtzeit-Status)

---

## 🔗 INTEGRATION

### OpenSIN Ökosystem

Dieser Agent ist Teil des größeren OpenSIN AI Systems:

- **Infra-SIN-Global-Brain**: Zentrale Intelligenz für Schwarm-Lernen
- **OpenSIN-Bridge**: Erweiterte Browser-Automatisierung
- **OpenSIN-stealth-browser**: Stealth-Technologie
- **A2A-SIN-Worker-amazon-crowd**: Schwester-Agent für MTurk

### Global Brain Sync

Der Agent verbindet sich automatisch mit dem Global Brain:

```python
# Lernen von anderen Agenten
agent.brain_sync.download_strategies()

# Eigene Erfahrungen teilen
agent.brain_sync.upload_success_data(job_results)
```

---

## 📊 ERWARTUNGEN

### Realistische Erfolgsquoten

| Metrik | Erwartungswert | Hinweis |
|--------|----------------|---------|
| **Job Annahme** | 60-80% | Nicht alle Jobs sind geeignet |
| **Job Erfolg** | 85-95% | Bei korrekter Konfiguration |
| **Tagesverdienst** | $5-20 | Abhängig von Job-Verfügbarkeit |
| **Laufzeit** | 24/7 | Mit automatischen Pausen |

### WICHTIG

⚠️ **Kein "Get Rich Quick" Scheme!**
- Dies ist ein Werkzeug zur Automatisierung repetitiver Aufgaben
- Erfolg erfordert Geduld und korrekte Konfiguration
- Microworkers kann Accounts bei Missbrauch sperren

⚠️ **Verantwortungsvolle Nutzung:**
- Halten Sie sich an die Microworkers AGB
- Führen Sie Jobs gewissenhaft aus
- Täuschen Sie keine Ergebnisse vor

---

## 📝 LIZENZ

MIT License - Siehe [LICENSE](LICENSE) Datei für Details.

---

## 🤝 BEITRAGEN

Beiträge sind willkommen! Bitte lesen Sie zuerst unsere [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📞 SUPPORT

- **Issues:** https://github.com/OpenSIN-AI/A2A-SIN-Worker-microworkers/issues
- **Discord:** [OpenSIN Community](https://discord.gg/opensin)
- **Dokumentation:** https://docs.opensin.ai

---

**OpenSIN AI - Die Zukunft der autonomen Arbeit** 🚀
