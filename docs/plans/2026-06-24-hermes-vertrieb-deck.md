# Hermes Sales-Pitch Deck Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render a branded ORGATEX PowerPoint deck that pitches the Hermes agent to sales, from a German markdown source with Slack-style chat mockups.

**Architecture:** A transform script renames seven layouts in the untouched `orgatex-template.potx` to the English names pandoc expects, producing a git-ignored reference template. A second script renders HTML chat mockups to PNG via headless Chromium. Pandoc renders `presentations/hermes-vertrieb.md` against the reference, embedding the mockups. A Makefile ties the three stages together.

**Tech Stack:** pandoc, bash, zip/unzip, headless chromium, libreoffice (verification), GNU make.

## Global Constraints

- All deck copy is **German with echte Umlaute** (ä, ö, ü, ß) - never ae/oe/ue/ss.
- **Never use em-dash** (—) or en-dash (–); use a hyphen (-) or colon.
- `slide-level: 2`: a level-1 heading (`#`) is a Section Header slide, level-2 (`##`) a content slide.
- Mockup style is **Slack**; chat dialogue is German; ORGATEX product names are real (LongLife Bodenmarkierung, Behälterkennzeichnung), customer names are fictional (Bauer GmbH, Klaus Müller).
- **Verified layout rename mapping** (match the exact quoted `<p:cSld name="...">` attribute):
  | German (in template) | English (in reference) |
  |-----------------------|------------------------|
  | `Titelfolie`          | `Title Slide`          |
  | `Kapitel 1`           | `Section Header`       |
  | `Titel und Inhalt`    | `Title and Content`    |
  | `Zwei Inhalte`        | `Two Content`          |
  | `Zwei Inhalte_weiss`  | `Comparison`           |
  | `Diagramm 1`          | `Content with Caption` |
  | `Nur Titel`           | `Blank`                |
- `orgatex-template.potx` is the untouched source of truth; never edit it.
- Generated artefacts are git-ignored: `orgatex-reference.potx`, `output/`. Committed: scripts, Makefile, `pandoc/defaults.yaml`, `assets/mockups/*.{html,css,png}`, `presentations/*.md`.
- Pandoc is invoked from the repo root; image paths in markdown are root-relative.
- Commit messages: English, no ticket number, one topic per commit.

---

### Task 1: Reference-template build script

**Files:**
- Create: `scripts/build-reference.sh`

**Interfaces:**
- Produces: executable `scripts/build-reference.sh` that reads `orgatex-template.potx` and writes `orgatex-reference.potx` in the repo root with the seven layouts renamed.

- [ ] **Step 1: Write the failing test**

Create `scripts/test-reference.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
scripts/build-reference.sh
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
unzip -q orgatex-reference.potx -d "$work"
for name in "Title Slide" "Section Header" "Title and Content" \
            "Two Content" "Comparison" "Content with Caption" "Blank"; do
  if ! grep -rqF "<p:cSld name=\"$name\"" "$work/ppt/slideLayouts/"; then
    echo "MISSING layout: $name" >&2
    exit 1
  fi
done
echo "OK: all seven pandoc layout names present"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `chmod +x scripts/test-reference.sh && scripts/test-reference.sh`
Expected: FAIL - `scripts/build-reference.sh: No such file or directory`.

- [ ] **Step 3: Write the build script**

Create `scripts/build-reference.sh`:

```bash
#!/usr/bin/env bash
# Regenerate a pandoc-compatible ORGATEX reference template by renaming the
# seven layouts pandoc locates by English name. The source .potx is untouched.
set -euo pipefail

src="orgatex-template.potx"
out="orgatex-reference.potx"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

unzip -q "$src" -d "$work"
layouts="$work/ppt/slideLayouts"

rename() { # $1 = German name, $2 = English name
  local f
  for f in "$layouts"/slideLayout*.xml; do
    sed -i "s/<p:cSld name=\"$1\"/<p:cSld name=\"$2\"/" "$f"
  done
}

rename "Titelfolie"         "Title Slide"
rename "Kapitel 1"          "Section Header"
rename "Titel und Inhalt"   "Title and Content"
rename "Zwei Inhalte"       "Two Content"
rename "Zwei Inhalte_weiss" "Comparison"
rename "Diagramm 1"         "Content with Caption"
rename "Nur Titel"          "Blank"

