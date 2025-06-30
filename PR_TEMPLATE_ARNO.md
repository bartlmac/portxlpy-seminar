## ✨ Kurzfassung
* **Pfad‑Refactor** – Skripte laufen nun von jedem Arbeits­verzeichnis (`Path(__file__)` + `os.chdir`)
* **Pytest‑Integration** – JUnit‑XML unter `*/output/tests/pytest-results.xml`, optionaler HTML‑Report
* **Tests**
  * **Arno** – Excel‑vs‑Python‑Vergleich, DIFF‑Logs im XML
  * **Bartek** – Funktions‑Parity inkl. Cache‑Ausnahme, Dummy‑CSV‑Roundtrip
* **CI/Hilfsfiles** – neues `requirements.txt`, `.gitignore` filtert XML/HTML, README v0.02

---

## ✅ Was wurde geändert
| Bereich | Änderung |
|---------|----------|
| **Arno**   | Pfad‑Utility, Rückgabewert `compare_results.main()`, Autouse‑Fixture, DIFF‑Prints |
| **Bartek** | Autouse‑Fixture, Tabelle in `test_func_parity`, Cache‑Dokumentation |
| **Root**   | `requirements.txt` (pandas, openpyxl, xlwings, oletools, pytest, junit2html, pytest-html) |
| **Docs**   | README aktualisiert (CLI + Tests & Reports) |
| **Sonstiges** | `.gitignore` ignoriert Test‑Artefakte |

---

## 🔍 Test / Verify

```bash
# Arno
cd Arno/output && pytest -q

# Bartek
cd Bartek/output && pytest -q

# Optionaler HTML‑Report
junit2html output/tests/pytest-results.xml output/tests/report.html
start output/tests/report.html   # macOS: open, Linux: xdg-open
```

---

## 📝 Review‑Checkliste
- [ ] `pytest` grün unter Windows **und** Linux  
- [ ] XML‑Pfad korrekt (`output/tests/...`)  
- [ ] README‑Schritte funktionieren  
- [ ] Keine Berichte oder .xlsm-Dateien mit‑committet  

*Danke fürs Review 🙏*
