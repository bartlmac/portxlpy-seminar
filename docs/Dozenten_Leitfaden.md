# Dozenten‑Leitfaden – Seminar‑Image bauen & veröffentlichen  

*Version: 15.08.2025*  
*(Repo **bartlmac/portxlpy**, Branch `docker‑seminar‑setup`)*

---

## 1 · Voraussetzungen
- GitHub‑Account (Push‑Rechte)
- Docker Desktop
- VS Code Desktop + **Dev Containers**‑Extension
- Git, Git CLI

---

## 2 · Lokaler Test

1. Repo öffnen: `code .`  
2. **F1 → Dev Containers: Reopen in Container**  
3. Im Container‑Terminal:
   ```bash
   pytest -q    # sollte „passed“ melden
   ```

---

## 3 · Neues Seminar‑Tag veröffentlichen (GHCR)
1. **Tag setzen & pushen**
   ```bash
   git tag -a seminar-<YYYYMM> -m "Seminar-Image <Monat/Jahr>"
   git push origin seminar-<YYYYMM>
   ```
   > Triggert den vorhandenen GitHub‑Actions‑Build; kein weiterer CI‑Code nötig.

2. **Tag im Compose setzen**  
   `.devcontainer/docker-compose.yml` →
   ```yaml
   services:
     seminar:
       image: ghcr.io/bartlmac/portxlpy:seminar-<YYYYMM>
   ```
   Commit & Push:
   ```bash
   git add .devcontainer/docker-compose.yml
   git commit -m "devcontainer: use image seminar-<YYYYMM>"
   git push
   ```

3. **Codespaces / lokal aktualisieren**  
   **F1 → Dev Containers: Rebuild Container** (zieht das neue Image).

---

## 4 · Veröffentlichung **prüfen**
1. **Actions**: Run „Build & Push Seminar Image“ ist **grün**.  
2. **GHCR (UI)** – Tag auf der Package-Seite unter **Tags** suchen:  
   `https://github.com/users/bartlmac/packages/container/package/portxlpy`  
3. **CLI‑Check (ohne Pull)**
   ```bash
   docker buildx imagetools inspect ghcr.io/bartlmac/portxlpy:seminar-<YYYYMM>
   ```
4. **Pull & Digest verifizieren**
   ```bash
   docker pull ghcr.io/bartlmac/portxlpy:seminar-<YYYYMM>
   docker inspect --format "{index .RepoDigests 0}" ghcr.io/bartlmac/portxlpy:seminar-<YYYYMM>
   ```
   *(zeigt `@sha256:…` → Tag ist in GHCR veröffentlicht).*

---

## 5 · One‑Pager
1. `F1 → Reopen in Container` → `pytest -q` ✔️  
2. `git tag -a seminar-<YYYYMM>` → `git push origin seminar-<YYYYMM>`  
3. Compose‑Image‑Tag anpassen → Commit & Push  
4. **Rebuild Container** (Codespaces & lokal)  
5. GHCR prüfen (Actions grün, Tag sichtbar, `imagetools inspect`).

