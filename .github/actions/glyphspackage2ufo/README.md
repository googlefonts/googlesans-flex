# glyphspackage2ufo

Pre-requisites:
1. expects `main` to be checked out in `$GITHUB_WORKSPACE/main`
2. expects Python to have been set up

Inputs:
1. `git-ref` - the branch for the sources to convert

Steps:
1. Check out `git-ref` in `$GITHUB_WORKSPACE/octavio`
3. Create a copy of `main` in target dir
4. Run import script

Outputs:
* `directory`: where the new UFO sources reside
