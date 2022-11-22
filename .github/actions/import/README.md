# Import scripts GitHub action

Runs the `gs-merge-designspace` & `gs-noramlize-designspace` scripts on two branches of a repository (both available using `git worktree`), expected at `/github/workspace/main` and `/github/workspace/staging`

The scripts are accessed via the `main` branch

## Running locally

Currently only known to work in WSL/Linux. The `local.sh` script will manage everything, including building the Docker image if you haven't already.

Note: once the docker image has been made, it won't automatically be updated if anything changes, you will need to rebuild it with the following command:

```bash
docker build -t import .github/actions/import
```

## Maintenance

`requirements.txt` is currently maintained by hand.
Versions are pinned to ensure reproducible builds.
It's probably recommended to keep the versions inline with those that are used to build `<repo root>/requirements.txt`
