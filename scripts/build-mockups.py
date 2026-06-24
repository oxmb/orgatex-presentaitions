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
