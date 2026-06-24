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
