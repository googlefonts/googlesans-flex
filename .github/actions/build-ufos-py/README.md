# build-ufos-py

Pre-requisites:
1. Expects Python to have been set up

Inputs:
1. `repo-path` - the location of the repository to build (default `.`, i.e. `$GITHUB_WORKSPACE`)

Steps:
1. Set up venv
2. Run `make bump-to-tag` if release
3. Build
4. Upload zip artifact

Outputs:
* `artifact-name`: the name of the artifact (without the .zip extension)

## Maintenance notes

Whenever a new workflow is made that uses this action, its name needs to be added to the `case` statement in the "Set zip file name" step
