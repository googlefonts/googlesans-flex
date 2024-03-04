# build-glyphs.yml

This is probably the most convoluted of all the build/import workflows

The sources have to be put into a tarball before being uploaded as an artifact otherwise it'll error on the number of files (and who can blame it?)

This is also then annoying when when tests.yml usually works by doing a Git checkout, when obviously we can't in this case.
Instead, we set `artifact-as-branch` to the name of the tarball artifact, which triggers the edge case in tests.yml

# tests.yml

Pre-requisites:
1. There should be a checkout of the repo with up-to-date sources and built fonts

Inputs:
1. `branch` - the branch to check out (defaults to main)
2. `repo-path` - where the repository checkout should be made (default `.`, i.e. `$GITHUB_WORKSPACE`)
3. `artifact-name` - the name of the artifact with the built fonts
4. `artifact-as-branch` (optional) - if set, uses the artifact name provided as a tarball checkout instead of using git (for build-glyphs)

Steps:
1. Checkout `branch`
2. Run [OpenType Sanitizer](https://github.com/googlefonts/ots-python)
3. Run [font-size](https://github.com/source-foundry/font-size)
4. Run [shaperglot](https://github.com/googlefonts/shaperglot)
5. Run [Fontbakery](https://github.com/fonttools/fontbakery)
6. Upload Fontbakery reports

Outputs: none

## Maintenance

### shaperglot

Target language list is currently hand-converted from [this GitHub issue](https://github.com/googlefonts/googlesans-flex/issues/684#issuecomment-1875253602) and is passed to shaperglot through `xargs` (see the Makefile)
