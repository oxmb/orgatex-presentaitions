# ORGATEX pandoc presentations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render markdown into ORGATEX-branded `.pptx` decks with pandoc, by generating a minimal pandoc-compatible reference template from `orgatex-template.potx`.

**Architecture:** A Python build script regenerates a stripped `orgatex-reference.potx` from the original template: it renames the 7 layouts pandoc addresses by name, detaches the example content, and garbage-collects every part unreachable from `presentation.xml`. Pandoc renders each `presentations/*.md` against that reference via a `Makefile`. The original `.potx` stays untouched and authoritative.

**Tech Stack:** Python 3 (standard library only), pandoc 3.x, GNU Make, LibreOffice (optional, for manual render checks). Reference and source spec: `docs/specs/2026-06-24-orgatex-pandoc-presentations-design.md`.

## Global Constraints

- Build script uses the Python 3 **standard library only** — no third-party packages (`zipfile`, `re`, `os`, `shutil`, `sys`, `tempfile`).
- Pandoc is invoked with `--slide-level=2` and `--reference-doc=orgatex-reference.potx`.
- The 7 kept layouts and their pandoc names are fixed: `slideLayout1`→`Title Slide`, `slideLayout3`→`Section Header`, `slideLayout8`→`Title and Content`, `slideLayout10`→`Two Content`, `slideLayout12`→`Comparison`, `slideLayout13`→`Content with Caption`, `slideLayout16`→`Blank`.
- Embedded Mundial fonts are kept (portable rendering). Font scheme: Mundial Black (major) / Mundial Thin (minor).
- `orgatex-reference.potx` and `output/` are git-ignored and always regenerated; never the source of truth.
- `orgatex-template.potx` is committed unchanged as the source of truth.
- German deck content: real Umlaute (ä/ö/ü/ß), no `ae/oe/ue/ss`; no em-dash.
- Commit messages in English.

---

### Task 1: Reference build script + validator

Produces the core fix: a script that turns the template into a pandoc-ready reference, and a validator that proves the result is structurally sound and renders branded. Includes `.gitignore` so the generated binary is never committed, and commits the template as source of truth.

**Files:**
- Create: `.gitignore`
- Create: `scripts/build-reference.py`
- Create: `scripts/check-reference.py`
- Create: `presentations/smoke-test.md`
- Commit (already present, untracked): `orgatex-template.potx`

**Interfaces:**
- Consumes: `orgatex-template.potx` (ORGATEX template, 24 layouts + 27 example slides).
- Produces:
  - `scripts/build-reference.py` — CLI `build-reference.py <template.potx> <reference.potx>`; writes the stripped reference, exits 0 on success.
  - `scripts/check-reference.py` — CLI `check-reference.py <reference.potx> <smoke-test.md>`; exits 0 only if integrity + zero-warning render + branding all pass, non-zero otherwise.
  - `presentations/smoke-test.md` — a deck exercising title / section / content / two-column slides.

- [ ] **Step 1: Create `.gitignore`**

```gitignore
/orgatex-reference.potx
/output/
```

- [ ] **Step 2: Write the validator `scripts/check-reference.py`**