rm -f "$out"
( cd "$work" && zip -q -r -X "$OLDPWD/$out" . )
echo "Wrote $out"
```

Note: the trailing-quote anchor in `<p:cSld name="Zwei Inhalte"` prevents matching `Zwei Inhalte_weiss`; the same holds for `Titelfolie`/`Titelfolie 2` and `Titel und Inhalt`/`Titel und Inhalt_weiss`.

- [ ] **Step 4: Run the test to verify it passes**

Run: `chmod +x scripts/build-reference.sh && scripts/test-reference.sh`
Expected: `OK: all seven pandoc layout names present`.

- [ ] **Step 5: Confirm the source template is unchanged**

Run: `git status --porcelain orgatex-template.potx`
Expected: empty output (no modification to the source of truth).

- [ ] **Step 6: Commit**

```bash
git add scripts/build-reference.sh scripts/test-reference.sh
git commit -m "Add reference-template build script renaming pandoc layouts"
```

---

### Task 2: Pandoc defaults, Makefile, gitignore, pipeline smoke test

**Files:**
- Create: `pandoc/defaults.yaml`
- Create: `Makefile`
- Create: `.gitignore`

**Interfaces:**
- Consumes: `scripts/build-reference.sh`, `orgatex-reference.potx` (Task 1).
- Produces: `make reference`, `make mockups`, `make all`, `make clean`; `output/<name>.pptx` rule; `pandoc/defaults.yaml` pinning `reference-doc` and `slide-level: 2`.

- [ ] **Step 1: Write the failing test**

Create `scripts/test-pipeline.sh`:

```bash
#!/usr/bin/env bash
# Render a representative throwaway deck and assert pandoc emits no
# "Couldn't find layout" warning against the generated reference.
set -euo pipefail
make reference
tmp_md="$(mktemp --suffix=.md)"
tmp_pptx="$(mktemp --suffix=.pptx)"
trap 'rm -f "$tmp_md" "$tmp_pptx"' EXIT
cat > "$tmp_md" <<'EOF'
% Test
% Autor
% 2026-06-24

# Abschnitt

## Inhalt

- Punkt eins
- Punkt zwei

## Zwei Spalten

::: columns
::: column
links
:::
::: column
rechts
:::
:::
EOF
err="$(pandoc --defaults=pandoc/defaults.yaml -o "$tmp_pptx" "$tmp_md" 2>&1 >/dev/null || true)"
if grep -qi "Couldn't find layout" <<<"$err"; then
  echo "FAIL: pandoc could not find layouts:" >&2
  echo "$err" >&2
  exit 1
fi
echo "OK: pandoc found all layouts, no warnings"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `chmod +x scripts/test-pipeline.sh && scripts/test-pipeline.sh`
Expected: FAIL - `make: *** No rule to make target 'reference'` (no Makefile yet).

- [ ] **Step 3: Write `pandoc/defaults.yaml`**

```yaml
reference-doc: orgatex-reference.potx
slide-level: 2
```

- [ ] **Step 4: Write the `.gitignore`**

```gitignore
orgatex-reference.potx
output/
```

- [ ] **Step 5: Write the `Makefile`**

```makefile
TEMPLATE     := orgatex-template.potx
REFERENCE    := orgatex-reference.potx
SRCS         := $(wildcard presentations/*.md)
DECKS        := $(patsubst presentations/%.md,output/%.pptx,$(SRCS))
MOCKUPS_HTML := $(wildcard assets/mockups/*.html)
MOCKUPS_PNG  := $(patsubst %.html,%.png,$(MOCKUPS_HTML))

.PHONY: all reference mockups clean
all: $(DECKS)

reference: $(REFERENCE)
$(REFERENCE): $(TEMPLATE) scripts/build-reference.sh
	scripts/build-reference.sh

mockups: $(MOCKUPS_PNG)
assets/mockups/%.png: assets/mockups/%.html assets/mockups/mockup.css scripts/build-mockups.sh
	scripts/build-mockups.sh $<

output:
	mkdir -p output

output/%.pptx: presentations/%.md pandoc/defaults.yaml $(REFERENCE) $(MOCKUPS_PNG) | output
	pandoc --defaults=pandoc/defaults.yaml -o $@ $<

clean:
	rm -f $(REFERENCE) $(DECKS) $(MOCKUPS_PNG)
```

Note: Makefile recipe lines MUST be indented with a TAB, not spaces.

- [ ] **Step 6: Run the test to verify it passes**

Run: `scripts/test-pipeline.sh`
Expected: `OK: pandoc found all layouts, no warnings`.

- [ ] **Step 7: Commit**

```bash
git add pandoc/defaults.yaml Makefile .gitignore scripts/test-pipeline.sh
git commit -m "Add pandoc defaults, Makefile and pipeline smoke test"
```

