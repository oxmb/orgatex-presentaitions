# Firmware-Split Vertriebspräsentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the 7-slide decision deck `presentations/fw-split-vertrieb.md` with two ThingsBoard-style mockups and wire it into the existing Pandoc build.

**Architecture:** Two HTML mockups (`ota-dashboard.html`, `feature-flags.html`) styled with a new `tb-mockup.css` (ThingsBoard dark theme, distinct from the existing Slack-style `mockup.css`). Mockups are rendered to PNG via the existing `scripts/build-mockups.py` pipeline. The slide deck references those PNGs and is built to PPTX by the existing Pandoc Makefile target.

**Tech Stack:** HTML/CSS for mockups, headless Chromium + ImageMagick (via `scripts/build-mockups.py`), Pandoc Markdown for slides, GNU Make.

## Global Constraints

- All German text must use real Umlaute (ä/ö/ü/ß), never ae/oe/ue/ss.
- No em-dashes; use a hyphen or colon instead.
- Mockup HTML files live in `assets/mockups/`, CSS alongside them.
- Slide Markdown lives in `presentations/`.
- Image paths in Markdown are relative to the project root (where `make` is invoked), e.g. `assets/mockups/ota-dashboard.png`.
- The Makefile must be extended so `output/fw-split-vertrieb.pptx` rebuilds when its mockup PNGs change.
- Run `make` from the project root to build everything.

---

### Task 1: ThingsBoard CSS

**Files:**
- Create: `assets/mockups/tb-mockup.css`

**Interfaces:**
- Produces: CSS classes used by both mockup HTML files (Tasks 2 and 3): `.tb-card`, `.tb-card-header`, `.tb-footer`, `table`, `thead th`, `tbody td`, `.badge`, `.badge-ok`, `.badge-update`, `.btn-update`, `.attr-row`, `.attr-key`, `.attr-val`, `.attr-val.false`, `.attr-val.true`

