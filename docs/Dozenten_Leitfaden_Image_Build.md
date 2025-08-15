
# Dozenten‑Leitfaden – Seminar‑Image bauen & veröffentlichen  
*Version: 15.08.2025*  
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
docker build -f .devcontainer/Dockerfile -t portxlpy:dev .
docker run -d --name portxl-dev `
  -v "${PWD}:/workspace" `
  --entrypoint /bin/bash portxlpy:dev -c `
  "tail -f /dev/null"
```

> **Hinweis (lokaler Test):** Das Seminar-Image besitzt einen `ENTRYPOINT` (z. B. `python Bartek/output/run_calc.py`), der nach der Ausgabe endet. Für lokale Tests überschreiben wir ihn mit `--entrypoint /bin/bash -c "tail -f /dev/null"`, damit der Container aktiv bleibt. Das Mount `-v "${PWD}:/workspace"` bindet dein lokales Repo ein. Danach per `docker exec -it portxl-dev bash` oder in VS Code über **Dev Containers: Attach to Running Container…** verbinden.  
> Windows/PowerShell: `${PWD}` verwenden und Zeilenumbrüche mit dem Backtick `` ` ``.  
> macOS/Linux: `$(pwd)` verwenden und Zeilenumbrüche mit `\`.


**VS Code Desktop**

1. *Command Palette → Dev Containers: Attach to Running Container…*  
2. Container **portxl-dev** auswählen.  
3. Schnelltest im Terminal:  
   ```bash
   pytest -q    # erwartet: 4 passed
   ```
4. Container entfernen: `docker rm -f portxl-dev`

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


## 6 · Prüfung (GHCR & lokal)

1. **GitHub Actions** – öffne den Run für dein Tag (z. B. `seminar-test3`) und prüfe, dass der Workflow **grün** ist.
2. **GHCR (UI)** – Tag auf der Package-Seite unter **Tags** suchen:  
   `https://github.com/users/bartlmac/packages/container/package/portxlpy`
3. **Registry-Check per CLI** – Manifest/Plattformen ohne Pull ansehen:
   ```powershell
   docker buildx imagetools inspect ghcr.io/bartlmac/portxlpy:seminar-test3
   ```
4. **Pull & Digest verifizieren**:
   ```powershell
   docker pull ghcr.io/bartlmac/portxlpy:seminar-test3
   docker inspect --format "{{index .RepoDigests 0}}" ghcr.io/bartlmac/portxlpy:seminar-test3
   ```
   *Es sollte ein `@sha256:…` Digest ausgegeben werden.*
5. **Lokaler Funktionstest (Container wach halten)**:
   ```powershell
   docker run -d --name portxl-test -p 8443:8443      --entrypoint /bin/bash ghcr.io/bartlmac/portxlpy:seminar-test3 -c "tail -f /dev/null"
   ```
   Danach in VS Code **Dev Containers: Attach to Running Container…** → `portxl-test`.
6. **Falls ein altes lokales Image stört (Pull klemmt)**:
   ```powershell
   docker rmi ghcr.io/bartlmac/portxlpy:seminar-test3
   docker pull ghcr.io/bartlmac/portxlpy:seminar-test3
   ```


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