```python
#!/usr/bin/env python3
"""Validate a generated ORGATEX pandoc reference.

Usage: check-reference.py <reference.potx> <smoke-test.md>

Checks:
  1. OOXML integrity: no dangling relationship targets, no [Content_Types]
     Override pointing at a missing part, every part has a content type and
     an inbound reference (no orphans).
  2. pandoc renders the smoke-test deck against the reference with zero
     "Couldn't find layout" warnings.
  3. the rendered deck carries the ORGATEX layout names (branding survived).

Exits non-zero on the first failure.
"""
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile


def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)


def read_rels(work, relpath, basedir):
    rp = os.path.join(work, relpath)
    if not os.path.exists(rp):
        return []
    out = []
    with open(rp, encoding="utf-8") as fh:
        body = fh.read()
    for m in re.finditer(r"<Relationship\b[^>]*/>", body):
        rel = m.group(0)
        if 'TargetMode="External"' in rel or 'Target="http' in rel:
            continue
        tgt = re.search(r'Target="([^"]*)"', rel)
        if tgt:
            out.append(os.path.normpath(
                os.path.join(basedir, tgt.group(1))).replace(os.sep, "/"))
    return out


def integrity(ref):
    work = tempfile.mkdtemp(prefix="ox-check-")
    try:
        with zipfile.ZipFile(ref) as z:
            z.extractall(work)

        def exists(part):
            return os.path.exists(os.path.join(work, part.lstrip("/")))

        # 1. dangling relationship targets (skip external relationships)
        for relf in glob.glob(work + "/**/*.rels", recursive=True):
            base = os.path.dirname(os.path.dirname(relf))
            with open(relf, encoding="utf-8") as fh:
                body = fh.read()
            for rel in re.findall(r"<Relationship\b[^>]*/>", body):
                if 'TargetMode="External"' in rel:
                    continue
                tgt = re.search(r'Target="([^"]*)"', rel)
                if not tgt or tgt.group(1).startswith("http"):
                    continue
                if not os.path.exists(os.path.normpath(os.path.join(base, tgt.group(1)))):
                    fail(f"dangling relationship {relf} -> {tgt.group(1)}")

        ct_path = os.path.join(work, "[Content_Types].xml")
        with open(ct_path, encoding="utf-8") as fh:
            ct = fh.read()
        overrides = set(re.findall(r'<Override PartName="([^"]*)"', ct))
        defaults = set(re.findall(r'<Default Extension="([^"]*)"', ct))

        # 2. every Override points at a real part
        for part in overrides:
            if not exists(part):
                fail(f"[Content_Types] Override -> missing {part}")

        # 3. every part has a content type, and is reachable (no orphans)
        reachable = set()
        queue = read_rels(work, "_rels/.rels", "")
        while queue:
            part = queue.pop()
            if part in reachable:
                continue
            reachable.add(part)
            d, b = os.path.split(part)
            rp = f"{d}/_rels/{b}.rels" if d else f"_rels/{b}.rels"
            queue.extend(read_rels(work, rp, d))

        for f in glob.glob(work + "/**/*", recursive=True):
            if not os.path.isfile(f) or f.endswith(".rels"):
                continue
            rel = os.path.relpath(f, work).replace(os.sep, "/")
            if rel == "[Content_Types].xml":
                continue
            ext = rel.rsplit(".", 1)[-1]
            if "/" + rel not in overrides and ext not in defaults:
                fail(f"no content type for {rel}")
            if rel.startswith("docProps"):
                continue
            if rel not in reachable:
                fail(f"orphan part (no inbound reference): {rel}")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print("OK: OOXML integrity")


def render(ref, md):
    fd, out = tempfile.mkstemp(suffix=".pptx", prefix="ox-deck-")
    os.close(fd)
    try:
        proc = subprocess.run(
            ["pandoc", md, "-o", out, "--reference-doc", ref, "--slide-level=2"],
            capture_output=True, text=True)
        if proc.returncode != 0:
            fail(f"pandoc failed: {proc.stderr.strip()}")
        if "Couldn't find layout" in proc.stderr:
            fail("pandoc fell back to default layouts:\n" + proc.stderr.strip())
        print("OK: pandoc rendered with zero layout warnings")

        chk = tempfile.mkdtemp(prefix="ox-deck-chk-")
        try:
            with zipfile.ZipFile(out) as z:
                z.extractall(chk)
            names = ""
            for f in glob.glob(chk + "/ppt/slideLayouts/slideLayout*.xml"):
                with open(f, encoding="utf-8") as fh:
                    names += fh.read()
            for expected in ("Title Slide", "Title and Content"):
                if f'cSld name="{expected}"' not in names:
                    fail(f"deck missing branded layout {expected!r}")
            print("OK: deck carries ORGATEX branded layouts")
        finally:
            shutil.rmtree(chk, ignore_errors=True)
    finally:
        if os.path.exists(out):
            os.remove(out)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: check-reference.py <reference.potx> <smoke-test.md>")
    integrity(sys.argv[1])
    render(sys.argv[1], sys.argv[2])
    print("ALL CHECKS PASSED")
```

- [ ] **Step 3: Write the smoke-test deck `presentations/smoke-test.md`**