---

### Task 3: Mockup rendering infrastructure, shared CSS, first mockup

**Files:**
- Create: `scripts/build-mockups.sh`
- Create: `assets/mockups/mockup.css`
- Create: `assets/mockups/recherche.html`

**Interfaces:**
- Consumes: `make mockups` rule (Task 2).
- Produces: `scripts/build-mockups.sh <file.html>` writes `<file>.png` via headless chromium; `assets/mockups/mockup.css` shared Slack styling; `assets/mockups/recherche.png`.

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
Expected: FAIL - `scripts/build-mockups.sh: No such file or directory` (via the make rule).

- [ ] **Step 3: Write the render script**

Create `scripts/build-mockups.sh`:

```bash
#!/usr/bin/env bash
# Render one chat-mockup HTML file to a PNG of the same basename.
set -euo pipefail
in="$1"
out="${in%.html}.png"
chromium --headless=new --no-sandbox --hide-scrollbars \
  --force-device-scale-factor=2 --window-size=900,1400 \
  --default-background-color=FFFFFFFF \
  --screenshot="$out" "file://$(realpath "$in")"
echo "Wrote $out"
```

- [ ] **Step 4: Write the shared CSS**

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

- [ ] **Step 5: Write the first mockup HTML**

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

- [ ] **Step 6: Run the test to verify it passes**

Run: `chmod +x scripts/build-mockups.sh && scripts/test-mockups.sh`
Expected: `OK: all mockups rendered`.

- [ ] **Step 7: Eyeball the render**

Run: `xdg-open assets/mockups/recherche.png` (or open it in any viewer).
Expected: a clean Slack-style two-message exchange with correct umlauts.

- [ ] **Step 8: Commit**

```bash
git add scripts/build-mockups.sh scripts/test-mockups.sh assets/mockups/mockup.css assets/mockups/recherche.html assets/mockups/recherche.png
git commit -m "Add mockup render script, shared style and research mockup"
```

---

### Task 4: Remaining three mockups

**Files:**
- Create: `assets/mockups/email.html`
- Create: `assets/mockups/posteingang.html`
- Create: `assets/mockups/antwort.html`

**Interfaces:**
- Consumes: `assets/mockups/mockup.css`, `scripts/build-mockups.sh`, `scripts/test-mockups.sh` (Task 3).
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

### Task 5: Deck markdown, render and branding verification

**Files:**
- Create: `presentations/hermes-vertrieb.md`

**Interfaces:**
- Consumes: the full pipeline (Tasks 1-2), all four mockup PNGs (Tasks 3-4).
- Produces: `output/hermes-vertrieb.pptx`.

- [ ] **Step 1: Write the failing test**

Create `scripts/test-deck.sh`:

```bash
#!/usr/bin/env bash
# Build the real deck, assert zero layout warnings, ORGATEX fonts/media
# survive into the output, and LibreOffice can open it.
set -euo pipefail
err="$(make output/hermes-vertrieb.pptx 2>&1 >/dev/null || true)"
if grep -qi "Couldn't find layout" <<<"$err"; then
  echo "FAIL: layout warning(s):" >&2; echo "$err" >&2; exit 1
fi
[ -s output/hermes-vertrieb.pptx ] || { echo "FAIL: no output" >&2; exit 1; }
work="$(mktemp -d)"; trap 'rm -rf "$work"' EXIT
unzip -q output/hermes-vertrieb.pptx -d "$work"
ls "$work/ppt/fonts/"*.fntdata >/dev/null 2>&1 \
  || { echo "FAIL: no embedded fonts (branding lost)" >&2; exit 1; }
ls "$work/ppt/media/"* >/dev/null 2>&1 \
  || { echo "FAIL: no media (branding lost)" >&2; exit 1; }
libreoffice --headless --convert-to pdf --outdir "$work" \
  output/hermes-vertrieb.pptx >/dev/null 2>&1
[ -s "$work/hermes-vertrieb.pdf" ] || { echo "FAIL: LibreOffice cannot open deck" >&2; exit 1; }
echo "OK: deck renders, branding intact, opens in LibreOffice"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `chmod +x scripts/test-deck.sh && scripts/test-deck.sh`
Expected: FAIL - `make` errors because `presentations/hermes-vertrieb.md` does not exist.

- [ ] **Step 3: Write the deck source**

Create `presentations/hermes-vertrieb.md`:

```markdown
% Hermes: Ein KI-Assistent für den Vertrieb
% ORGATEX
% 2026-06-24

## Weniger Routine, mehr Zeit für den Kunden

