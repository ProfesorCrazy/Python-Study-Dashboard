# Python Study Dashboard

Ein terminalbasiertes Dashboard zur Analyse und Visualisierung des persönlichen Studienfortschritts.

Das Projekt wurde im Rahmen des Kurses **Objektorientierte und funktionale Programmierung mit Python** entwickelt. Ziel ist es, den aktuellen Studienfortschritt übersichtlich darzustellen und zentrale Kennzahlen wie ECTS-Fortschritt, Notendurchschnitt, Modulstatus und Prüfungsvorbereitung sichtbar zu machen.

## Projektziel

Das Dashboard unterstützt Studierende dabei, ihren Studienverlauf besser zu überwachen. Im Mittelpunkt stehen zwei zentrale Ziele:

- Abschluss des Studiums innerhalb von 36 Monaten
- Erreichen eines gewichteten Notendurchschnitts von maximal 1,7

Dazu werden verschiedene Kennzahlen ausgewertet und in einer interaktiven Terminaloberfläche dargestellt.

## Funktionen

Das Dashboard zeigt unter anderem:

- aktuellen ECTS-Fortschritt
- Vergleich zwischen Zielkurve und tatsächlichem Studienfortschritt
- Notenübersicht über das gesamte Studium
- Notenübersicht des aktuellen Semesters
- Modulübersicht mit Lernfortschritt
- Prüfungsfortschritt je Modul
- vorhandene Noten und Gewichtungen
- Import der Studiendaten aus einer JSON-Datei
- Speicherung der Daten in einer SQLite-Datenbank

## Technologiestack

Das Projekt verwendet folgende Technologien:

- Python >= 3.13
- Textual für die terminalbasierte Benutzeroberfläche
- textual-plotext für Diagramme im Terminal
- SQLite für die lokale Datenspeicherung
- JSON als Ausgangsformat für Studiendaten
- Git und GitHub zur Versionsverwaltung

## Projektstruktur

```text
Python-Study-Dashboard/
│
├── main.py                  # Startpunkt der Anwendung und zentrale Dashboard-App
├── models.py                # Fachliche Modellklassen des Dashboards
├── database.py              # SQLite-Datenbankzugriff und Laden der Objekte
├── importer.py              # Import der Studiendaten aus study.json
├── ui.py                    # Wiederverwendbare Textual-Widgets
├── ui.tcss                  # Styling der Terminaloberfläche
├── study.json               # Studiendaten für den Import
├── database.db              # Lokale SQLite-Datenbank, wird bei Bedarf erzeugt
├── pyproject.toml           # Projekt- und Abhängigkeitsdefinition
└── README.md                # Projektdokumentation
```

## Architektur

Das Projekt ist objektorientiert aufgebaut und in mehrere Schichten gegliedert.

### Domänenmodell

Die Datei `models.py` enthält die fachlichen Klassen des Dashboards, zum Beispiel:

- `Study`
- `Semester`
- `Module`
- `Progress`
- `Exam`
- `Grade`

Zusätzlich gibt es mehrere spezialisierte Prüfungsarten, die von `Exam` erben, zum Beispiel:

- `PortfolioExam`
- `HomeworkExam`
- `SeminarPaperExam`
- `CaseStudyExam`
- `ProjectReportExam`
- `ProjectPresentationExam`
- `AdvancedWorkbookExam`
- `BachelorThesisExam`
- `ColloquiumExam`

Dadurch kann jede Prüfungsform ihren eigenen Fortschritt berechnen, während die Benutzeroberfläche allgemein mit `Exam`-Objekten arbeiten kann.

### Persistenz

Die Klasse `Database` in `database.py` kapselt den Zugriff auf SQLite. Sie erstellt die notwendigen Tabellen, speichert Studiendaten und lädt daraus wieder Python-Objekte.

### Import

Die Klasse `Importer` in `importer.py` liest die Datei `study.json` ein und überträgt die enthaltenen Daten in die SQLite-Datenbank.

### Benutzeroberfläche

Die Oberfläche basiert auf Textual. Die Hauptklasse `StudyDashboard` befindet sich in `main.py`. Wiederverwendbare UI-Komponenten sind in `ui.py` ausgelagert, zum Beispiel:

- `ModuleWidget`
- `ModuleProgressWidget`
- `ExamWidget`
- `GradeWidget`

## Installation

### Voraussetzungen

Für die Ausführung werden benötigt:

- Python >= 3.13
- Git
- Internetverbindung zur Installation der Python-Bibliotheken

### Repository klonen

```bash
git clone https://github.com/ProfesorCrazy/Python-Study-Dashboard.git
cd Python-Study-Dashboard
```

### Virtuelle Umgebung erstellen

Unter Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Unter macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### Abhängigkeiten installieren

```bash
pip install .
```

## Anwendung starten

Das Dashboard wird aus dem Projektordner heraus gestartet:

```bash
python main.py
```

Nach dem Start wird eine Terminaloberfläche geöffnet. Die Anwendung importiert die Studiendaten aus `study.json`, speichert sie in einer SQLite-Datenbank und zeigt anschließend die wichtigsten Kennzahlen zum Studienfortschritt an.

## Datenbasis

Die Studiendaten werden aus der Datei `study.json` importiert. Diese Datei enthält Informationen zu:

- Studiengang
- Semestern
- Modulen
- ECTS-Punkten
- Lernfortschritt
- Prüfungen
- Prüfungsarten
- Noten

Beim Start der Anwendung werden die Daten in die SQLite-Datenbank übernommen. Bereits vorhandene Einträge werden aktualisiert.

## Beispielhafte Kennzahlen

Das Dashboard berechnet unter anderem:

- gewichteten Notendurchschnitt
- Durchschnittsnote pro Semester
- kumulierte ECTS-Punkte
- durchschnittlichen ECTS-Fortschritt
- Lernfortschritt einzelner Module
- Fortschritt verschiedener Prüfungsarten

## Objektorientierte Konzepte

Im Projekt werden zentrale objektorientierte Konzepte umgesetzt:

- Klassen und Objekte
- Dataclasses
- Komposition
- Aggregation
- Vererbung
- Polymorphie
- Kapselung durch klare Verantwortlichkeiten
- Typannotationen
- optionale Werte mit `None`

Ein Beispiel für Polymorphie ist die Methode `get_progress_percent()`. Jede Prüfungsart implementiert ihre eigene Fortschrittsberechnung, während die UI diese Methode unabhängig vom konkreten Prüfungstyp aufrufen kann.

## Ziel des Prototyps

Der Prototyp soll zeigen, dass das entwickelte Konzept mit Python technisch umsetzbar ist. Der Fokus liegt dabei nicht auf einer produktionsreifen Anwendung, sondern auf einer nachvollziehbaren objektorientierten Modellierung und einer funktionierenden prototypischen Umsetzung.

## Autor

Josua Würzle

## Lizenz

Dieses Projekt wurde im Rahmen einer Studienleistung erstellt.
