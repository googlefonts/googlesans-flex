# Import scripts GitHub action

Runs the `gs-merge-designspace` & `gs-noramlize-designspace` scripts on two branches of a repository (both available using `git worktree`), expected at `/github/workspace/main` and `/github/workspace/staging`

## Running locally

Requirements:
* MacOS/Linux/WSL bash shell
* Docker
* GitHub SSH authentication ([guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh))

Usage:

Make sure you're in a terminal in the repository root, then run

```bash
./.github/actions/import/local.sh <branch name>
```

The script will detect whether you are updating an existing import or starting a new one

## Maintenance

`requirements.txt` is currently maintained by hand.
Versions are pinned to ensure reproducible builds.
It's probably recommended to keep the versions inline with those that are used to build `<repo root>/requirements.txt`

glyph-lists also needs to be maintained.
It is expected that the file name is the same as the folder name in `sources`, which is defined in `sources/config.yaml`.
For example:

```yml
sources:
  - regular/GoogleSansFlex.designspace
  - italic/GoogleSansFlex-Italic.designspace
...
```

Will expect a `.github/actions/import/glyph-lists/regular.txt` and a `.github/actions/import/glyph-lists/italic.txt` - though there is fallback to regular (hard-coded) if `italic.txt` doesn't exist
