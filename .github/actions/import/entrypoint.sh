#!/bin/sh
set -e

# Check branches are mounted
if [ ! -d /github/workspace/main ]; then
    echo "ERROR: Missing branch to merge into (destination branch)"
    exit 1
fi
if [ ! -d /github/workspace/staging ]; then
    echo "ERROR: Missing branch to merge (source branch)"
    exit 1
fi

echo "Merging upright designspace..."
python3 /scripts/gs-merge-designspace.py \
    --source /github/workspace/staging/sources/roman/GoogleSansFlex.designspace \
    --target /github/workspace/main/sources/regular/GoogleSansFlex.designspace \
    --import-glyphs-file /glyph-list.txt \
    --replace-target-designspace \
    --follow-glyphs # While sources are in flux
echo

echo "Normalising upright designspaces..."
python3 /scripts/gs-normalize-designspace.py \
    --source-dir /github/workspace/main/sources/regular/

echo "Merging italic designspace..."
python3 /scripts/gs-merge-designspace.py \
    --source /github/workspace/staging/sources/italic/Italic-opsz18.designspace \
    --target /github/workspace/main/sources/italic/GoogleSansFlex-Italic.designspace \
    --import-glyphs-file /glyph-list.txt \
    --replace-target-designspace \
    --follow-glyphs # While sources are in flux
echo

echo "Normalising italic designspaces..."
python3 /scripts/gs-normalize-designspace.py \
    --source-dir /github/workspace/main/sources/italic/
