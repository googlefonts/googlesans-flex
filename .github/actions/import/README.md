# Import scripts GitHub action

Runs the `gs-merge-designspace` & `gs-noramlize-designspace` scripts on two branches of a repository (both available using `git worktree`), expected at `/github/workspace/main` and `/github/workspace/staging`

The scripts are accessed via the 'base' branch of the PR

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

The script will detect whether you are updating an existing import or starting a new one.
The only difference to the GitHub workflow is that it will not create a pull request for you if one does not already exist

## Maintenance

`requirements.txt` is currently maintained by hand.
Versions are pinned to ensure reproducible builds.
It's probably recommended to keep the versions inline with those that are used to build `<repo root>/requirements.txt`

`glyph-list.txt` also needs to be maintained.
It is not currently in use, but is expected to be in due course
