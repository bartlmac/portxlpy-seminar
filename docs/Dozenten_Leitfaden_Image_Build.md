
# Dozenten‑Leitfaden – Seminar‑Image bauen & veröffentlichen  
*Version: 04.07.2025*  
*(Repository **bartlmac/portxlpy**, Branch `docker‑seminar‑setup`)*

---

## 1 · Voraussetzungen

| Tool / Konto | Zweck |
|--------------|-------|
| **GitHub‑Account** (Push‑Rechte) | Git‑Tags setzen, CI auslösen |
| **Docker Desktop** | Image lokal bauen & testen |
| **Git CLI** | Tagging & Push |
| **VS Code Desktop** + **Dev Containers‑Extension** | Container bequem attachen |

---

## 2 · Tag‑Namenskonvention

Seminar‑Tags folgen dem Muster **`seminar‑<YYYYMM>`**  
(z. B. `seminar‑202507`).  
*Tags niemals überschreiben – lieber `seminar‑202507b` anlegen.*

---

## 3 · Image lokal bauen & testen (ohne Browser)

```bash
git checkout docker-seminar-setup
docker build -t portxlpy:dev .
docker run -d --name portxl-test -v "$(pwd):/workspace" portxlpy:dev tail -f /dev/null
```

**VS Code Desktop**

1. *Command Palette → Dev Containers: Attach to Running Container…*  
2. Container **portxl-test** auswählen.  
3. Schnelltest im Terminal:  
   ```bash
   pytest -q    # erwartet: 4 passed
   ```
4. Container entfernen: `docker rm -f portxl-test`

---

## 4 · Git‑Tag setzen & pushen (lößt CI aus)

```bash
git tag -a seminar-202507 -m "Seminar‑Image Juli 2025"
git push origin seminar-202507
```

> **Hinweis:** Der CI‑Workflow `.github/workflows/build-docker.yml`  
> ist bereits im Repo und baut automatisch jedes `seminar-*`‑Tag.  
> **Kein weiterer Code erforderlich.**

---

## 5 · devcontainer.json auf neues Tag stellen

```jsonc
{
  "image": "ghcr.io/bartlmac/portxlpy:seminar-202507"
}
```

```bash
git add .devcontainer/devcontainer.json
git commit -m "devcontainer → seminar-202507"
git push origin docker-seminar-setup
```

---

## 6 · Prüfung

* **GitHub Actions**: Workflow grün  
* **GHCR**: Tag `seminar-202507` sichtbar  
* **Codespace**: Rebuild Container lädt neues Image  
* **Docker Desktop**:  
  ```bash
  docker pull ghcr.io/bartlmac/portxlpy:seminar-202507
  docker run -d -p 8443:8443 ghcr.io/bartlmac/portxlpy:seminar-202507 tail -f /dev/null
  ```
  → VS Code Desktop *Attach to Running Container…*

---

## 7 · One‑Page‑Checkliste

1. `git pull && git checkout docker-seminar-setup`
2. `docker build -t portxlpy:dev .` → Test OK  
3. `git tag -a seminar-<YYYYMM>` → `git push --tags`  
4. CI grün? Tag in GHCR?  
5. devcontainer.json auf neues Tag pushen  
6. Codespace **Rebuild** & Docker **Pull + Attach** testen  

> **Seminar ready!**
