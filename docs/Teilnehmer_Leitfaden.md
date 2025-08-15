
# Teilnehmerleitfaden – Webinar „Excel‑Tarifrechner → Python“

## Teilnahmeformen

| Typ | Umgebung | Voraussetzungen |
|-----|----------|-----------------|
| **A (Zuschauen)** | Live‑Stream / Teams | Keine |
| **B (Codespaces)** | VS Code im **Browser** | GitHub‑Account |
| **C (Docker + VS Code Desktop)** | Lokaler Dev‑Container | Docker Desktop, VS Code, Git |

---

## B – GitHub Codespaces (Browser‑IDE)

1. Repository öffnen → **Code ▸ Codespaces ▸ Create**  
2. ~60 s warten → VS Code‑Web startet.  
3. Terminalbefehle (Beispiel):  
   ```bash
   pytest -q
   python Bartek/output/run_calc.py --help
   ```

---

## C – Lokale Variante (Docker Desktop + VS Code)

### 1 · Software installieren

| Tool | URL |
|------|-----|
| **Docker Desktop** | <https://docs.docker.com/get-docker/> |
| **Visual Studio Code** | <https://code.visualstudio.com/> |
| **Dev Containers‑Extension** | Marketplace ID `ms-vscode-remote.remote-containers` |
| **Git CLI** | <https://git-scm.com/downloads> |

### 2 · Projekt einrichten

```powershell
git clone https://github.com/bartlmac/portxlpy.git
cd portxlpy
code .
```

*In VS Code:* **F1 ▸ “Dev Containers: Reopen in Container”**  
→ Image `ghcr.io/bartlmac/portxlpy:seminar-202507` wird geladen.  
→ Container **portxl-seminar** startet automatisch, Workspace = `/workspace` wird automatisch gesetzt.  

### 3 · Smoke‑Test

```bash
pytest -q          # Erwartet: 4 passed
```

#### Troubleshooting (nur Docker Desktop)

* **Symptom:** VS Code meldet beim *Reopen in Container* `docker inspect … exit 1`  
  → Ursache: Ein veraltetes Seminar‑Image liegt noch lokal und blockiert den Pull.  
  **Lösung:**  
  ```powershell
  docker rmi ghcr.io/bartlmac/portxlpy:<altes‑Tag>
  ```
  Danach *Reopen in Container* erneut ausführen.

---

## Kontakt

| Name | E-Mail | GitHub |
|------|--------|--------|
| Bartlomiej Maciaga | bartlomiej.maciaga@hotmail.com | @bartlmac |
| Arno Rasch | arno.rasch@vtmw.de | @arnorasch |

*Stand: 04.07.2025*
