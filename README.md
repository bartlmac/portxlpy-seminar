# Excel-Tarifrechner → Python-Rechner (LLM Proof of Concept)

*ver. 0.02 (2025-06-30)*

Dieses Repository begleitet das Video / Webinar der DAV-Arbeitsgruppe  

Excel-Tarifrechner sind in der täglichen Aktuarpraxis allgegenwärtig – aber komplexe Formeln, verstreute VBA-Makros und eingeschränkte Teamarbeit bremsen Innovation und Wartbarkeit aus.

Python bietet dank leistungsstarker Bibliotheken eine skalierbare und leicht wartbare Alternative mit klar strukturiertem Code und nahtloser Integration in moderne Workflows. In diesem Video wird gezeigt, wie man unter Einsatz eines Large-Language-Models (LLM) – hier ChatGPT – einen typischen Excel-Tarifrechner nach Python übersetzt. Dazu werden zwei unterschiedliche Ansätze vorgestellt.

**„Portierung von Referenzrechnern mit Large-Language-Models“**.  
Ziel ist es, einen klassischen Excel-Tarifrechner der Lebensversicherung reproduzierbar in **reinen Python-Code** zu überführen – in zwei unterschiedlichen Workflows (“handwerklich” vs. “industriell”).

---

## Inhaltsverzeichnis
1. [Projektüberblick](#projektüberblick)  
2. [Repository-Struktur](#repository-struktur)  
3. [Workflows](#workflows)  
   * [Arnos „handwerklicher“ Ansatz](#arnos-handwerklicher-ansatz)  
   * [Barteks „industrieller“ Ansatz](#barteks-industrieller-ansatz)  
4. [Erste Schritte](#erste-schritte)  
5. [Benutzung](#benutzung)  
6. [Tests & Berichte](#tests--berichte)  
7. [Mitwirken](#mitwirken)  
8. [Lizenz](#lizenz)

---

## Projektüberblick

* **Problem:** Excel-Tarifrechner sind schnell gebaut, aber schwer wartbar und kaum CI-fähig.  
* **Lösung:** Einsatz von Large-Language-Models, um Excel-Formeln, VBA-Module und Tabellendaten automatisiert in Python-Code zu migrieren.  
* **Mehrwert:**  
  * nachvollziehbarer, modularer Source-Code  
  * automatisierte Tests & Continuous Integration  
  * Basis für künftige Produkt- und Bestandsmigrationen innerhalb der LV-IT

Die beiden Ansätze unterscheiden sich in **Automatisierungsgrad** und **Tool-Stack**:

| Merkmal                  | Handwerklich (Arno) | Industriell (Bartek) |
|--------------------------|---------------------|----------------------|
| Input für LLM            | VBA-Quelltext & Screenshot | Vollständiger Excel-Dump als Text |
| Manuelle Schritte        | Screenshot, Copy-&-Paste der Formeln | keine |
| Zielsetzung              | schneller PoC       | vollautomatisierbarer Workflow |
| Haupterkenntnis          | LLM erkennt Zellen überraschend gut | Kontext-Limit aktuell Engpass |

---

## Repository-Struktur

```text
dev/
├─ Arno/                 # Handwerklicher Workflow
│  ├─ input/             # Chat-Verlauf (nur Prompts), Screenshot, Original-Excel
│  └─ output/            # Von ChatGPT generierter Python-Code
├─ Bartek/               # Industrieller Workflow
│  ├─ input/             # Optimierte Prompts, Original-Excel
│  └─ output/            # root: i/o und python-Module
│     └─ tests/          # PyTest-Fixtures & Smoke-Tests
└─ README.md             # *this file*
```

*(Bei neuen Files bitte die gleiche Tiefenstruktur beibehalten.)*

---

## Workflows

### Arnos „handwerklicher“ Ansatz

*Ziel:* **Rapid Prototyping** – bei möglichst wenig Prompts und Nutzung des Reasoning-Modells o1.


Idee: Da das Modell o1 keine Excel-Datei verarbeiten kann, werden die Bestandteile der Eingabedatei `Tarifrechner_KLV.xlsm` separat behandelt. Die Aufgabe wird in drei Schritte (plus einen 4. Schritt für einen Werteabgleich) zerlegt.

| Schritt | Beschreibung | Chatprotokoll | Erzeugte Dateien | 
| ------- | ------------ | ------------- | ---------------- |
| 1       | Übersetze die Tafeln aus der Eingabedatei in eine XML-Datei. Dieses Format lässt sich gut in Python verarbeiten. Dazu wird der komplette Inhalt des Tabellenblattes `Tafeln` aus der Eingabdatei per Copy&Paste an ChatGPT übergeben. | Chat 1 - Excel_nach_XML_konvertieren | `Tafeln.xml` |
| 2       | Übersetze den VBA-Code, der in der Eingabedatei enthalten ist, nach Python. Der VBA-Code besteht aus insgesamt drei Modulen (`mConstants`, `mBarwerte` und `mGwerte`), die jeweils einzeln in Textform an ChatGTP übergeben werden. Wichtig ist, dass der erzeugte Python Code die gleichen Rundungsregeln verwendet wie Excel. | Chat 2 - VBA_nach_Python_übersetzen | `constants.py` `barwerte.py` `gwerte.py` |
| 3       | Es bleibt noch die Aufgabe, das Tabellenblatt `Kalkulation`, das als User-Inferface des Excel-Rechners dient, in Python abzubilden. In diesem Rapid-Prototyping Ansatz möchten wir ein Python-Programm erzeugen, das die Eingabewerte aus dem Excel-Tabellenblat ausliest, dann die Berechnungen in Python durchführt und schließlich die Ergebnisse auf stdio ausgibt. Da das verwendete Modell kein Excel verarbeiten kann, geben wir ChatGPT zunächst einen Screenshot von dem Tabellenblatt `Kalkulation` und die verwendeten Formeln, die wir aus dem Excel-Zellen herauskopieren und als Text übergeben. ChatGPT braucht ein wenig Hilfe, um das gewünschte Ergebnis zu liefern, wie aus dem Chatprotokoll ersichtlich ist. | Chat 3 - Excel-Tarifrechner_nach_Python_mit_QS (Prompts 1 bis 9) | `verlaufswerte.py` `tarifrechner.py` (Hauptprogramm) |
| 4       | Erzeuge ein Programm, das die mit Python berechneten Werte mit den Werten des Excel-Rechners vergleicht. |  Chat 3 - Excel-Tarifrechner_nach_Python_mit_QS (Prompts 10 bis 13) | `compare_results.py` (Hauptprogramm) |


---

### Barteks „industrieller“ Ansatz

*Workflow-Ziel:* **100 % Script-gesteuerte Migration** – keine händischen Zwischenschritte.

``` mermaid
flowchart TD

subgraph Excel-Dump
    A1[excel_to_text.py<br>Zellen & Bereiche → CSV]
    A2[vba_to_text.py<br>VBA-Module → TXT]
    A3[data_extract.py<br>var.csv • tarif.csv • tafeln.csv]
    B1[tests PyTest<br>Smoke + Funktionsparitaet]
    A1 --> B1
    A2 --> B1
    A3 --> B1
end

subgraph Code-Portierung
    C1[basfunct.py<br>VBA-Basis → Python]
    D1[Bxt in ausfunct.py]
    D2[BJB • BZB • Pxt<br>offen]
    D3[verlaufswerte<br>offen]
    R1[tests PyTest<br>Referenzparitaet]
    C1 --> D1
    C1 --> D2
    C1 --> D3
    D1 --> R1
    D2 --> R1
    D3 --> R1
end

subgraph Ausführungsebene
    E1[run_calc.py<br>CLI-Runner]
end

B1 --> C1
R1 --> E1

```

*Workflow-Phasen:*

| Abschnitt | Bedeutung |
|-----------|-----------|
| **Excel-Dump & Preprocessing** | Automatisierte Extract-Skripte (Schritte 1 – 4) |
| **Code-Portierung** | Übersetzung der Logik nach Python (Schritte 5 – 6C) |
| **Ausführungsebene** | End-User-Interface via CLI (Schritt 7) |


*Konkrete TASKS / LLM-PROMPTS und Status der Implementierung:*

* ✅ erledigt / implementiert – Schritte 1–5, 6A, 7  
* ⏳ offen / Platzhalter – Schritte 6B & 6C

| Schritt | Tool / Datei       | Kurzbeschreibung                                         | Status                     |
| ------- | ------------------ | -------------------------------------------------------- | -------------------------- |
| 1       | `excel_to_text.py` | Sämtliche Zellen & Bereiche als CSV exportieren          | ✅ fertig                   |
| 2       | `vba_to_text.py`   | Alle VBA-Module als TXT sichern                          | ✅ fertig                   |
| 3       | `data_extract.py`  | Daten extrahieren → `var.csv`, `tarif.csv`, `tafeln.csv` | ✅ fertig                   |
| 4       | `tests/`           | Smoke-Tests & Funktionsparität (PyTest)                  | ✅ eingerichtet             |
| 5       | `basfunct.py`      | 1‑zu‑1‑Port der VBA-Basisfunktionen                      | ✅ vollständig              |
| 6A      | `ausfunct.py`      | `Bxt()` – Beitrag (Kalkulation!K5)                       | ✅ implementiert & getestet |
| 6B      | `ausfunct.py`      | `BJB()`, `BZB()`, `Pxt()` – weitere Ausgabewerte         | ⏳ offen                    |
| 6C      | `ausfunct.py`      | `verlaufswerte()` – Monats‑/Jahresverläufe               | ⏳ offen                    |
| 7       | `run_calc.py`      | CLI-Runner mit Argumenten für Datei‑ und Funktionswahl   | ✅ einsatzbereit            |



## Erste Schritte

### Voraussetzungen
* Python ≥ 3.11  
* Git, Make (optional)  
* Abhängigkeiten: siehe `requirements.txt`  
  (pandas, xlwings, oletools, openpyxl, pytest;  
  *optional:* junit2html, pytest-html)

### Installation
```bash
git clone https://github.com/<ORG>/excel2python-llm.git
cd excel2python-llm
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Benutzung

### CLI-Runner von Arno
```bash
# Hauptberechnung
python Arno/output/tarifrechner.py

# Werte-Gegenprobe Excel ↔ Python (optional: über pytest)
python Arno/output/compare_results.py
```

### CLI-Runner von Bartek
```bash
# Funktionsweise wählbar mit --funcs
python Bartek/output/run_calc.py --funcs Bxt
```


---

## Tests & Berichte

### Lokal ausführen
```bash
# Arno
cd Arno/output && pytest -q

# Bartek
cd Bartek/output && pytest -q
```
* Terminal bleibt dank `-q` aufgeräumt (nur „passed/failed“).  
* Ein JUnit-XML landet automatisch unter `output/tests/pytest-results.xml`  
  – inklusive aller Vergleichs-Ausgaben im `<system-out>`-Block.

### Optionales HTML-Dashboard
```bash
pip install junit2html           # einmalig oder per requirements.txt
junit2html tests/pytest-results.xml tests/report.html
```

Oder (schöner) direkt über pytest-funktionalität beim Testlauf:
```bash
pip install pytest-html          # einmalig oder per requirements.txt
pytest --html=output/tests/report.html --self-contained-html
```

---

## Mitwirken

Pull Requests sind willkommen! Bitte beachte:

1. Erstelle einen Issue für größere Änderungen.  
2. Schreibe (oder aktualisiere) Tests für neue Features.  

---

## Appendix 1: Arbeiten mit der Python-Umgebung (`.venv`) und `requirements.txt`

### Projekt lokal starten

1. **Repository klonen und ins Projektverzeichnis wechseln**  
   ```bash
   git clone <REPO-URL>
   cd <REPO-ORDNER>
   ```

2. **Virtuelle Umgebung anlegen und aktivieren**  
   - **Linux/Mac:**  
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```
   - **Windows:**  
     ```bash
     python -m venv .venv
     .venv\Scripts\activate
     ```

3. **Abhängigkeiten installieren**  
   ```bash
   pip install -r requirements.txt
   ```

### Neue Packages installieren und requirements.txt aktualisieren

1. **Neues Package in bestehender Umgebung installieren:**  
   ```bash
   pip install <paketname>
   ```

2. **`requirements.txt` aktualisieren:**  
   ```bash
   pip freeze > requirements.txt
   ```
   *(Alternativ: Paket und Version manuell eintragen.)*

3. **Teammitglieder/andere Nutzer:**  
   Nach Pull von Änderungen an der `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

**Hinweis:**  
Alle Workflows im Projekt nutzen **eine zentrale virtuelle Umgebung** und **ein gemeinsames `requirements.txt`**. Bei Problemen mit Abhängigkeiten empfiehlt sich das Löschen der `.venv` und erneutes Anlegen wie oben beschrieben.

---

## (WIP!) Appendix 2: 🛠️ Seminar Setup & Workflow

Dieser Abschnitt erklärt Schritt für Schritt, wie **Teilnehmende** das Projekt in einer **identischen, vorkonfigurierten Umgebung** starten – egal ob lokal mit Docker + VS Code oder direkt in GitHub Codespaces. Außerdem enthält er Anweisungen für **Maintainer**, um neue Seminar‑Images zu veröffentlichen.


### 1 · Voraussetzungen

| Tool | Mindestversion | Download |
|------|----------------|----------|
| **Docker Desktop** (Win / Mac) oder **Docker Engine** (Linux) | ≥ 24.x | <https://docs.docker.com/get-docker/> |
| **Visual Studio Code** | ≥ 1.90 | <https://code.visualstudio.com/> |
| VS Code Extension **„Remote – Containers“** | aktuell | `ext install ms-vscode-remote.remote-containers` |

Optional für Cloud‑Nutzung: **GitHub Codespaces** (braucht GitHub‑Team/Org‑Lizenz).

---

### 2 · Schnellstart (lokal)  
*(empfohlen für Teilnehmende)*

```bash
# 1 Repository klonen
git clone https://github.com/bartlmac/portxlpy.git
cd portxlpy

# 2 VS Code starten
code .
# → Pop‑up „Reopen in Container“ anklicken.
#   VS Code zieht das vorgebaute Image ghcr.io/bartlmac/portxlpy:seminar-202507.
#
# 3 Smoke‑Test im VS‑Code‑Terminal (im Container!)
pytest -q            # Ausgabe: 4 passed
```

> **Hinweis:** Beim ersten Öffnen lädt Docker ~250 MB; Folge‑Starts dauern Sekunden.

---

### 3 · Alternative A – Nur Container (ohne VS Code)

```bash
# Image ziehen
docker pull ghcr.io/bartlmac/portxlpy:seminar-202507

# Standard‑Run (setzt Default‑Parameter)
docker run --rm ghcr.io/bartlmac/portxlpy:seminar-202507

# Help & CLI‑Parameter anzeigen
docker run --rm ghcr.io/bartlmac/portxlpy:seminar-202507 --help
```

---

### 4 · Alternative B – GitHub Codespaces

1. Öffne das Repo im Browser → grüner **„Code“**‑Button → **„Codespaces“** → **„Create codespace on branch…“**  
2. Branch `seminar-202507` oder `main` auswählen.  
3. Codespace startet mit **demselben Dev‑Container** – Tests laufen automatisch.

---

### 5 · Authentifizierung bei privaten Images

Falls das GHCR‑Package *private* ist:

```bash
# Personal Access Token mit Scope `read:packages` erstellen
echo <GH_PAT> | docker login ghcr.io -u <github‑username> --password-stdin
```

---

### 6 · Workflow für Maintainer – neues Seminar veröffentlichen

```bash
# 1 Alle Tests grün? → neuen Tag setzen
git switch main
git pull
git tag -a seminar-202509 -m "Release September‑Seminar"
git push origin seminar-202509

# 2 CI tut den Rest:
#   • GitHub Action baut das Image
#   • pushed es nach ghcr.io/bartlmac/portxlpy:seminar-202509
#   • README/Einladungs‑Mail anpassen
```

Die Action befindet sich in `.github/workflows/build-docker.yml` und nutzt den Dockerfile aus `.devcontainer/`.

---

### 7 · Troubleshooting

| Problem                                         | Lösung                                                                                                                                        |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **„Workspace does not exist“**                  | Compose-Volume fehlt. In `.devcontainer/docker-compose.yml` sicherstellen: `volumes: - ..:/workspace:cached` → **Rebuild Container**.         |
| **VS Code meldet „Git not found“ im Container** | Falsches/zu altes Image. `docker rmi ghcr.io/bartlmac/portxlpy:<tag> && docker pull ghcr.io/bartlmac/portxlpy:<tag>` → **Rebuild Container**. |
| **`ModuleNotFoundError` nach Code-Änderung**    | **F1 → Dev Containers: Rebuild Container** (baut neu, installiert Abhängigkeiten).                                                            |
| **Container beendet sich sofort**               | ENTRYPOINT läuft durch. Mit Compose bereits gelöst; sonst beim Testen starten mit `--entrypoint /bin/bash -c "tail -f /dev/null"`.            |
| **Auto-Port-Forward-Popup (Port 4594)**         | In `.devcontainer/devcontainer.json`: `"portsAttributes": { "4594": { "onAutoForward": "ignore" } }"`.                                        |
| **Neues Tag wird nicht gepullt**                | Altes lokales Image blockiert. `docker rmi ghcr.io/bartlmac/portxlpy:<tag>` danach `docker pull ghcr.io/bartlmac/portxlpy:<tag>`.             |
| **`docker` im Container nicht gefunden**        | Docker-Befehle **auf dem Host** ausführen (PowerShell/Terminal). Optional: Feature `docker-outside-of-docker` nutzen.                         |
| **„name is already in use“**                    | Vorhandenen Container löschen/umbenennen: `docker rm -f portxlpy-seminar` oder `docker rename <alt> portxlpy-seminar`.                        |
| **Bild belegt viel Platz**                      | Unbenötigte Images entfernen: `docker image prune -a` *(Vorsicht: löscht alle ungenutzten Images!)*                                           |


---

### 8 · Aufräumen

```bash
# Container beenden & löschen
docker ps -a                                 # Container‑ID nachschlagen
docker ps -a \
  --format "table {{.Names}}\t{{.ID}}\t{{.Status}}"
                                             # (optional) oder so aufgehübscht
docker stop <ID>                             # Zuerst stoppen (ID oder Name, beides geht)
docker rm <ID>                               # Löschen (dito)

# Unbenutzte Images entfernen
docker image prune -a
```

---

## Lizenz
*DAV*

---

**Kontakt:**  
*Bartlomiej Maciaga* – <bartlomiej.maciaga@hotmail.com>  
*Dr. Arno Rasch*      – <arno.rasch@vtmw.de>  

Fragen oder Feedback gerne als GitHub‑Issue oder per E‑Mail.
