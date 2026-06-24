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

        # 4. all 7 renamed layouts present in the reference
        expected_layouts = [
            "Title Slide", "Section Header", "Title and Content",
            "Two Content", "Comparison", "Content with Caption", "Blank",
        ]
        layout_names = ""
        for f in glob.glob(work + "/ppt/slideLayouts/slideLayout*.xml"):
            with open(f, encoding="utf-8") as fh:
                layout_names += fh.read()
        for name in expected_layouts:
            if f'cSld name="{name}"' not in layout_names:
                fail(f"reference missing renamed layout: {name!r}")
        print("OK: all 7 renamed layouts present")
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
