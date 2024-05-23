# Google Sans Flex Workspace Fonts

This folder contains a set of VFs intended for use in Google Workspace. These
families should be hidden from catalog surfaces and only shown in Workspace.

## Details

These families are:

| Family name                     | opsz  | wdth | ROND | GRAD |
|---------------------------------|-------|------|------|------|
| Google Sans Flex ExtraExpanded  | 144pt | 150  | 0    | 0    |
| Google Sans Flex Normal         | 144pt | 100  | 0    | 0    |
| Google Sans Flex Rounded        | 144pt | 100  | 100  | 0    |
| Google Sans Flex SuperCondensed | 144pt | 25   | 0    | 0    |
| Google Sans Flex Text           | 12pt  | 100  | 0    | 0    |
| Google Sans Flex UltraCondensed | 144pt | 50   | 0    | 0    |

- Each family has 2 VFs, one upright and one italic.
- All VFs include a subset of the Weight axis from 100 to 900, with fvar instances.
- All VFs have had their Slant/slnt axis renamed to Italic/ital in the STAT, and
other STAT axes removed (anything else than Weight and Italic).

### Process for slicing VFs

1. Slice Workspace VF from `GoogleSansFlex[GRAD,ROND,opsz,slnt,wdth,wght].ttf`
  using `fonttools varLib.instancer`
2. Fixup a few tables:
    - `OS/2` average char width, and various measurements that get changed
      inadvertently by the instancer. FontBakery checks that in the end we have
      the correct measurements that match the rest of the GS family.
    - family and style names, style mapping
    - name ID 25, which needs to be different for each TTF file
    - PANOSE entries, fsSelection bits, which depend on the location of the VF
    - fvar instances along the Weight axis, as a Workspace requirement
    - STAT Slant -> Italic, as a FontBakery requirement
    - remove other STAT axes to prevent issues in Adobe apps
3. Prune TTF using the subsetter, to shake off any potential unreachable glyphs
4. Run `font-v` to write the Git commit SHA into the name table
5. Run the GPOS compaction to reduce the file size

## Links

- Issue from Dave Crossland: [Release v2.1 as wght axis fonts instead of static fonts, and rename the default width family #932](https://github.com/googlefonts/googlesans-flex/issues/932)
- Initial issue for static fonts: [Add Static Instances #897](https://github.com/googlefonts/googlesans-flex/issues/897)
- GitHub workflow: [.github/workflows/release.yml](https://github.com/googlefonts/googlesans-flex/blob/main/.github/workflows/release.yml)
- VF Slicing script: [scripts/cut_instances.py](https://github.com/googlefonts/googlesans-flex/blob/main/scripts/cut_instances.py)
- [Further issue about cleaning up the STAT table](https://github.com/googlefonts/googlesans-flex/issues/949)
