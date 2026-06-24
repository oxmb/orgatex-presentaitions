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
   - **Detach example content from the part graph:** removes `<p:sldIdLst>` and
     `<p:notesMasterIdLst>` from `presentation.xml`; drops the slide / notes /
     customXml relationships from `presentation.xml.rels`; removes the 17 unused
     layouts from the slide master (`<p:sldLayoutId>` entries plus their
     relationships).
   - **Reachability GC:** keeps only parts reachable from `presentation.xml`
     through the relationship graph; deletes everything else. This is what makes
     the strip robust - it automatically sweeps orphans that directory-by-
     directory deletion misses (verified: it removed `theme2.xml` and
     `themeOverride1.xml`, which also eliminated the stray Calibri font for
     free).
   - **Prune + re-zip:** drops `[Content_Types].xml` Override entries for deleted
     parts, then re-zips as `orgatex-reference.potx`.
   - Survivors: master, the 7 kept layouts, `theme1.xml`, the 7 branding media
     they reference, the 14 embedded Mundial fonts, and presentation
     properties. Result: ~3.2 MB (from 4.4 MB).
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

Only these seven layouts are kept in the reference; the other 17 (which pandoc
can never auto-select by name) are dropped. The original German names and the
full 24-layout set remain in `orgatex-template.potx` for normal PowerPoint use;
only the generated reference is trimmed and carries the English names.

**Pandoc default-layout merge behaviour:** pandoc always injects approximately
11 of its own unbranded default layouts into every output deck and only
overrides those whose names match one of the seven names above. A rendered deck
therefore contains the 7 branded ORGATEX layouts plus pandoc's unbranded
defaults. Slides routed to one of pandoc's unmapped fallback layouts (e.g.
"Picture with Caption") will render unbranded, and pandoc emits no warning for
this. The 7 mappings cover all slide types produced by ordinary markdown; this
is a known limitation, not a bug.

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
  (branding present), not pandoc defaults, and that the embedded Mundial fonts
  survive (branding intact). Reference ~3.2 MB, deck ~3.2 MB, both dominated by
  the embedded fonts; this is intended.
- Render headless with LibreOffice to confirm the deck opens and displays in
  Mundial.

## Decided defaults

- Standard content layouts (`Titel und Inhalt`, `Zwei Inhalte`) are the
  workhorses; `_weiss` variants are reserved for Comparison.
- The reference is stripped to the minimum pandoc needs: 7 layouts, master,
  theme, the branding media those reference, and the embedded fonts. All example
  content (27 slides, charts, chart-backing Excel, notes, custom XML, the 17
  unused layouts and their media) is removed via reachability GC. Verified to
  render with zero warnings and pass the integrity check.
- Embedded Mundial fonts are kept so decks render in the correct typeface on any
  machine (portable). The template's font scheme is Mundial Black (major) /
  Mundial Thin (minor). The stray Calibri is removed as a side effect of the GC
  (it lived only in the discarded notes-master theme).
- The generated reference is git-ignored and regenerated via `make reference`;
  the binary is never the source of truth.

## Risks / open items

- PowerPoint itself cannot be exercised in this environment. The reference and
  decks are validated by OOXML integrity checks plus LibreOffice rendering as a
  proxy; a one-time manual open in PowerPoint is recommended before relying on
  the workflow.
- If lean (font-free) decks are ever needed for machines that have Mundial
  installed, font embedding could be stripped as a separate build variant; out
  of scope for this work.
