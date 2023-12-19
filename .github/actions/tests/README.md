# tests

Pre-requisites:
1. There should be an artifact of built fonts available

Inputs:
1. `branch` - the branch to get the sources from
2. `variable-artifact` - the GitHub artifact name of the variable TTFs built from `branch`

Steps:
1. Checkout `branch`
2. Run [Fontbakery](https://github.com/fonttools/fontbakery)
3. Run [OpenType Sanitizer](https://github.com/googlefonts/ots-python)
4. Run [font-size](https://github.com/source-foundry/font-size)
5. Upload Fontbakery reports

Outputs: none