```markdown
---
title: Smoke Test
author: ORGATEX
date: 2026-06-24
---

# Abschnitt eins

## Eine Inhaltsfolie

- Erster Punkt
- Zweiter Punkt
- Dritter Punkt

## Zwei Spalten

::: columns
:::: column
Linke Spalte
::::
:::: column
Rechte Spalte
::::
:::
```

- [ ] **Step 4: Run the validator to verify it fails (no reference yet)**

Run: `python3 scripts/check-reference.py orgatex-reference.potx presentations/smoke-test.md`
Expected: non-zero exit — a `zipfile`/`FileNotFoundError` traceback because `orgatex-reference.potx` does not exist yet. (Confirms the validator actually depends on a built reference.)

- [ ] **Step 5: Write the build script `scripts/build-reference.py`**

```python
#!/usr/bin/env python3
"""Build a minimal pandoc reference .potx from the ORGATEX template.

Usage: build-reference.py <template.potx> <reference.potx>

Steps:
  1. rename the 7 layouts pandoc addresses by name;
  2. detach example content from the part graph (slide list, notes master,
     custom XML, the 17 unused layouts);
  3. garbage-collect every part no longer reachable from presentation.xml;
  4. prune [Content_Types].xml to surviving parts and re-zip.

The design system pandoc actually uses survives: the slide master, the 7 kept
layouts, the theme, the branding media they reference, and the embedded Mundial
fonts (kept so decks render in the correct typeface on any machine).
"""
import os
import re
import shutil
import sys
import tempfile
import zipfile

RENAMES = {
    "slideLayout1.xml":  ("Titelfolie",         "Title Slide"),
    "slideLayout3.xml":  ("Kapitel 1",          "Section Header"),
    "slideLayout8.xml":  ("Titel und Inhalt",   "Title and Content"),
    "slideLayout10.xml": ("Zwei Inhalte",       "Two Content"),
    "slideLayout12.xml": ("Zwei Inhalte_weiss", "Comparison"),
    "slideLayout13.xml": ("Diagramm 1",         "Content with Caption"),
    "slideLayout16.xml": ("Nur Titel",          "Blank"),
}
KEEP_LAYOUTS = {1, 3, 8, 10, 12, 13, 16}


def main(src, out):
    work = tempfile.mkdtemp(prefix="ox-ref-")
    try:
        with zipfile.ZipFile(src) as z:
            z.extractall(work)
        build(work, out)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print("built", out)


def build(work, out):
    def wp(*a):
        return os.path.join(work, *a)

    def read(f):
        with open(f, encoding="utf-8") as fh:
            return fh.read()

    def write(f, s):
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(s)

    def attr(rel, name):
        m = re.search(name + r'="([^"]*)"', rel)
        return m.group(1) if m else None

    def layout_num(s):
        m = re.search(r"slideLayout(\d+)\.xml", s)
        return int(m.group(1)) if m else None

    # 1. rename the 7 layouts pandoc needs
    for fn, (old, new) in RENAMES.items():
        fp = wp("ppt", "slideLayouts", fn)
        s = read(fp).replace(f'cSld name="{old}"', f'cSld name="{new}"', 1)
        assert f'cSld name="{new}"' in s, f"rename failed in {fn}"
        write(fp, s)

    # 2a. presentation.xml: detach the example slide list and notes master
    pres = wp("ppt", "presentation.xml")
    s = read(pres)
    s = re.sub(r"<p:sldIdLst>.*?</p:sldIdLst>", "", s, flags=re.S)
    s = re.sub(r"<p:notesMasterIdLst>.*?</p:notesMasterIdLst>", "", s, flags=re.S)
    write(pres, s)

    # 2b. presentation.xml.rels: drop slide / notesMaster / customXml rels
    relf = wp("ppt", "_rels", "presentation.xml.rels")
    s = re.sub(
        r"<Relationship\b[^>]*/>",
        lambda m: "" if re.search(
            r'Target="[^"]*(slides/|notesMasters/|customXml/)', m.group(0))
        else m.group(0),
        read(relf))
    write(relf, s)

    # 2c. slide master: drop the 17 unused layouts (rels + sldLayoutIdLst)
    mrel = wp("ppt", "slideMasters", "_rels", "slideMaster1.xml.rels")
    dropped = set()

    def drop_master_rel(m):
        rel = m.group(0)
        n = layout_num(attr(rel, "Target") or "")
        if n is not None and n not in KEEP_LAYOUTS:
            dropped.add(attr(rel, "Id"))
            return ""
        return rel
    write(mrel, re.sub(r"<Relationship\b[^>]*/>", drop_master_rel, read(mrel)))

    master = wp("ppt", "slideMasters", "slideMaster1.xml")
    write(master, re.sub(
        r"<p:sldLayoutId\b[^>]*/>",
        lambda m: "" if attr(m.group(0), "r:id") in dropped else m.group(0),
        read(master)))

    # 3. reachability GC from the package root
    def rels_path(part):
        d, b = os.path.split(part)
        return f"{d}/_rels/{b}.rels" if d else f"_rels/{b}.rels"

    def read_rels(relpath, basedir):
        rp = wp(relpath)
        if not os.path.exists(rp):
            return []
        targets = []
        for m in re.finditer(r"<Relationship\b[^>]*/>", read(rp)):
            rel = m.group(0)
            if 'TargetMode="External"' in rel or 'Target="http' in rel:
                continue
            tgt = attr(rel, "Target")
            if tgt:
                targets.append(
                    os.path.normpath(os.path.join(basedir, tgt)).replace(os.sep, "/"))
        return targets

    reachable = set()
    queue = list(read_rels("_rels/.rels", ""))
    while queue:
        part = queue.pop()
        if part in reachable:
            continue
        reachable.add(part)
        queue.extend(read_rels(rels_path(part), os.path.dirname(part)))

    keep = set(reachable)
    for part in reachable:
        keep.add(rels_path(part))
    keep.update({"_rels/.rels", "[Content_Types].xml"})

    for root, _, files in os.walk(work):
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), work).replace(os.sep, "/")
            if rel not in keep:
                os.remove(os.path.join(root, f))
    for root, _, _ in os.walk(work, topdown=False):
        if not os.listdir(root):
            os.rmdir(root)

    # 4. prune [Content_Types].xml Overrides to surviving parts, then re-zip
    ct = wp("[Content_Types].xml")
    write(ct, re.sub(
        r"<Override\b[^>]*/>",
        lambda m: m.group(0) if os.path.exists(
            wp(*(attr(m.group(0), "PartName") or "").lstrip("/").split("/")))
        else "",
        read(ct)))

    if os.path.exists(out):
        os.remove(out)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(work):
            for f in files:
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, work))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: build-reference.py <template.potx> <reference.potx>")
    main(sys.argv[1], sys.argv[2])
```

