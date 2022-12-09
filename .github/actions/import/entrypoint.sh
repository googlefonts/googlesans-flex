#!/bin/sh
set -e

# Check branches are mounted
if [ ! -d /github/workspace/target ]; then
    echo "ERROR: Missing branch to merge into (target branch)"
    exit 1
fi
if [ ! -d /github/workspace/source ]; then
    echo "ERROR: Missing branch to merge (source branch)"
    exit 1
fi

# TODO: read the list of designspaces from the config.yaml
# for designspace in $(python -e "import yaml parse config.py") do

echo "Merging upright designspace..."
python3 /scripts/gs-merge-designspace.py \
    --source /github/workspace/source/sources/roman/GoogleSansFlex.designspace \
    --target /github/workspace/target/sources/regular/GoogleSansFlex.designspace \
    --import-glyphs-file /glyph-list.txt \
    --replace-target-designspace \
    --follow-glyphs # While sources are in flux
echo

echo "Normalising upright designspaces..."
python3 /scripts/gs-normalize-designspace.py \
    --source-dir /github/workspace/target/sources/regular/

echo "Merging italic designspace..."
python3 /scripts/gs-merge-designspace.py \
    --source /github/workspace/source/sources/italic/GoogleSansFlex-Italic.designspace \
    --target /github/workspace/target/sources/italic/GoogleSansFlex-Italic.designspace \
    --import-glyphs-file /glyph-list.txt \
    --replace-target-designspace \
    --follow-glyphs # While sources are in flux
echo

echo "Normalising italic designspaces..."
python3 /scripts/gs-normalize-designspace.py \
    --source-dir /github/workspace/target/sources/italic/
