# tests

Pre-requisites:
1. There should be a checkout of the repo with up-to-date sources and built fonts

Inputs:
1. `repo-path` - where the repository checkout is (default `.`, i.e. `$GITHUB_WORKSPACE`)

Steps:
1. Checkout `branch`
2. Run [Fontbakery](https://github.com/fonttools/fontbakery)
3. Run [OpenType Sanitizer](https://github.com/googlefonts/ots-python)
4. Run [font-size](https://github.com/source-foundry/font-size)
5. Upload Fontbakery reports

Outputs: none