- [ ] **Step 1: Create the CSS file**

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: Roboto, "Segoe UI", Arial, sans-serif;
  background: #1b2035;
  width: 900px;
  color: #eceff1;
}
.tb-card {
  background: #263047;
  border-radius: 4px;
  margin: 24px 28px;
  overflow: hidden;
}
.tb-card-header {
  padding: 14px 20px;
  font-size: 14px;
  font-weight: 500;
  color: #90a4ae;
  border-bottom: 1px solid #1b2035;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
thead th {
  padding: 10px 20px;
  text-align: left;
  color: #90a4ae;
  font-weight: 500;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  background: #1e2d40;
}
tbody tr { border-top: 1px solid #1b2035; }
tbody td { padding: 12px 20px; color: #cfd8dc; }
.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}
.badge-ok { background: #1b3a2a; color: #43a047; }
.badge-update { background: #3a2e00; color: #ffc107; }
.btn-update {
  padding: 6px 14px;
  background: #305680;
  color: #fff;
  border: none;
  border-radius: 3px;
  font-size: 13px;
  cursor: pointer;
}
.tb-footer {
  padding: 12px 20px;
  font-size: 12px;
  color: #78909c;
  border-top: 1px solid #1b2035;
  line-height: 1.5;
}
.attr-row {
  display: flex;
  padding: 10px 20px;
  border-top: 1px solid #1b2035;
  font-size: 14px;
}
.attr-key { width: 240px; color: #90a4ae; font-weight: 500; }
.attr-val { color: #cfd8dc; }
.attr-val.false { color: #ef5350; }
.attr-val.true { color: #43a047; }
```

- [ ] **Step 2: Commit**

```bash
git add assets/mockups/tb-mockup.css
git commit -m "feat: add ThingsBoard dark theme CSS for fw-split mockups"
```

---

### Task 2: OTA-Dashboard Mockup

**Files:**
- Create: `assets/mockups/ota-dashboard.html`
- Generates: `assets/mockups/ota-dashboard.png` (via build)

**Interfaces:**
- Consumes: `assets/mockups/tb-mockup.css` (Task 1)
- Produces: `assets/mockups/ota-dashboard.png` referenced in slide 4

- [ ] **Step 1: Create the HTML file**

```html
<!doctype html>
<html lang="de">
<head><meta charset="utf-8"><link rel="stylesheet" href="tb-mockup.css"></head>
<body>
  <div class="tb-card">
    <div class="tb-card-header">Firmware-Updates</div>
    <table>
      <thead>
        <tr>
          <th>Gerätename</th>
          <th>Seriennummer</th>
          <th>Aktuelle Version</th>
          <th>Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>OX-Label-0042</td>
          <td>SN-2024-0042</td>
          <td>1.2.1</td>
          <td><span class="badge badge-ok">Aktuell</span></td>
          <td></td>
        </tr>
        <tr>
          <td>OX-Label-0051</td>
          <td>SN-2024-0051</td>
          <td>1.1.8</td>
          <td><span class="badge badge-update">Update verfügbar</span></td>
          <td><button class="btn-update">Jetzt aktualisieren</button></td>
        </tr>
        <tr>
          <td>OX-Button-0003</td>
          <td>SN-2024-0003</td>
          <td>0.9.4</td>
          <td><span class="badge badge-ok">Aktuell</span></td>
          <td></td>
        </tr>
      </tbody>
    </table>
    <div class="tb-footer">
      Geräte prüfen beim nächsten OTA-Intervall automatisch auf Updates.
      Sofortige Aktualisierung: Gerät 10 Sekunden lang gedrückt halten.
    </div>
  </div>
</body>
</html>
```

- [ ] **Step 2: Build and verify the PNG**

```bash
python3 scripts/build-mockups.py assets/mockups/ota-dashboard.html
```

Expected: `wrote assets/mockups/ota-dashboard.png`. Open the PNG and verify:
- Dark background visible
- Three-row device table with correct content
- Middle row shows yellow "Update verfügbar" badge and "Jetzt aktualisieren" button
- Footer text about OTA interval and 10-second reset visible

- [ ] **Step 3: Commit**

```bash
git add assets/mockups/ota-dashboard.html assets/mockups/ota-dashboard.png
git commit -m "feat: add OTA dashboard mockup for fw-split deck"
```

---

### Task 3: Feature-Flag Panel Mockup

**Files:**
- Create: `assets/mockups/feature-flags.html`
- Generates: `assets/mockups/feature-flags.png` (via build)

**Interfaces:**
- Consumes: `assets/mockups/tb-mockup.css` (Task 1)
- Produces: `assets/mockups/feature-flags.png` referenced in slide 5

- [ ] **Step 1: Create the HTML file**

```html
<!doctype html>
<html lang="de">
<head><meta charset="utf-8"><link rel="stylesheet" href="tb-mockup.css"></head>
<body>
  <div class="tb-card">
    <div class="tb-card-header">Server-Attribute - OX-Button-0003</div>
    <div class="attr-row">
      <div class="attr-key">product_type</div>
      <div class="attr-val">ox_button</div>
    </div>
    <div class="attr-row">
      <div class="attr-key">label_api_enabled</div>
      <div class="attr-val false">false</div>
    </div>
    <div class="attr-row">
      <div class="attr-key">button_flow_enabled</div>
      <div class="attr-val true">true</div>
    </div>
    <div class="tb-footer">
      Feature-Flags werden vor dem Claiming zugewiesen.
      Eine Änderung wirkt sofort - ohne OTA-Update.
    </div>
  </div>
</body>
</html>
```

- [ ] **Step 2: Build and verify the PNG**

```bash
python3 scripts/build-mockups.py assets/mockups/feature-flags.html
```

Expected: `wrote assets/mockups/feature-flags.png`. Open the PNG and verify:
- Dark background
- Three attribute rows with correct keys and values
- `label_api_enabled` value shown in red (`false`)
- `button_flow_enabled` value shown in green (`true`)
- Footer text about zero-OTA flag change visible

- [ ] **Step 3: Commit**

```bash
git add assets/mockups/feature-flags.html assets/mockups/feature-flags.png
git commit -m "feat: add feature-flag panel mockup for fw-split deck"
```

---

### Task 4: Slide Deck Markdown

**Files:**
- Create: `presentations/fw-split-vertrieb.md`

**Interfaces:**
- Consumes: `assets/mockups/ota-dashboard.png` (Task 2), `assets/mockups/feature-flags.png` (Task 3)
- Produces: source for `output/fw-split-vertrieb.pptx`

- [ ] **Step 1: Create the slide deck**

```markdown
---
title: "OX-Label und OX-Button: Firmware-Strategie"
subtitle: "Entscheidungsgrundlage für den Vertrieb"
author: Manoel Brunnen
date: 2026-07-01
---

## Ausgangslage

- Gleiche Hardware (nRF9151) für OX-Label und OX-Button
- Produktidentität entsteht erst durch Firmware und Cloud-Konfiguration
- Aktuell: eine gemeinsame Firmware mit Feature-Flags für beide Produkte
- Frage: Weiter so, oder sauber trennen?

## Was braucht welches Produkt?

- OX-Label: API-Abfrage (Inhalt vom Server) und Button-Flow
- OX-Button: nur Button-Flow
- Beide Produkte benötigen Onboarding über ThingsBoard (Claiming und OTA)

## Szenario A: Getrennte Firmwares

- Zwei unabhängige Firmware-Produkte: ox-label und ox-button
- Je ein eigenes ThingsBoard Device Profile mit eigenem OTA-Kanal
- Gerät erhält beim Onboarding das produktspezifische Firmware-Image via OTA
- Upgrade Button auf Label: neues OTA-Image erforderlich
- Jede Firmware enthält nur die eigenen Features (kein ungenutzter Code der anderen Produktlinie)

## Szenario A: OTA-Flow

::: columns
:::: column
- Kunde kauft OX-Label oder OX-Button
- Onboarding: Claiming über ThingsBoard
- OTA-Dashboard zeigt verfügbares Firmware-Update an
- Gerät lädt Firmware beim nächsten OTA-Intervall
- Sofortige Aktualisierung: Gerät 10 Sekunden lang gedrückt halten
::::
:::: column
![](assets/mockups/ota-dashboard.png)
::::
:::

## Szenario B: Kombinierte Firmware

::: columns
:::: column
- Eine Firmware für beide Produkte
- ThingsBoard Server-Attribute (Feature-Flags) schalten Funktionen an oder ab
- OX-Label: API und Button aktiv
- OX-Button: nur Button aktiv
- Upgrade Button auf Label: Flag-Änderung in ThingsBoard reicht, kein OTA
::::
:::: column
![](assets/mockups/feature-flags.png)
::::
:::

## Vergleich

| Kriterium | A: Getrennte Firmwares | B: Kombiniert + Flags |
|---|---|---|
| Wartungsaufwand | Zwei separate Produkte zu pflegen | Ein Codebase, aber Flag-Komplexität |
| Flexibilität | Kein spontaner Upgrade ohne OTA | Flag-Wechsel reicht für Upgrade |
| Kundenerfahrung | OTA beim Onboarding nötig | Kein OTA-Schritt beim Onboarding |
| Time-to-Market | Besser: Fokus auf wichtigere FW, keine Projektabhängigkeiten | Schlechter: jede Änderung muss beide Use Cases berücksichtigen |

## Zur Entscheidung

- **Szenario A wählen wenn:** Entwicklungsfokus und saubere Produkttrennung wichtiger als Zero-Touch-Upgrade
- **Szenario B wählen wenn:** Einfacher Upgrade-Pfad Button auf Label und kein OTA beim Onboarding oberste Priorität
```

- [ ] **Step 2: Commit**

```bash
git add presentations/fw-split-vertrieb.md
git commit -m "feat: add fw-split sales deck slides"
```

---

### Task 5: Makefile Dependency

**Files:**
- Modify: `Makefile`

**Interfaces:**
- Consumes: `assets/mockups/ota-dashboard.png`, `assets/mockups/feature-flags.png` (Tasks 2-3)
- Produces: `output/fw-split-vertrieb.pptx` rebuilds when those PNGs change

- [ ] **Step 1: Add dependency lines**

In `Makefile`, after the existing `output/hermes-vertrieb.pptx: $(MOCKUPS_PNG)` line, add two lines: the deck dependency and explicit rules for the TB mockup PNGs that include `tb-mockup.css` as a dependency (the generic `%.png` rule only lists `mockup.css`):

```makefile
output/fw-split-vertrieb.pptx: assets/mockups/ota-dashboard.png assets/mockups/feature-flags.png

assets/mockups/ota-dashboard.png: assets/mockups/ota-dashboard.html assets/mockups/tb-mockup.css scripts/build-mockups.py
	$(PYTHON) scripts/build-mockups.py $<

assets/mockups/feature-flags.png: assets/mockups/feature-flags.html assets/mockups/tb-mockup.css scripts/build-mockups.py
	$(PYTHON) scripts/build-mockups.py $<
```

These specific rules override the generic `%.png` pattern for the two TB mockups and add `tb-mockup.css` to their dependency list.

- [ ] **Step 2: Commit**

```bash
git add Makefile
git commit -m "build: wire fw-split deck mockup dependencies in Makefile"
```

---

### Task 6: Full Build and Verify

**Files:**
- Generates: `output/fw-split-vertrieb.pptx`

- [ ] **Step 1: Run the full build**

```bash
make
```

Expected output includes:
```
wrote assets/mockups/ota-dashboard.png
wrote assets/mockups/feature-flags.png
```
...and pandoc producing `output/fw-split-vertrieb.pptx` without errors.

- [ ] **Step 2: Verify the PPTX**

Open `output/fw-split-vertrieb.pptx` and confirm:
- 7 slides present
- Slide 4 ("Szenario A: OTA-Flow") shows the OTA dashboard mockup in the right column
- Slide 5 ("Szenario B: Kombinierte Firmware") shows the attribute panel mockup in the right column
- Slide 6 table renders correctly with all four comparison rows
- No missing images, no broken layout

- [ ] **Step 3: Commit**

```bash
git add output/fw-split-vertrieb.pptx
git commit -m "build: add fw-split-vertrieb deck output"
```
