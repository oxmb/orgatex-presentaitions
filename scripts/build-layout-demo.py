#!/usr/bin/env python3
"""Build the ORGATEX layout demo PPTX.

Pandoc 3.x does not auto-trigger every PPTX layout from markdown alone
(Comparison, Content with Caption, Blank all fall back to Two Content /
Title and Content).  This script builds the deck with pandoc then
post-processes the ZIP to force the correct layout reference on the slides
that need it.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

REF = "orgatex-reference.potx"
SRC = "presentations/layout-demo.md"
OUT = "output/layout-demo.pptx"

FORCED = {
    5: "Comparison",
    6: "Content with Caption",
    7: "Blank",
}


def main():
    os.makedirs("output", exist_ok=True)

    subprocess.run(
        ["pandoc", "--defaults", "pandoc/defaults.yaml", SRC, "-o", OUT],
        check=True)

    work = tempfile.mkdtemp(prefix="ox-layout-demo-")
    try:
        with zipfile.ZipFile(OUT) as z:
            z.extractall(work)

        layout_dir = os.path.join(work, "ppt", "slideLayouts")
        name_to_file = {}
        for fn in os.listdir(layout_dir):
            if not (fn.startswith("slideLayout") and fn.endswith(".xml")):
                continue
            with open(os.path.join(layout_dir, fn), encoding="utf-8") as fh:
                xml = fh.read()
            m = re.search(r'cSld name="([^"]+)"', xml)
            if m:
                name_to_file[m.group(1)] = fn

        for slide_num, layout_name in FORCED.items():
            if layout_name not in name_to_file:
                print(f"WARNING: layout {layout_name!r} not found in deck", file=sys.stderr)
                continue
            target = name_to_file[layout_name]
            rel_path = os.path.join(
                work, "ppt", "slides", "_rels", f"slide{slide_num}.xml.rels")
            if not os.path.exists(rel_path):
                print(f"WARNING: {rel_path} not found", file=sys.stderr)
                continue
            with open(rel_path, encoding="utf-8") as fh:
                rels = fh.read()
            rels = re.sub(
                r'(Type="[^"]*slideLayout"[^/]*/?\s*Target=")[^"]+(")',
                rf'\1../slideLayouts/{target}\2',
                rels)
            with open(rel_path, "w", encoding="utf-8") as fh:
                fh.write(rels)

        os.remove(OUT)
        with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(work):
                for fn in files:
                    full = os.path.join(root, fn)
                    z.write(full, os.path.relpath(full, work))
    finally:
        shutil.rmtree(work, ignore_errors=True)

    print("built", OUT)


if __name__ == "__main__":
    main()
