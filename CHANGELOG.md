# Google Sans Flex Changelog

## Version 2.000 (2024-02-26)

### New
- added Grade axis (tag: GRAD)
- added Maōri language support (2 new marks, 15 precomposed glyphs)
- added new kerning to support the whole language target.

- New Scripts:
  - glyphs_to_ds.py 
  - gs-glyphs2ufo.py Add ufo2glyphs2ufo scripts
  - gs-merge-designspace.py
  - gs-normalize-designspace.py
  - gs-progress-burndown.py
  - gs-ufo2glyphs.py
  - find-data-source.py - a script to find interpolation sources at a location
  - name_ufos_by_position.py - a script for flattening UFO hierarchy and renaming with new scheme
  - print-space-width.py - a script to write widths of space glyph to a CSV
  - prune-glyphsets.py - a glyphset pruning script
  - set-notdef-glyph.py - a script to set notdef in all sources

- added shaperglot

### Changed

- Source type:
  - Using .glyphspackage as design sources while keeping the production sources as UFO

- General updates in the design space of the variable font:
  - Improved balance of weight and width within each optical size
  - Updated the setup of the source to reduce the number of masters and the file-size
  - Reduced number of intermediate masters - related to the update to the terminals in the condensed styles 

- Design improvements in the variable font:
  - Improved spacing and kerning
  - Improved consistency of the terminals font-wide: an update to the condensed styles–terminals are now more open
  - Design craft improvements: improved proportions, character balance and curves
  - Refined the point structure, e.g. remove extra points
  - Improved consistency of the stems
  - Improved consistency of the overshoots  
  - Refined angles of the terminals in C c G g S s J j 
  - Refined the proportions of letters with diagonal strokes to improve the design of the rounding styles
  - Refined fractions
  - Refined Black weight to improve legibility 
  - Updated design of the quotes and ellipsis in the heavier masters
  - Improved design of mathematical symbols
  - Improved positioning of small numbers for better consistency within the whole design space
  - Improved small number positioning (sups, subs, sinf, numr, dnom, frac)

- Scripts:
  - updated set-overlap-bits.py

## Version 1.000 (2023-01-18)
- initial release


## Version 1.002 (2023-06-28)

### New
- Italic font
- New font with a slant axis, which combines Italic and Upright

- New Scripts:
  - defuse-guidelines.py
  - gs-glyphs2ufo.py
  - gs-merge-designspace.py
  - gs-normalize-designspace.py
  - gdef.py
  - normalize.py
  - prune_font_binary.py
  - reachable_glyphs.py
  - set-overlap-bits.py
  - print-space-width.py
  - prune-glyphsets.py
  - set-notdef-glyph.py
  - find-data-source.py


### Changed
- Bug fixes in outlines
- Bug fixes in kerning
- added burndown chart workflow
- diffenator workflow
- updated check-googlesans.py
- gs-progress-burndown.py
- gs-ufo2glyphs.py
- cut-instances.py

## Version 1.001 (2023-03-08)

### New
- OpenType Layout Features:
calt dnom frac liga lnum locl numr ordn pnum sinf ss01 ss02 subs sups tnum zero kern

- 66 new glyphs in total:
wiggle glyphs
Google logo glyphs

- set OVERLAP_SIMPLE and OVERLAP_COMPOUND bit flags in glyf table

- new scripts
find-unknerned-glyphs.py
round-sources.py
set-overlap-bits.py
add-feas.py
adjust-advance-width.py
prune_font_binary.py

### Changed
- This version doesn't contain GRAD axis

## Version 1.000 (2023-01-18)
- initial release


## Template

### New
- 

### Changed
- 

### Fixed
- 

### Dependencies
- 

