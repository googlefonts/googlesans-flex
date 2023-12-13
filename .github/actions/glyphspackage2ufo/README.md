# glyphspackage2ufo

Pre-requisites: expects `main` to be checked out in `$GITHUB_WORKSPACE/main`

Inputs:
1. `git-ref` - the Git reference for the sources to convert

Steps:
0. Setup Python
1. Check out `it-ad-wip-v2.0` in `$GITHUB_WORKSPACE/octavio`
3. Create a copy of `main` in target dir
4. Run import script

Outputs:
* `directory`: where the new UFO sources reside
