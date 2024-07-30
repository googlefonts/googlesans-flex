# Google Sans Flex Changelog


## Version 2.003 (2024-07-30)

### New
- added Azerbaijani, Hausa, Hawaiian, Igbo, Vietnamese, and Yoruba  language support (#804, added 21 base glyphs and 100 composed glyphs) 

- new scripts:
	- diff-kerning scripts (#992 #987)

- new Font Bakery checks:
	- all quadratics check (#944)
	- no open corners check (#944)
	- excluded smallcaps before ligatures check (#977)

### Changed
- reduced the width of the space.tf from full to half tabular width (#973)
- changed point structure to address a rasterisation issue in ligatures with crossbars (#937)
- glyph updates: 
	- small outline and proportion refinements on selected Grade and Grade Rounded sources: 0 1 2 3 4 5 7 8 A a B b C c D d F G H h j L N M m R U u V k K Q X x S T p q y Z Æ æ œ Þ þ ? ¿ & Ø Ĳ ĳ ȷ ď Ħ … \ [ { ( · ‘ ® ™ © ≈ ≠ ÷ ≥ # ‹ § @ € £ ¤ ¥ µ * ¢ $ (#996)
-  
	- bug fixes in GRAD sources: ģ ẞ ð Q ¦ ◌̃  ã ñ õ Ã  ◌́ ź í À ý ľ Ù à ỳ ń û ů ű ù ú ŭ ų u ū ü ļ l ĺ ł ̀ ŀ Ì Į Ď D Đ Ð Ħ ħ ď ľ   (#803  #871 #971)
	- glyphs with spacing improvements in GRAD sources: Ŵ Ẅ Ẁ Ẃ W N Ň Ñ Ń N Ņ « » “ ” "
	- addressed a bug in % - slanted in condensed italics (#870)
	- outline bug fix in 9 6 (#954) 
	- refined the consistency of the small numbers (#831)

- modified Font Bakery checks:
	- same tabular width check (#974)




## Version 2.002 (2024-05-16)

### Changed
- added variable fonts with weight axis as a package to the release artifacts, font dedicated to Workspace only (#932)
- fixed interpolation bug in cent and dollar (#936)

## Version 2.001 (2024-04-02)

### Changed
- added static instance package to the release artifacts, instances dedicated to Workspace (#897)
- removed uni0335 uni0337

## Version 2.000 (2024-02-26)

### New
- added Grade axis (tag: GRAD)
- added Maōri language support (2 new marks, 15 precomposed glyphs)
- added new kerning to support the whole language target

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

- Testing:
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

- Metadata in the font: 
  - updated STAT table
  - updated MVAR 

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

