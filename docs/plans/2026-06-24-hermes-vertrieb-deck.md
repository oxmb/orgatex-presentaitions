# Hermes Sales-Pitch Deck Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render a branded ORGATEX PowerPoint deck that pitches the Hermes agent to sales, from a German markdown source with Slack-style chat mockups.

**Architecture:** The Pandoc pipeline already exists (`scripts/build-reference.py`, `scripts/check-reference.py`, `Makefile`, `pandoc/defaults.yaml`) and renders any `presentations/*.md` against a layout-renamed, GC-stripped ORGATEX reference. This plan adds only the Hermes-specific work: a HTML-to-PNG mockup renderer, four Slack-style chat mockups, the Makefile wiring for them, and the deck source. Pandoc runs from the repo root.

**Tech Stack:** existing: pandoc, python3, make. Added: headless chromium (mockup rendering), libreoffice (deck open-check).

## Pre-existing pipeline (do NOT rebuild)

These are already implemented and verified by `make check`; build on them, do not duplicate:

- `scripts/build-reference.py <template> <reference>` — renames the 7 layouts pandoc needs, keeps all 24 layouts (avoids a PowerPoint repair prompt), strips example content via reachability-GC, and strips embedded fonts (so the deck stays editable in PowerPoint for the web); the theme, master and branding media survive.
- `scripts/check-reference.py <reference> <smoke.md>` — OOXML integrity + zero-warning render + branding check.
- `Makefile` targets: `all`, `reference`, `check`, `clean`; rule `output/%.pptx: presentations/%.md $(REFERENCE) pandoc/defaults.yaml | output`.
- `pandoc/defaults.yaml`: `reference-doc: orgatex-reference.potx`, `slide-level: 2`.
- `presentations/smoke-test.md` (pipeline test fixture), `presentations/intelligence-architecture.md` (unrelated placeholder — leave untouched).

## Global Constraints

- All deck copy is **German with echte Umlaute** (ä, ö, ü, ß) - never ae/oe/ue/ss.
- **Never use em-dash** (—) or en-dash (–); use a hyphen (-) or colon.
- `slide-level: 2`: a level-1 heading (`#`) is a Section Header slide, level-2 (`##`) a content slide. The deck uses content slides throughout.
- **Column fences follow the repo convention:** outer `::: columns`, inner `:::: column` (four colons), as in `presentations/smoke-test.md`.
- **Image paths are root-relative** (`assets/mockups/x.png`), because the Makefile invokes pandoc from the repo root.
- Mockup style is **Slack**; chat dialogue is German; ORGATEX product names are real (LongLife Bodenmarkierung, Behälterkennzeichnung), customer names are fictional (Bauer GmbH, Klaus Müller).
- Generated artefacts are git-ignored: `orgatex-reference.potx`, `output/`. Committed: scripts, Makefile, `pandoc/defaults.yaml`, `assets/mockups/*.{html,css,png}`, `presentations/*.md`. The mockup PNGs are committed so building the deck does not require chromium; they are NOT removed by `make clean`.
- Commit messages: English, no ticket number, one topic per commit.

---

### Task 1: Baseline sanity check

**Files:** none (verification only).

**Interfaces:**
- Produces: confirmation that the existing pipeline is green before new work starts.

- [ ] **Step 1: Run the existing pipeline check**

Run: `make check`
Expected: ends with `ALL CHECKS PASSED` (builds the reference, renders the smoke deck with zero layout warnings, confirms branding). If it fails, stop and report — the pre-existing pipeline is broken and must be fixed before adding the deck.

---

### Task 2: Mockup renderer, shared CSS, Makefile wiring, first mockup

**Files:**
- Create: `scripts/build-mockups.py`
- Create: `scripts/test-mockups.sh`
- Create: `assets/mockups/mockup.css`
- Create: `assets/mockups/recherche.html`
- Modify: `Makefile`

**Interfaces:**
- Consumes: existing `Makefile` variable `PYTHON`.
- Produces: `scripts/build-mockups.py <file.html>` writes `<file>.png`; `make mockups` renders all mockups; `assets/mockups/recherche.png`.

- [ ] **Step 1: Write the failing test**

Create `scripts/test-mockups.sh`:

