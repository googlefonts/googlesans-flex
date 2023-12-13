# create-import-branch

Pre-requisites:
1. `glyphspackage2ufo`
2. Expects `main` to be checked out in `$GITHUB_WORKSPACE/main`

Inputs:
1. `updated-sources` - path for the sources `glyphspackage2ufo` produced
2. `imported-branch` - the branch that was imported from
3. `git-email` - the Google CLA-approved email to use for the commit

Steps:
1. Checkout main
2. Create/Checkout branch as worktree
3. Delete everything in the worktree (except `.git/`), and move the `updated-sources` in
4. Commit & push

Outputs: none
