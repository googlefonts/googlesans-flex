# Import scripts GitHub action

Runs the `gs-merge-designspace` & `gs-noramlize-designspace` scripts on two branches of a repository (both available using `git worktree`), expected at `/github/workspace/main` and `/github/workspace/staging`

The scripts are accessed via the `main` branch

## Maintenance

`requirements.txt` is currently maintained by hand.
Versions are pinned to ensure reproducible builds.
It's probably recommended to keep the versions inline with those that are used to build `<repo root>/requirements.txt`
