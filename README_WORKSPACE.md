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
- All VFs have had their Slant/slnt axis renamed to Italic/ital in the STAT.

## Links

- Issue from Dave Crossland: [Release v2.1 as wght axis fonts instead of static fonts, and rename the default width family #932](https://github.com/googlefonts/googlesans-flex/issues/932)
- Initial issue for static fonts: [Add Static Instances #897](https://github.com/googlefonts/googlesans-flex/issues/897)
- GitHub workflow: [.github/workflows/release.yml](https://github.com/googlefonts/googlesans-flex/blob/main/.github/workflows/release.yml)
- VF Slicing script: [scripts/cut_instances.py](https://github.com/googlefonts/googlesans-flex/blob/main/scripts/cut_instances.py)
