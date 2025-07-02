# Teilnehmerleitfaden – Webinar „Excel‑Tarifrechner → Python"

| Typ                                    | Teilnahmeform                                                                    | Erforderliche Vorbereitung                                                                    |
| -------------------------------------- | -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **A – Zuhörer\*innen**                 | Reines Zuschauen (keine Hands‑on‑Übungen)                                        | *Keine*. Sie verfolgen Demo & Diskussion im Meeting‑Tool.                                     |
| **B – Codespaces‑Nutzer\*innen**       | Arbeiten direkt im Browser in einem GitHub Codespace                             | GitHub‑Account; Repo‑Einladung akzeptieren                                                    |
| **C – Lokale Container‑Nutzer\*innen** | Klonen Repo **oder** Container direkt starten, arbeiten in VS Code‑Dev‑Container | Docker Desktop ≥ 24, VS Code ≥ 1.90 (Installer), „Dev Containers“-Extension, *(optional)* Git |

---

## Typ B – Arbeiten mit GitHub Codespaces

1. **Vor dem Seminar**

   1. GitHub‑Account anlegen (falls noch nicht vorhanden): [https://github.com/signup](https://github.com/signup)
   2. Einladung zum privaten Repo per Mail/Notification **akzeptieren**.

2. **Beim Seminarstart**

   1. Repo im Browser öffnen → grüner **Code‑Button → “Codespaces” → “Create codespace on main”**.
   2. Nach ca. 1 Minute steht eine VS‑Code‑ähnliche Web‑IDE bereit – alle Python‑Pakete sind bereits installiert.
   3. Terminal & Editor sind sofort nutzbar, z. B.:

      ```bash
      pytest -q          # Tests ausführen
      python Bartek/output/run_calc.py --help
      ```

3. **Container neu ziehen / Rebuild (bei Änderungen)**
   Codespaces nutzt das Docker‑Image, das in deiner *devcontainer.json* definiert ist – aktuell `ghcr.io/bartlmac/portxlpy:seminar-202507`.

   * **Erststart**: Liegt das Image noch nicht im Codespace‑Cache, wird es automatisch heruntergeladen (⏱ ≈ 1 Min.).
   * **Weitere Sessions**: Öffnest du denselben Codespace erneut, startet genau dieser vorhandene Container; es erfolgt **kein** erneuter Download.
   * **Updates**: Wenn

     1. dasselbe Tag (`seminar-202507`) neu gebaut wurde **oder**
     2. in `devcontainer.json` ein **neuer Tag** steht,
        führe **F1 → Codespaces: Rebuild Container** (oder Zahnrad → *Rebuild container*) aus.
        Codespaces beendet den alten Container, lädt das aktuelle Image und führt `postCreateCommand` erneut aus (hier: `pytest -q || true`).
        Gesamt­dauer: ≈ 1–2 Minuten.

4. **Vorteile**\*\*

   * Null Setup auf dem eigenen Rechner
   * Einheitliche Umgebung für alle

---

## Typ C – Lokale Container‑Variante (VS Code + Docker)

1. **Programme installieren**

   * [Docker Desktop](https://docs.docker.com/get-docker/) (Win/Mac) oder Docker Engine (Linux) ≥ 24.x
   * [Visual Studio Code](https://code.visualstudio.com/) ≥ 1.90 (System‑Installer)
   * VS Code‑Extension **„Dev Containers“** (`ms-vscode-remote.remote-containers`)
   * *(optional)* [Git](https://git-scm.com/downloads) für eigenen Clone/Commits

2. **Image vorab laden** *(spart Zeit im Webinar)*

   ```bash
   docker pull ghcr.io/bartlmac/portxlpy:seminar-202507
   ```

3. **Option A – Repo in Container‑Volume klonen (empfohlen)**

   * VS Code öffnen → **F1** → `Dev Containers: Clone Repository in Container Volume`
   * Repository‑URL eingeben: `https://github.com/<ORG>/<REPO>.git`
   * VS Code lädt Code in ein Docker‑Volume und startet den Container mit obigem Image.

4. **Option B – Laufenden Container anhängen**

   ```bash
   docker run -d --name portxlpy ghcr.io/bartlmac/portxlpy:seminar-202507
   ```

   * VS Code → **F1** → `Dev Containers: Attach to Running Container…` → `portxlpy` auswählen.

5. **Smoke‑Test im Container**

   ```bash
   pytest -q            # Ausgabe: 4 passed
   ```

**Vorteile**

* Einheitliche Umgebung identisch zu Codespaces.
* Keine lokale Python‑Installation nötig.
* Offline‑Arbeit nach vorherigem Image‑Pull möglich.

**Fallback**
Docker funktioniert nicht? → Nutze **Typ B** (Codespaces).

---

### Kontakt

| Name                   | E-Mail                                                                  | GitHub    |
| ---------------------- | ----------------------------------------------------------------------- | --------- |
| **Bartlomiej Maciaga** | [bartlomiej.maciaga@hotmail.com](mailto:bartlomiej.maciaga@hotmail.com) | bartlmac  |
| **Arno Rasch**         | [arno.rasch@vtmw.de](mailto:arno.rasch@vtmw.de)                         | arnorasch |

*Letztes Update: 2. Juli 2025*
