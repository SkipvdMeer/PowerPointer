#!/bin/bash
# Builds "Slide Remote.app" and puts it in your Applications folder.
set -e
cd "$(dirname "$0")"
echo ""
echo "  Building Slide Remote for Mac..."
echo ""

PY=python3
if ! command -v $PY >/dev/null 2>&1; then
  echo "  Python 3 was not found. Install it from https://www.python.org/downloads/macos/ and run this again."
  read -n 1 -s -r -p "  Press any key to close."; exit 1
fi
if ! $PY -c "import tkinter" >/dev/null 2>&1; then
  echo "  Your Python has no window toolkit (tkinter)."
  echo "  Fix: install Python from python.org, or run: brew install python-tk"
  read -n 1 -s -r -p "  Press any key to close."; exit 1
fi

echo "  [1/4] Installing packages"
$PY -m venv .venv
PY=".venv/bin/python"
"$PY" -m pip install --quiet -r requirements-build.txt

echo "  [2/4] Creating the app icon"
"$PY" SlideRemote.pyw --make-icon

echo "  [3/4] Building Slide Remote.app (takes about a minute)"
"$PY" -m PyInstaller --noconfirm --clean --windowed --name "Slide Remote" \
  --specpath build --icon "$PWD/icon.icns" --osx-bundle-identifier nl.yellowtail.slideremote \
  SlideRemote.pyw > build.log 2>&1 || { echo "  Build failed. See build.log."; exit 1; }

echo "  [4/4] Installing to Applications"
DEST="/Applications"
[ -w "$DEST" ] || DEST="$HOME/Applications"; mkdir -p "$DEST"
rm -rf "$DEST/Slide Remote.app"
cp -R "dist/Slide Remote.app" "$DEST/"
xattr -cr "$DEST/Slide Remote.app" 2>/dev/null || true
codesign --force --deep --sign - "$DEST/Slide Remote.app" >/dev/null 2>&1 || true

echo ""
echo "  Done. Slide Remote is in $DEST."
echo "  One-time setup: System Settings > Privacy & Security > Accessibility,"
echo "  click +, add Slide Remote, and switch it on. Then restart the app."
echo ""
open -R "$DEST/Slide Remote.app"
read -n 1 -s -r -p "  Press any key to close."
