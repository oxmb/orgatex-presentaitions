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