- [ ] **Step 6: Build the reference**

Run: `python3 scripts/build-reference.py orgatex-template.potx orgatex-reference.potx`
Expected output: `built orgatex-reference.potx`. The file is ~3.2 MB (down from 4.4 MB).

- [ ] **Step 7: Run the validator to verify it passes**

Run: `python3 scripts/check-reference.py orgatex-reference.potx presentations/smoke-test.md`
Expected:
```
OK: OOXML integrity
OK: pandoc rendered with zero layout warnings
OK: deck carries ORGATEX branded layouts
ALL CHECKS PASSED
```

- [ ] **Step 8: Commit**

```bash
git add .gitignore scripts/build-reference.py scripts/check-reference.py presentations/smoke-test.md orgatex-template.potx
git commit -m "Add ORGATEX pandoc reference build script and validator"
```

---

### Task 2: Make-based build workflow

Wires the developer commands so a deck builds with one command and the reference rebuilds when the template or script changes.

**Files:**
- Create: `Makefile`
- Create: `pandoc/defaults.yaml`

**Interfaces:**
- Consumes: `scripts/build-reference.py`, `scripts/check-reference.py`, `presentations/smoke-test.md`, `orgatex-template.potx` (from Task 1).
- Produces:
  - `make reference` → builds `orgatex-reference.potx`.
  - `make check` → runs the validator.
  - `make all` → renders every `presentations/*.md` into `output/*.pptx`.
  - `make clean` → removes `output/` and the generated reference.

- [ ] **Step 1: Write `pandoc/defaults.yaml`**

```yaml
reference-doc: orgatex-reference.potx
slide-level: 2
```

- [ ] **Step 2: Write the `Makefile`**

Note: the recipe lines below must be indented with a TAB, not spaces.

