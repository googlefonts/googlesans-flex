# tests.yml

Pre-requisites:
1. There should be a checkout of the repo with up-to-date sources and built fonts

Inputs:
1. `branch` - the branch to check out (defaults to main)
2. `artifact-name` - the name of the artifact with the built fonts

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
