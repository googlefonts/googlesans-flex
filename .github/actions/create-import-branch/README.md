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
2. Create/Checkout import branch as worktree
3. Delete the sources, and move the `updated-sources/sources` in
4. Commit
5. Rebase on `main`
    * If this fails, a push without rebase is done instead, but the pipeline fails
    * This is so someone can intervene and do the rebase themselves if they want to, resolving conflicts
    * Otherwise, just delete the import branch and start over
    * Conflicts should be super rare
6. Push

Outputs:
* `import-branch`: the name of the new/updated import branch