# Der Vertriebsalltag heute

## Was kostet uns Zeit?

- Viel unterwegs, wenig Zeit am Laptop
- Kundeninfos sind verstreut, Recherche kostet Zeit
- Der Posteingang läuft über, Antworten warten
- Die Routine frisst die Zeit, die dem Kunden gehört

# Die Lösung: Hermes

## Was ist Hermes?

- Ein persönlicher KI-Assistent, erreichbar über euren Arbeits-Messenger (z. B. Slack) und E-Mail
- Merkt sich Kontext und euren Schreibstil
- Arbeitet auch, während ihr offline seid
- Eigene Instanz pro Person, kein gemeinsamer Dienst

## Kundenrecherche vor dem Termin

::: columns
::: column
- Gleich beim Kunden, keine Zeit zur Vorbereitung
- Hermes liefert die Kurzfassung vorab: Firma, Ansprechpartner, Neuigkeiten
- Ergebnis: vorbereitet ins Gespräch, mit konkretem Aufhänger
:::
::: column
![](assets/mockups/recherche.png)
:::
:::

## E-Mails entwerfen

::: columns
::: column
- Antwort oder Angebot im eigenen Stil entwerfen lassen
- Auch vom Handy, in wenigen Sekunden
- Ihr prüft und sendet, Hermes liefert den ersten Entwurf
:::
::: column
![](assets/mockups/email.png)
:::
:::

## Posteingang-Zusammenfassung

::: columns
::: column
- Tägliche Kurzfassung: was ist wichtig, was kann warten
- Priorisierung schon vor der Durchsicht
- Weniger Zeit im Posteingang, kein Verpassen
:::
::: column
![](assets/mockups/posteingang.png)
:::
:::

## Schnelle Antworten unterwegs

::: columns
::: column
- Frage per Messenger oder Sprache, ohne Laptop
- Belastbare Produktauskunft direkt für den Kunden
- Antwort im Gespräch, nicht erst nach dem Termin
:::
::: column
![](assets/mockups/antwort.png)
:::
:::

# Ihre Daten bleiben im Haus

## Datenresidenz

- Läuft auf einem lokalen Modell auf unserem eigenen Server
- Kein externer Cloud-Anbieter, Kundendaten verlassen das Unternehmen nicht
- DSGVO-freundlich, genau dafür haben wir den lokalen KI-Stack gebaut

# Wofür würden SIE es nutzen?

## Eure Sicht zählt

- Welche Aufgaben kosten euch im Alltag am meisten Zeit?
- Wäre Slack als Kanal für euch okay, oder etwas anderes?
- Wie organisieren wir die Einrichtung pro Person?
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `scripts/test-deck.sh`
Expected: `OK: deck renders, branding intact, opens in LibreOffice`.

- [ ] **Step 5: Eyeball the deck**

Convert and open the PDF the test produced, or open `output/hermes-vertrieb.pptx` in PowerPoint/LibreOffice.
Expected: ORGATEX branding and Mundial typeface; four use-case slides show text left, mockup right; correct umlauts throughout; ~4 MB file size.

- [ ] **Step 6: Commit**

```bash
git add presentations/hermes-vertrieb.md scripts/test-deck.sh
git commit -m "Add Hermes sales-pitch deck source and end-to-end test"
```

---

## Self-Review

**Spec coverage:**
- Narrative Problem -> Lösung -> Vorschlag, 9 slides, layout mapping: Task 5 deck source. ✓
- Four Slack mockups with verbatim German dialogue and real ORGATEX products: Tasks 3-4. ✓
- Asset pipeline (`assets/mockups/*.html` + `*.png`, `scripts/build-mockups.sh`, `make mockups`): Tasks 2-3. ✓
- Reference pipeline dependency (build-reference, defaults, Makefile): Tasks 1-2. ✓
- Authoring conventions (`slide-level: 2`, `::: columns`, title block): Task 2 defaults, Task 5 deck. ✓
- Testing/verification (zero layout warnings, branding intact, LibreOffice opens): Tasks 2 and 5. ✓
- Open items (no multi-tenancy on slide 3 + slide 9; Slack-not-yet-used; Chromium dependency): reflected in deck copy and Global Constraints. ✓

**Placeholder scan:** No TBD/TODO; every code and test step carries complete content.

**Type/name consistency:** Layout names match the Global Constraints mapping across Task 1 script and test; mockup basenames (`recherche`, `email`, `posteingang`, `antwort`) are identical in Tasks 3-4 and the Task 5 image references; image paths are root-relative as required.
