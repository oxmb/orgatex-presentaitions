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
orgatex-template.potx ──(build-reference.sh)──▶ orgatex-reference.potx
                                                        │
presentations/*.md ──────────(pandoc)───────────────────┴──▶ output/*.pptx
```

### Why .potx for the reference

A pandoc reference document is, semantically, "slide layouts with no real
slides" - which is exactly what a PowerPoint template (`.potx`) is. Pandoc reads
it directly (verified: `--reference-doc=...potx` exits 0). Rendered decks remain
`.pptx`, because a finished presentation is not a template.

## Components

1. `scripts/build-reference.sh`
   - Unzips `orgatex-template.potx` into a working directory.
   - Renames the seven layouts pandoc needs by editing only the
     `<p:cSld name="...">` attribute in the relevant `slideLayoutN.xml` files.
   - Re-zips the result as `orgatex-reference.potx`.
   - Nothing else is touched: media, embedded fonts, master, theme, and the
     example slides are left intact. Renaming the seven layouts is the entire
     fix.
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
scripts/build-reference.sh       committed
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

The transform renames only these seven layouts. The original German names remain
in `orgatex-template.potx` for normal PowerPoint use; only the generated
reference carries the English names.

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
- Unzip an output deck and confirm its slide layouts carry ORGATEX names
  (branding present), not pandoc defaults.
- Confirm the embedded Mundial fonts and ORGATEX media survive into the output
  (branding intact). Each deck is expected to be ~4 MB, dominated by the
  embedded fonts; this is intended.
- Render headless with LibreOffice to confirm the deck opens and displays in
  Mundial.

## Decided defaults

- Standard content layouts (`Titel und Inhalt`, `Zwei Inhalte`) are the
  workhorses; `_weiss` variants are reserved for Comparison.
- The transform renames layouts only; nothing is stripped. Investigation showed
  the 4.3 MB template is ~3.3 MB embedded Mundial fonts and <1 MB media, of
  which 16/18 files are branding the layouts reference. Only 2 media files are
  example-only, so stripping buys nothing and risks the design.
- Embedded Mundial fonts are kept so decks render in the correct typeface on any
  machine (portable, ~4 MB per deck). The template's font scheme is
  Mundial Black (major) / Mundial Thin (minor).
- The generated reference is git-ignored and regenerated via `make reference`;
  the binary is never the source of truth.

## Risks / open items

- The template embeds a stray `Calibri` alongside the Mundial family (likely a
  leftover from one text box). It is harmless and left in place; removing it is
  optional cleanup, not required.
- Each deck carries ~3.3 MB of embedded Mundial fonts by design. If lean decks
  are ever needed, font embedding could be stripped as a separate build variant;
  out of scope for this work.