```makefile
PANDOC    ?= pandoc
PYTHON    ?= python3
TEMPLATE  := orgatex-template.potx
REFERENCE := orgatex-reference.potx
SOURCES   := $(wildcard presentations/*.md)
DECKS     := $(patsubst presentations/%.md,output/%.pptx,$(SOURCES))

.PHONY: all reference check clean
all: $(DECKS)

reference: $(REFERENCE)

$(REFERENCE): $(TEMPLATE) scripts/build-reference.py
	$(PYTHON) scripts/build-reference.py $(TEMPLATE) $(REFERENCE)

output/%.pptx: presentations/%.md $(REFERENCE) pandoc/defaults.yaml | output
	$(PANDOC) --defaults pandoc/defaults.yaml $< -o $@

output:
	mkdir -p output

check: $(REFERENCE)
	$(PYTHON) scripts/check-reference.py $(REFERENCE) presentations/smoke-test.md

clean:
	rm -rf output $(REFERENCE)
```

- [ ] **Step 3: Verify the reference target rebuilds cleanly**

Run: `make clean && make reference`
Expected: prints the `build-reference.py` command then `built orgatex-reference.potx`; `orgatex-reference.potx` exists.

- [ ] **Step 4: Verify the check target**

Run: `make check`
Expected: ends with `ALL CHECKS PASSED`.

- [ ] **Step 5: Verify deck rendering**

Run: `make all`
Expected: creates `output/smoke-test.pptx` (~3.2 MB). Re-running `make all` with no changes prints `make: Nothing to be done for 'all'.` (incremental build works).

- [ ] **Step 6: Commit**

```bash
git add Makefile pandoc/defaults.yaml
git commit -m "Add Make workflow for building ORGATEX decks"
```

---

### Task 3: First presentation scaffold

Creates `presentations/intelligence-architecture.md` as a renderable scaffold using each mapped slide type. The detailed content is authored interactively with the user after this task (topic is in the user's head, per the spec); this task proves the real deck path renders branded and gives the outline a home.

**Files:**
- Create: `presentations/intelligence-architecture.md`

**Interfaces:**
- Consumes: the Make workflow and reference from Tasks 1–2.
- Produces: `output/intelligence-architecture.pptx` via `make all`.

- [ ] **Step 1: Write the deck scaffold `presentations/intelligence-architecture.md`**

```markdown
---
title: Intelligence Architecture
author: Manoel Brunnen
date: 2026-06-24
---

# Überblick

## Ausgangslage

- Platzhalter: Kontext und Motivation
- Wird gemeinsam ausgearbeitet

## Architektur im Überblick

::: columns
:::: column
Platzhalter: linke Spalte
::::
:::: column
Platzhalter: rechte Spalte
::::
:::

# Nächste Schritte

## Zusammenfassung

- Platzhalter
```

- [ ] **Step 2: Render the deck**

Run: `make all`
Expected: creates `output/intelligence-architecture.pptx`.

- [ ] **Step 3: Verify it renders branded with no warnings**

Run: `python3 scripts/check-reference.py orgatex-reference.potx presentations/intelligence-architecture.md`
Expected: ends with `ALL CHECKS PASSED`.

- [ ] **Step 4: Commit**

```bash
git add presentations/intelligence-architecture.md
git commit -m "Add intelligence-architecture deck scaffold"
```

- [ ] **Step 5: Manual PowerPoint check (recommended, once)**

Open `output/intelligence-architecture.pptx` in PowerPoint and confirm the ORGATEX branding and Mundial typeface render correctly. (PowerPoint cannot be exercised in CI; LibreOffice is the automated proxy.)

---

## Notes for the implementer

- The reference build is pure string/zip manipulation of OOXML XML — no XML library is needed, and none should be added. The regexes target the specific attributes ORGATEX uses; if a future template revision changes layout names, update `RENAMES` and `KEEP_LAYOUTS`.
- After Task 1, all later validation reuses `scripts/check-reference.py`. If it ever reports an orphan or dangling reference, the template structure changed — re-inspect before relaxing the check.
- LibreOffice render (`libreoffice --headless --convert-to pdf`) is an optional extra manual smoke check; it is intentionally not wired into `make check` to keep the check fast and dependency-light.
