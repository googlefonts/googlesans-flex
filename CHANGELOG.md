# Google Sans Flex Changelog

## Version 4.007 (2026-08-21)

### New
- Addition of white arrows and "point of interest" ([#1281](https://github.com/googlefonts/googlesans-flex/pull/1281))
- Expand Yoruba language support: add ◌̩ (U+0329) ([#1128](https://github.com/googlefonts/googlesans-flex/pull/1128))

### Changed
- Update superscript and subscript number design to follow standard figure designs ([#1265](https://github.com/googlefonts/googlesans-flex/pull/1265))
- Shorten arm of one.tf ([#1286](https://github.com/googlefonts/googlesans-flex/pull/1286))
- Tight spacing in /L/A ([#1272](https://github.com/googlefonts/googlesans-flex/pull/1272))
- Fix spacing in ij ([#1269](https://github.com/googlefonts/googlesans-flex/pull/1269))
- RSB / kerning on e.logo appears too large  ([#1266](https://github.com/googlefonts/googlesans-flex/pull/1266))
- Changed condition for swapping $ from 699 to 700 wght ([#1267](https://github.com/googlefonts/googlesans-flex/pull/1267))


## Version 4.006 (2026-06-26)

### New
Adding workspace build for opsz 11 ([#1287](https://github.com/googlefonts/googlesans-flex/pull/1287)) 

### Changed
- updated logo glyphs
- updated dependencies (actions/cache from 5 to 6, f-actions/opentype-sanitizer from 3 to 4, actions/checkout from 6 to 7)

## Version 4.005 (2026-04-10)

### Changed
- updated logo glyphs

## Version 4.004 (2026-03-26)

### Changed
- reverted logo glyphs to their design from v3.007


## Version 4.003 (2026-02-25)

### Changed
- adding Figma-specific VF builds ([#1271](https://github.com/googlefonts/googlesans-flex/pull/1271))


## Version 4.002 (2026-01-15)

### Changed
- removed `BASE` table from Android builds. ([#1262](https://github.com/googlefonts/googlesans-flex/issues/1262))


## Version 4.001 (2026-01-14)
### New
- added circled figures ([#1170](https://github.com/googlefonts/googlesans-flex/issues/1170))
- updated default copyright symbol and moved old one to the ss09 feature ([#1224](https://github.com/googlefonts/googlesans-flex/issues/1224))
- added scripts: `find_non_duplex_kerning.py` ([#1253](https://github.com/googlefonts/googlesans-flex/issues/1253)) 

### Changed
- updated Saudi Riyal symbol (U+20C1) ([#1237](https://github.com/googlefonts/googlesans-flex/issues/1237))
- updated default copyright symbol and moved old one to the feature 

## Version 4.000 (2025-12-22)
### New
- added Saudi Riyal symbol (U+20C1) ([#1230](https://github.com/googlefonts/googlesans-flex/issues/1230))
- added BASE table ([#1170](https://github.com/googlefonts/googlesans-flex/issues/1170))


### Changed
- updated optical size 144 pt design (letter proportions, spacing, kerning) ([#1167](https://github.com/googlefonts/googlesans-flex/issues/1167))
- revised tapering of the semi-round curved stems in characters involving terminals occurring along a curve (eg. C, G, J, S, c, e, f, g, j, q, r, s, t, etc.)
- updated logo ligatures
- fixed ([#1160]https://github.com/googlefonts/googlesans-flex/issues/1160)

## Version 3.007 (2025-11-7)
### Changed
- added updated the licence to OFL, CODE_OF_CONDUCT.md, CONTRIBUTING.md, CONTRIBUTORS.txt, added TRADEMARKS.md, added AUTHORS.txt

### Production
- moved to fontc compiler #1194
- moved partially to fontspector #1191 
- uv for for venv management #1184
- updated and reduced dependencies (#1198 and multiple other PRs)
- Added dependabot configuration for GH Actions version update monitoring #1150 

## Version 3.006 (2025-08-25)
### Changed
- added currency signs: ₹ ₩ ฿ (#1164)
- added script to find where glyphs accidentally vary width across duplex axes ([#1180](https://github.com/googlefonts/googlesans-flex/pull/1180))


## Version 3.005 (2028-08-19)
### Changed
- added GSF TV font slice (#1176)
- added U+207B and U+02E3 (#1165)
- removed HVAR table from Android release

## Version 3.004 (2025-04-9)
### Changed
- updated workspace font families (upright + italic):
  - added back and changed opsz from 12 to 14:
    Google Sans Flex Text (14opsz, 100wdth, 0ROND)


## Version 3.003 (2025-03-25)
### Changed
- updated workspace font families (upright + italic):
  - added back and changed opsz from 144 to 18:
    Google Sans Flex Normal (18opsz, 100wdth, 00ROND)
    Google Sans Flex Text (12opsz, 100wdth, 0ROND)
    Google Sans Flex UltraCondensed (18opsz, 50wdth, 0ROND)
    Google Sans Flex SuperCondensed (18opsz, 25wdth, 0ROND)
    Google Sans Flex ExtraExpanded (18opsz, 150wdth, 0ROND)

  - removed:
    Google Sans Flex (18opsz, 100wdth, 0ROND)

- changed workflow:
  - migrated private Fontbakery checks to open-sourced equivalents ([#983](https://github.com/googlefonts/googlesans-flex/pull/983)) 
  

## Version 3.002 (2025-03-20)
### Changed
- updated workspace families (upright + italic):
  - added
    Google Sans Flex SemiRounded (18opsz, 100wdth, 40ROND)

  - changed optical size from 144 to 18:
    Google Sans Flex (18opsz, 100wdth, 0ROND)
    Google Sans Flex Rounded (18opsz, 100wdth,  100ROND)

  - removed:
    Google Sans Flex Normal (18opsz, 100wdth, 00ROND)
    Google Sans Flex Text (12opsz, 100wdth, 0ROND)
    Google Sans Flex UltraCondensed (144opsz, 50wdth, 0ROND)
    Google Sans Flex SuperCondensed (144opsz, 25wdth, 0ROND)
    Google Sans Flex ExtraExpanded (144opsz, 150wdth, 0ROND)

## Version 3.001 (2024-12-28)
### Changed
- kerning triples 7.1; 7.4; 7.9 reviewed and updated to address #1124

## Version 3.000 (2024-12-17)
### New
- added Add narrow non-breaking space, U+202F (#1083)

### Changed
- edited rounding style (#905, #1093, #1071)
- filesize optimisation (#1055 #1018, partly #968)
- small design improvements (#1091, #1049 #1050 #1053 #1063 #1108)
- fixed anchor positioning in Ų (#1001)
- fixed bug in Oslash (#1039)
- improved the height of the accents in uppercase across the designspace (#967)
- update terminal of mu in opsz144 (#1049)
- adjustments 6 & 9 (#1052) 
- correction interpolation diagonal Q (#1075)
- correction in the open type feature: ss01 single-storey /a variant for /adotbelow (#1061) 
- correction in the open type feature: zeroslash.tf (#1076) 

### Production
- add automatic checks for automatic decomposition (#1019)
- added METADATA.pb file (#1095)
- added Font Bakery check to ensure that creation date in head does not change between releases (#1070)
- improved Shaperglot output (#805)
- improved the workflow (#890 #894 #797 #1012 #1031)
- new build workflow with fonts for Android (#1051 #1090 #1085 )
- remove dead code case feature (#958)

## Version 2.007 (2025-09-13)
### Changed
Production ready fonts, for Android only. 
- removed HVAR table to improve VF rendering performance on Android
- updated USE_MY_METRICS settings. (When the USE_MY_METRICS flag is set on a component, it instructs the font renderer to use the advance width and side bearings of that specific component as the metrics for the entire composite glyph, instead of calculating the metrics based on the composite glyph's own outline data, or by summing the metrics of all components.)

## Version 2.006 (2024-11-12)

### New
- added Android fonts with fixed yMin + yMax (#1051)


## Version 2.005 (2024-11-1)

### New
- added `radical` and `pi`. `Pi` is encoded under the `u+1D6E1` as the Mathematical Bold Pi Symbol (#1020)

### Changed
- changed the spacing of tabular punctuation from full tabular width to half tabular width. (#1046)
- updated feature code to better support the tabular colon. (#1046)
- addressed an interpolation bug in the `dollar` sign. Few intermediate masters changed. (#997)


## Version 2.004 (2024-10-10)
### Changed
- bug fix in the workspace fonts (#1034) 


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

