# shaperglot

Pre-requisites:
1. Expects Python to have been setup
2. Expects a TTF to be available

Inputs:
1. Path to a TTF to test

Steps:
1. Setup venv
2. Run `shaperglot report` on the TTF

## Maintenance

Target language list is currently hand-converted from: https://github.com/googlefonts/googlesans-flex/issues/684#issuecomment-1875253602

`target_langs.txt` currently isn't used due to `shaperglot check` seemingly not accepting this language codes, despite saying it does in the help text.
Raised [here](https://github.com/googlefonts/shaperglot/issues/23#issuecomment-1900600952)
