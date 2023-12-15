# tests

Pre-requisites:
1. There should be an artifact of built fonts available

Inputs:
1. `branch` - the branch to get the sources from
2. `variable-artifact` - the GitHub artifact name of the variable TTFs built from `branch`

Steps:
1. Checkout `branch`
2. Download `variable-artifact`
2. Run Fontbakery
3. Run OT Sanitizer
4. Run `file-size`
5. Upload Fontbakery reports

Outputs: none
