# tests.yml

Pre-requisites:
1. There should be a checkout of the repo with up-to-date sources and built fonts

Inputs:
1. `repo-path` - where the repository checkout is (default `.`, i.e. `$GITHUB_WORKSPACE`)

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

Target language list is currently hand-converted from: https://github.com/googlefonts/googlesans-flex/issues/684#issuecomment-1875253602

`target_langs.txt` currently isn't used due to `shaperglot check` seemingly not accepting this language codes, despite saying it does in the help text.
Raised [here](https://github.com/googlefonts/shaperglot/issues/23#issuecomment-1900600952)