```bash
#!/usr/bin/env bash
# Render every mockup HTML and assert a non-trivial PNG is produced.
set -euo pipefail
make mockups
shopt -s nullglob
html=(assets/mockups/*.html)
if [ ${#html[@]} -eq 0 ]; then echo "FAIL: no mockup HTML found" >&2; exit 1; fi
for f in "${html[@]}"; do
  png="${f%.html}.png"
  if [ ! -s "$png" ]; then echo "FAIL: missing/empty $png" >&2; exit 1; fi
  bytes="$(wc -c < "$png")"
  if [ "$bytes" -lt 5000 ]; then echo "FAIL: $png suspiciously small ($bytes B)" >&2; exit 1; fi
done
echo "OK: all mockups rendered"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `chmod +x scripts/test-mockups.sh && scripts/test-mockups.sh`
Expected: FAIL - `make: *** No rule to make target 'mockups'` (target not added yet).

- [ ] **Step 3: Write the render script**

Create `scripts/build-mockups.py`:

```python
#!/usr/bin/env python3
"""Render one chat-mockup HTML file to a PNG of the same basename.

Usage: build-mockups.py <file.html>

Uses headless Chromium so the chat layout is styled by ordinary CSS and the
German wording stays editable in the HTML source.
"""
import os
import subprocess
import sys


def main(html):
    png = os.path.splitext(html)[0] + ".png"
    subprocess.run([
        "chromium", "--headless=new", "--no-sandbox", "--hide-scrollbars",
        "--force-device-scale-factor=2", "--window-size=900,1400",
        "--default-background-color=FFFFFFFF",
        f"--screenshot={png}", "file://" + os.path.realpath(html),
    ], check=True)
    print("wrote", png)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: build-mockups.py <file.html>")
    main(sys.argv[1])
