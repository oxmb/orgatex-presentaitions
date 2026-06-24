# ORGATEX presentations via pandoc

Date: 2026-06-24
Status: approved (design)

## Problem

The corporate `orgatex-template.potx` (16:9, full HD, 24 slide layouts, plus 27
embedded example slides) cannot be used as a pandoc reference document as-is.
Pandoc's pptx writer locates layouts by seven fixed English names:

- `Title Slide`
- `Section Header`
- `Title and Content`
- `Two Content`
- `Comparison`
- `Content with Caption`
- `Blank`

The ORGATEX template uses German layout names (`Titelfolie`, `Kapitel 1`,
`Titel und Inhalt`, `Zwei Inhalte`, ...), so pandoc finds none of them, emits
seven `Couldn't find layout` warnings, and silently falls back to its own plain
built-in layouts. The result carries no ORGATEX branding. The file extension is
irrelevant: pandoc already accepts a raw `.potx` as `--reference-doc`; only the
names are wrong.

## Goal

1. A reproducible, reviewable fix that produces a pandoc-compatible ORGATEX
   reference template, keeping branding intact.
2. A markdown-to-pptx build workflow so any markdown file renders to a branded
   ORGATEX deck.
3. A first real presentation (`intelligence-architecture`) authored in markdown,
   outlined together once the pipeline renders correctly.

## Approach

Markdown is the single authoring source. A transform script regenerates a
pandoc-compatible reference template from the original `.potx`; pandoc renders
each deck against it. The original `orgatex-template.potx` stays untouched and
authoritative.

```
orgatex-template.potx ──(build-reference.py)──▶ orgatex-reference.potx
                                                        │
presentations/*.md ──────────(pandoc)───────────────────┴──▶ output/*.pptx
```

### Why .potx for the reference

A pandoc reference document is, semantically, "slide layouts with no real
slides" - which is exactly what a PowerPoint template (`.potx`) is. Pandoc reads
it directly (verified: `--reference-doc=...potx` exits 0). Rendered decks remain
`.pptx`, because a finished presentation is not a template.

## Components

1. `scripts/build-reference.py` (Python 3 stdlib only: `zipfile`, `re`, `os`)
   - Unzips `orgatex-template.potx` into a working directory.
   - **Rename:** renames the seven layouts pandoc needs by editing only the
     `<p:cSld name="...">` attribute in the relevant `slideLayoutN.xml` files.
   - **Detach example content and embedded fonts from the part graph:** removes
     `<p:sldIdLst>`, `<p:notesMasterIdLst>` and `<p:embeddedFontLst>` (plus the
     `embedTrueTypeFonts`/`saveSubsetFonts` flags) from `presentation.xml`; drops
     the slide / notes / customXml / font relationships from
     `presentation.xml.rels`. All 24 layouts and the slide master are left
     untouched (see "Why all 24 layouts are kept"). Fonts are stripped on purpose
     (see "Why embedded fonts are stripped").
   - **Reachability GC:** keeps only parts reachable from `presentation.xml`
     through the relationship graph; deletes everything else. This is what makes
     the strip robust - it automatically sweeps orphans that directory-by-
     directory deletion misses (verified: it removed `theme2.xml`,
     `themeOverride1.xml`, and the now-unreferenced `.fntdata` font parts).
   - **Prune + re-zip:** drops `[Content_Types].xml` Override entries for deleted
     parts, then re-zips as `orgatex-reference.potx`.
   - Survivors: master, all 24 layouts, `theme1.xml`, the branding media they
     reference, and presentation properties. No embedded fonts.
     Result: ~0.4 MB reference; deck ~0.45 MB (from a 4.4 MB template).
2. `Makefile`
   - `make reference` - regenerate `orgatex-reference.potx` from the `.potx`.
   - `make output/<name>.pptx` - render `presentations/<name>.md`.
   - `make all` - build every deck under `presentations/`.
3. `pandoc/defaults.yaml`
   - Pins `reference-doc: orgatex-reference.potx`, `slide-level: 2`, output
     location, and any standard options.
4. `presentations/*.md` - the deck sources.

### Repository layout

```
orgatex-template.potx            committed (source of truth, untouched)
scripts/build-reference.py       committed
pandoc/defaults.yaml             committed
presentations/*.md               committed
Makefile                         committed
orgatex-reference.potx           git-ignored (generated)
output/*.pptx                    git-ignored (generated)
```

## Layout mapping

Verified against the template's placeholder structure.

| pandoc name          | ORGATEX layout       | layout # | match quality        |
|----------------------|----------------------|----------|----------------------|
| Title Slide          | Titelfolie           | 1        | exact (ctrTitle+sub) |
| Section Header       | Kapitel 1            | 3        | exact (title+sub)    |
| Title and Content    | Titel und Inhalt     | 8        | exact (title+body)   |
| Two Content          | Zwei Inhalte         | 10       | exact (title+2 body) |
| Comparison           | Zwei Inhalte_weiss   | 12       | close (title+2 body) |
| Content with Caption | Diagramm 1           | 13       | approximate          |
| Blank                | Nur Titel            | 16       | approximate          |

The first four are exact placeholder matches and cover the overwhelming majority
of real slides. The last three are pandoc fall-back layouts rarely triggered by
ordinary markdown; they are mapped to the closest ORGATEX variant.

Only seven layouts are renamed, but **all 24 layouts are kept** in the
reference. The original German names and full 24-layout set also remain in
`orgatex-template.potx` for normal PowerPoint use.

