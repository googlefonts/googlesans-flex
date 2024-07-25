When importing the v2.003 design sources, we wish to include the new kerning added for new glyphs from v2.003, while retaining the pre-existing kerning for pre-existing glyphs from v2.002.

This directory contains scripts for:

- Reporting changes made to the pre-existing kerning in the v2.002 design sources; and
- Discarding these changes while preserving the new kerning for new glyphs.

## Producing sources with only the desired changes

1. Gather two sets of Glyphs design sources:

   - _GSF-full-2.002.glyphs_
     - Contains:
       - The reference kerning from v2.002 that we wish to preserve
     - Source from:
       - The last Glyphs package imported before the v2.002 release
   - _GSF-full-2.003.glyphs_
     - Contains:
       - All of the latest changes for v2.003 (outlines, anchors, etc)
       - The new kerning for new v2.003 glyphs that we wish to preserve
       - The modified kerning for pre-existing v2.002 glyphs that we wish to strip away
     - Source from:
       - The latest Glyphs package imported to `main` in preparation for the v2.003 release

2. If either source is a `.glyphspackage` directory, convert it to a `.glyphs` file in Glyphs.

   - This is necessary for `glyphsLib` to be able to save the changes in the same format.
   - **NOTE:** Use the version of Glyphs used for design work to avoid unwanted changes.

3. Run `split_kerning_groups.py`

   1. `make venv`
   1. Activate the new venv.
   1. `python scripts/one-off/diff-kerning/split_kerning_groups.py`

4. _GSF-full-2.003.glyphs_ should now contain the desired kerning for release.

   - The kerning from v2.002 will be used for pre-existing glyphs, while any new glyphs sharing kerning groups with pre-existing glyphs will have been split into their own new groups to avoid losing v2.003 kerning additions.

5. Each optional, as required:
   - Analyse the new sources for redundant groups with `prunable_extension_groups.py`.
   - Produce a test build of the new design sources:
     1. Convert the sources to the `.glyphspackage` format in Glyphs.
     1. Commit to the `sources/design-source` directory in a new branch.
     1. Run the _Build from Glyphs package_ workflow from `main` targeting the new branch as described in the project's root README.
   - Import the sources into `main` for release :
     1. Ensure that the sources used in the process contain **EVERY** change wanted for v2.003, in addition to the latest kerning.
     1. Convert the sources to the `.glyphspackage` format in Glyphs.
     1. Commit to the `sources/design-source` directory in a new branch.
     1. Run the _Update from sources_ workflow from `main` targeting the new branch as described in the project's root README.
     1. If we wish to avoid future releases from re-importing the changes to pre-existing glyphs' kerning, then use the new branch as a basis for future design work in Glyphs.

## Origin of sources

**NOTE:** This may be outdated; see the latest commit **message** for each file to be sure of the exact source commit.

v2.002 downloaded from that commit:
https://github.com/googlefonts/googlesans-flex/commit/56b9a2087de6ebdd0fa86f1a2e9717150619489c

v2.003 downloaded from:
https://github.com/googlefonts/googlesans-flex/tree/GSF-Ashler-v2.2-OctDev