```

- [ ] **Step 4: Wire the Makefile**

After the `DECKS := ...` line, add the mockup variables:

```makefile
MOCKUPS_HTML := $(wildcard assets/mockups/*.html)
MOCKUPS_PNG  := $(patsubst %.html,%.png,$(MOCKUPS_HTML))
```

Change the `.PHONY` line to include `mockups`:

```makefile
.PHONY: all reference check mockups clean
```

Add this rule after the `reference:` rule block (recipe lines use a TAB):

```makefile
mockups: $(MOCKUPS_PNG)

assets/mockups/%.png: assets/mockups/%.html assets/mockups/mockup.css scripts/build-mockups.py
	$(PYTHON) scripts/build-mockups.py $<
```

Leave the `clean` target unchanged (committed PNGs must survive `make clean`).

- [ ] **Step 5: Write the shared CSS**

Create `assets/mockups/mockup.css`:

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: "Segoe UI", Helvetica, Arial, sans-serif;
  background: #ffffff;
  width: 900px;
  padding: 24px 28px;
  color: #1d1c1d;
}
.msg { display: flex; gap: 12px; padding: 10px 0; }
.avatar {
  width: 40px; height: 40px; border-radius: 8px; flex: 0 0 40px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; color: #fff; font-size: 16px;
}
.avatar.du { background: #4a154b; }
.avatar.hermes { background: #1264a3; }
.body { flex: 1; }
.head { display: flex; align-items: baseline; gap: 8px; }
.name { font-weight: 700; font-size: 15px; }
.time { color: #616061; font-size: 12px; }
.text { font-size: 15px; line-height: 1.46; margin-top: 2px; }
.text + .text { margin-top: 6px; }
```

- [ ] **Step 6: Write the first mockup HTML**

Create `assets/mockups/recherche.html`:

```html
<!doctype html>
<html lang="de">
<head><meta charset="utf-8"><link rel="stylesheet" href="mockup.css"></head>
<body>
  <div class="msg">
    <div class="avatar du">Du</div>
    <div class="body">
      <div class="head"><span class="name">Du</span><span class="time">09:42</span></div>
      <div class="text">Hermes, ich habe morgen um 10 Uhr einen Termin bei der Bauer GmbH. Fass mir kurz zusammen: Was macht die Firma, wer ist mein Ansprechpartner, gibt es Neuigkeiten?</div>
    </div>
  </div>
  <div class="msg">
    <div class="avatar hermes">H</div>
    <div class="body">
      <div class="head"><span class="name">Hermes</span><span class="time">09:42</span></div>
      <div class="text">Bauer GmbH, Maschinenbau aus Augsburg, rund 200 Mitarbeiter. Ansprechpartner laut CRM: Klaus Müller, Einkaufsleiter.</div>
      <div class="text">Aktuell: neue Produktionshalle eröffnet (Pressemitteilung letzte Woche), Expansion in die Lebensmittelbranche.</div>
      <div class="text">Tipp: stell den Bezug zur neuen Halle her - dort braucht es Bodenmarkierung und Behälterkennzeichnung.</div>
    </div>
  </div>
</body>
</html>
```

- [ ] **Step 7: Run the test to verify it passes**

Run: `chmod +x scripts/build-mockups.py && scripts/test-mockups.sh`
Expected: `OK: all mockups rendered`.

- [ ] **Step 8: Eyeball the render**

Open `assets/mockups/recherche.png`.
Expected: a clean Slack-style two-message exchange with correct umlauts, nothing clipped.

- [ ] **Step 9: Commit**

```bash
git add scripts/build-mockups.py scripts/test-mockups.sh assets/mockups/mockup.css assets/mockups/recherche.html assets/mockups/recherche.png Makefile
git commit -m "Add mockup renderer, shared style and research mockup"
```

---

### Task 3: Remaining three mockups

**Files:**
- Create: `assets/mockups/email.html`
- Create: `assets/mockups/posteingang.html`
- Create: `assets/mockups/antwort.html`

**Interfaces:**
- Consumes: `assets/mockups/mockup.css`, `scripts/build-mockups.py`, `scripts/test-mockups.sh` (Task 2).
- Produces: `email.png`, `posteingang.png`, `antwort.png`.

- [ ] **Step 1: Write the "E-Mails entwerfen" mockup**

Create `assets/mockups/email.html`:

```html
<!doctype html>
<html lang="de">
<head><meta charset="utf-8"><link rel="stylesheet" href="mockup.css"></head>
<body>
  <div class="msg">
    <div class="avatar du">Du</div>
    <div class="body">
      <div class="head"><span class="name">Du</span><span class="time">11:08</span></div>
      <div class="text">Hermes, entwirf eine Antwort an Herrn Müller von der Bauer GmbH. Er fragt nach einem Termin nächste Woche für die Angebotspräsentation.</div>
    </div>
  </div>
  <div class="msg">
    <div class="avatar hermes">H</div>
    <div class="body">
      <div class="head"><span class="name">Hermes</span><span class="time">11:08</span></div>
      <div class="text">Klar. Entwurf: "Sehr geehrter Herr Müller, vielen Dank für Ihre Nachricht. Für die Angebotspräsentation schlage ich Dienstag, den 30.06., um 14:00 Uhr vor. Passt Ihnen das? Mit freundlichen Grüßen ..."</div>
    </div>
  </div>
  <div class="msg">
    <div class="avatar du">Du</div>
    <div class="body">
      <div class="head"><span class="name">Du</span><span class="time">11:09</span></div>
      <div class="text">Mach es etwas lockerer.</div>
    </div>
  </div>
  <div class="msg">
    <div class="avatar hermes">H</div>
    <div class="body">
      <div class="head"><span class="name">Hermes</span><span class="time">11:09</span></div>
      <div class="text">"Hallo Herr Müller, danke für Ihre Nachricht! Wie wäre es mit Dienstag, 30.06., um 14 Uhr für die Präsentation? Sagen Sie gern Bescheid. Beste Grüße ..."</div>
    </div>
  </div>
</body>
</html>
```

- [ ] **Step 2: Write the "Posteingang-Zusammenfassung" mockup**

Create `assets/mockups/posteingang.html`:

```html
<!doctype html>
<html lang="de">
<head><meta charset="utf-8"><link rel="stylesheet" href="mockup.css"></head>
<body>
  <div class="msg">
    <div class="avatar du">Du</div>
    <div class="body">
      <div class="head"><span class="name">Du</span><span class="time">08:01</span></div>
      <div class="text">Was ist heute früh wichtig im Posteingang?</div>
    </div>
  </div>
  <div class="msg">
    <div class="avatar hermes">H</div>
    <div class="body">
      <div class="head"><span class="name">Hermes</span><span class="time">08:01</span></div>
      <div class="text">3 von 14 Mails brauchen dich heute:</div>
      <div class="text">1) Bauer GmbH bestätigt Termin Di 14 Uhr.</div>
      <div class="text">2) Frau Schmidt (Meier KG) bittet um ein aktualisiertes Angebot bis Freitag.</div>
      <div class="text">3) Buchhaltung: Reisekostenabrechnung Mai fehlt noch.</div>
      <div class="text">Der Rest sind Newsletter und CCs, das kann warten.</div>
    </div>
  </div>
</body>
</html>
```

- [ ] **Step 3: Write the "Schnelle Antworten unterwegs" mockup**

Create `assets/mockups/antwort.html`:

```html
<!doctype html>
<html lang="de">
<head><meta charset="utf-8"><link rel="stylesheet" href="mockup.css"></head>
<body>
  <div class="msg">
    <div class="avatar du">Du</div>
    <div class="body">
      <div class="head"><span class="name">Du</span><span class="time">13:24</span></div>
      <div class="text">Kunde fragt gerade: Hält die LongLife Bodenmarkierung auch dauerhaften Staplerverkehr aus? Schnell bitte!</div>
    </div>
  </div>
  <div class="msg">
    <div class="avatar hermes">H</div>
    <div class="body">
      <div class="head"><span class="name">Hermes</span><span class="time">13:24</span></div>
      <div class="text">Ja, genau dafür ist LongLife gemacht: abriebfest, für Stapler- und Routenzugverkehr ausgelegt.</div>
      <div class="text">Soll ich dir das Datenblatt schicken?</div>
    </div>
  </div>
</body>
</html>
```

- [ ] **Step 4: Render and verify all four**

Run: `scripts/test-mockups.sh`
Expected: `OK: all mockups rendered` (now four PNGs).

- [ ] **Step 5: Eyeball each render**

Open `assets/mockups/email.png`, `posteingang.png`, `antwort.png`.
Expected: readable Slack-style threads, correct umlauts, no clipped text.

- [ ] **Step 6: Commit**

```bash
git add assets/mockups/email.html assets/mockups/email.png \
        assets/mockups/posteingang.html assets/mockups/posteingang.png \
        assets/mockups/antwort.html assets/mockups/antwort.png
git commit -m "Add email, inbox and quick-answer mockups"
```

---

### Task 4: Deck source, Makefile dependency, render and verification

**Files:**
- Create: `presentations/hermes-vertrieb.md`
- Create: `scripts/test-deck.sh`
- Modify: `Makefile`

**Interfaces:**
- Consumes: the existing pipeline (reference + defaults), all four mockup PNGs (Tasks 2-3).
- Produces: `output/hermes-vertrieb.pptx`.

- [ ] **Step 1: Write the failing test**

Create `scripts/test-deck.sh`:

```bash
#!/usr/bin/env bash
# Build the Hermes deck, assert zero layout warnings, that ORGATEX branding
# media survives into the output, that no fonts are embedded (the pipeline
# strips them so the deck stays editable in PowerPoint for the web), and that
# LibreOffice can open it.
set -euo pipefail
err="$(make output/hermes-vertrieb.pptx 2>&1 >/dev/null || true)"
if grep -qi "Couldn't find layout" <<<"$err"; then
  echo "FAIL: layout warning(s):" >&2; echo "$err" >&2; exit 1
fi
[ -s output/hermes-vertrieb.pptx ] || { echo "FAIL: no output" >&2; exit 1; }
work="$(mktemp -d)"; trap 'rm -rf "$work"' EXIT
unzip -q output/hermes-vertrieb.pptx -d "$work"
ls "$work/ppt/media/"* >/dev/null 2>&1 \
  || { echo "FAIL: no media (branding lost)" >&2; exit 1; }
if ls "$work/ppt/fonts/"*.fntdata >/dev/null 2>&1; then
  echo "FAIL: deck embeds fonts (must be stripped for web editability)" >&2; exit 1
fi
libreoffice --headless --convert-to pdf --outdir "$work" \
  output/hermes-vertrieb.pptx >/dev/null 2>&1
[ -s "$work/hermes-vertrieb.pdf" ] || { echo "FAIL: LibreOffice cannot open deck" >&2; exit 1; }
echo "OK: deck renders, branding intact, no embedded fonts, opens in LibreOffice"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `chmod +x scripts/test-deck.sh && scripts/test-deck.sh`
Expected: FAIL - `make` errors because `presentations/hermes-vertrieb.md` does not exist.

- [ ] **Step 3: Write the deck source**

Create `presentations/hermes-vertrieb.md`:

```markdown
---
title: "Hermes: Ein KI-Assistent für den Vertrieb"
subtitle: "Weniger Routine, mehr Zeit für den Kunden"
author: Manoel Brunnen
date: 2026-06-24
---

## Der Vertriebsalltag heute

- Viel unterwegs, wenig Zeit am Laptop
- Kundeninfos sind verstreut, Recherche kostet Zeit
- Der Posteingang läuft über, Antworten warten
- Die Routine frisst die Zeit, die dem Kunden gehört

## Was ist Hermes?

- Ein persönlicher KI-Assistent, erreichbar über euren Arbeits-Messenger (z. B. Slack) und E-Mail
- Merkt sich Kontext und euren Schreibstil
- Arbeitet auch, während ihr offline seid
- Eigene Instanz pro Person, kein gemeinsamer Dienst

## Kundenrecherche vor dem Termin

::: columns
:::: column
- Gleich beim Kunden, keine Zeit zur Vorbereitung
- Hermes liefert die Kurzfassung vorab: Firma, Ansprechpartner, Neuigkeiten
- Ergebnis: vorbereitet ins Gespräch, mit konkretem Aufhänger
::::
:::: column
![](assets/mockups/recherche.png)
::::
:::

## E-Mails entwerfen

::: columns
:::: column
- Antwort oder Angebot im eigenen Stil entwerfen lassen
- Auch vom Handy, in wenigen Sekunden
- Ihr prüft und sendet, Hermes liefert den ersten Entwurf
::::
:::: column
![](assets/mockups/email.png)
::::
:::

## Posteingang-Zusammenfassung

::: columns
:::: column
- Tägliche Kurzfassung: was ist wichtig, was kann warten
- Priorisierung schon vor der Durchsicht
- Weniger Zeit im Posteingang, kein Verpassen
::::
:::: column
![](assets/mockups/posteingang.png)
::::
:::

## Schnelle Antworten unterwegs

::: columns
:::: column
- Frage per Messenger oder Sprache, ohne Laptop
- Belastbare Produktauskunft direkt für den Kunden
- Antwort im Gespräch, nicht erst nach dem Termin
::::
:::: column
![](assets/mockups/antwort.png)
::::
:::

## Ihre Daten bleiben im Haus

- Läuft auf einem lokalen Modell auf unserem eigenen Server
- Kein externer Cloud-Anbieter, Kundendaten verlassen das Unternehmen nicht
- DSGVO-freundlich, genau dafür haben wir den lokalen KI-Stack gebaut

## Wofür würden SIE es nutzen?

- Welche Aufgaben kosten euch im Alltag am meisten Zeit?
- Wäre Slack als Kanal für euch okay, oder etwas anderes?
- Wie organisieren wir die Einrichtung pro Person?
```

- [ ] **Step 4: Add the deck-to-mockups dependency in the Makefile**

So the deck rebuilds when a mockup changes, add this prerequisite-only line (no recipe — it augments the existing pattern rule) after the `output/%.pptx` rule:

```makefile
output/hermes-vertrieb.pptx: $(MOCKUPS_PNG)
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `scripts/test-deck.sh`
Expected: `OK: deck renders, branding intact, no embedded fonts, opens in LibreOffice`.

- [ ] **Step 6: Eyeball the deck**

Open the PDF the test produced (or `output/hermes-vertrieb.pptx` in PowerPoint/LibreOffice).
Expected: ORGATEX branding (theme, layouts, media); title slide shows title + subtitle; four use-case slides show text left, mockup right; correct umlauts. The deck is well under 1 MB because fonts are stripped (it renders in Mundial where that font is installed, otherwise a fallback).

- [ ] **Step 7: Commit**

```bash
git add presentations/hermes-vertrieb.md scripts/test-deck.sh Makefile
git commit -m "Add Hermes sales-pitch deck source and end-to-end test"
```

---

## Self-Review

**Spec coverage:**
- Narrative Problem -> Lösung -> Vorschlag, 9 slides (title + 8 content), layout via `slide-level: 2`: Task 4 deck. ✓
- Four Slack mockups with verbatim German dialogue and real ORGATEX products: Tasks 2-3. ✓
- Asset pipeline (`assets/mockups/*.{html,png}`, `scripts/build-mockups.py`, `make mockups`): Task 2. ✓
- Reuses the existing reference pipeline rather than rebuilding it: Pre-existing pipeline section + Task 1 gate. ✓
- Authoring conventions (`slide-level: 2`, `::::` columns, front-matter title/subtitle, root-relative images): Global Constraints + Task 4. ✓
- Verification (zero layout warnings, branding intact, LibreOffice opens): Task 4 test. ✓
- Open items (no multi-tenancy on slides 2-3 and 9; Slack-not-yet-used; Chromium dependency): reflected in deck copy and Global Constraints. ✓

**Placeholder scan:** No TBD/TODO; every code and test step carries complete content.

**Type/name consistency:** Mockup basenames (`recherche`, `email`, `posteingang`, `antwort`) are identical across Tasks 2-3 and the Task 4 image references; image paths root-relative; Makefile variable `MOCKUPS_PNG` defined in Task 2 and reused in Task 4.