**Why all 24 layouts are kept (PowerPoint-repair lesson):** an earlier version
trimmed the reference to just the 7 renamed layouts. That broke the output:
pandoc fills any layout slot it expects but cannot find in the reference with
its own default layout, and it leaves those injected layouts **unregistered in
the slide master** (`sldLayoutIdLst` and the master's relationships). The result
is orphan layout parts in the rendered deck, which PowerPoint reports as corrupt
and silently "repairs". Keeping all 24 ORGATEX layouts, with the master's
`sldLayoutIdLst` intact, gives pandoc every layout slot it needs from a
fully consistent master, so it injects nothing and the deck is clean. The
validator enforces this: it asserts every layout part in the rendered deck is
registered in the master.

**Why embedded fonts are stripped (PowerPoint-web lesson):** the template embeds
its fonts (Mundial family + a stray Calibri), and an earlier version kept them
for portability. That made every generated deck open **read-only** in PowerPoint
for the web, which cannot edit a presentation containing embedded fonts; the
embedded-font binaries also triggered a repair in the desktop app. The build
therefore strips `embeddedFontLst`, the `embedTrueTypeFonts`/`saveSubsetFonts`
flags, and the font relationships; the GC then sweeps the `.fntdata` parts. The
deck still references Mundial through the theme, and Mundial is available in the
target environment (installed locally and as an organisation font in Microsoft
365), so it renders correctly and stays editable. The validator enforces this:
it asserts the rendered deck embeds no fonts. This drops the deck from ~3.6 MB
to ~0.45 MB. Trade-off: a deck opened where Mundial is not available falls back
to a substitute font; that is acceptable here and is the same behaviour as the
ORGATEX decks that already work in this environment.

## Authoring conventions

- `slide-level: 2`. A level-1 heading (`#`) starts a Section Header slide; a
  level-2 heading (`##`) starts a content slide.
- Title slide metadata via the pandoc title block (`% Title`, `% Author`,
  `% Date`) or a YAML front-matter block.
- Two-column slides via pandoc `::: {.columns}` / `::: {.column}` fenced divs,
  which map to the Two Content layout.

## First deck

`presentations/intelligence-architecture.md`. Content outlined together once the
pipeline renders a smoke-test deck with zero layout warnings. A minimal
placeholder deck proves the pipeline before real content exists.

## Testing / verification

- Run pandoc against the generated reference and confirm **zero**
  `Couldn't find layout` warnings.
- Run an integrity check on the generated reference: no dangling relationship
  targets, no `[Content_Types].xml` Override pointing at a missing part, every
  surviving part has a content type and an inbound reference (no orphans).
- Unzip an output deck and confirm its slide layouts carry ORGATEX names
  (branding present), not pandoc defaults. Reference ~0.4 MB, deck ~0.45 MB.
- Confirm every layout part in the rendered deck is registered in the slide
  master (no orphan layouts), so PowerPoint accepts the deck without repairing.
- Confirm the rendered deck embeds no fonts (`embeddedFontLst` absent, no
  `.fntdata` parts), so PowerPoint for the web keeps it editable.
- Render headless with LibreOffice to confirm the deck opens and displays in
  Mundial.

## Decided defaults

- Standard content layouts (`Titel und Inhalt`, `Zwei Inhalte`) are the
  workhorses; `_weiss` variants are reserved for Comparison.
- The reference keeps all 24 layouts, the master, the theme, and the branding
  media they reference. Example content (27 slides, charts, chart-backing Excel,
  notes, custom XML) and the embedded fonts are removed via reachability GC.
  Layouts are deliberately NOT trimmed - doing so makes pandoc inject
  unregistered default layouts that PowerPoint flags as corrupt (see "Why all 24
  layouts are kept"). Verified to render with zero warnings, pass the integrity
  check, and produce an orphan-free deck.
- Embedded fonts are stripped so decks stay editable in PowerPoint for the web
  (see "Why embedded fonts are stripped"). The deck references Mundial through
  the theme (scheme: Mundial Black major / Mundial Thin minor); Mundial is
  available in the target environment. The stray Calibri embed disappears with
  the rest of the fonts.
- The generated reference is git-ignored and regenerated via `make reference`;
  the binary is never the source of truth.

## Risks / open items

- PowerPoint itself cannot be exercised in this environment. The reference and
  decks are validated by OOXML integrity checks plus LibreOffice rendering as a
  proxy; a one-time manual open in PowerPoint is recommended before relying on
  the workflow.
- Decks rely on Mundial being available wherever they are opened (installed
  locally, or as a Microsoft 365 organisation font). On a machine without
  Mundial, text falls back to a substitute. Embedding the fonts to make decks
  self-contained is incompatible with editing in PowerPoint for the web, so it
  is intentionally not done.
- PowerPoint (desktop and web) shows a one-time "repaired" / "we found a problem
  with some content" prompt when opening these decks. **The deck opens and is
  fully editable afterwards** - this is accepted as benign and is not a defect to
  chase further. Evidence: PowerPoint's saved-back copy is byte-identical in part
  content to ours (only the zip wrapper and PowerPoint's own normalisation, e.g.
  adding `clrMapOvr`, differ); a plain no-SVG variant triggers the same prompt,
  so it is not caused by fonts (stripped), layout orphans (fixed), or SVG. It is
  PowerPoint's standard reaction to OOXML produced by a non-Office tool (pandoc).
  Do not re-investigate unless the deck becomes non-editable or content is lost.
