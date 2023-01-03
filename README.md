# Google Sans Flex


## Building

Fonts are built automatically by GitHub Actions - take a look in the "Actions" tab for the latest build.

If you want to build fonts manually on your own computer:

* `make build` will produce font files.
* `make test` will run [FontBakery](https://github.com/googlefonts/fontbakery)'s quality assurance tests.
* `make proof` will generate HTML proof files.

## Importing new sources

### From another branch on this repository

There it a GitHub workflow that covers this from start to finish, no local work required.
You can access it from [Actions > Update from sources > Run workflow](https://github.com/googlefonts/googlesans-flex/actions/workflows/import.yaml).

The "Use workflow from" determines which version of the import script will be used.
* As Marianna or Chris, you'll always want this to be `main`, to use the latest stable version.
* As a developer of the import script, you can select a branch on which you're
  implementing fixes to the workflow, e.g. `fix-import-crash`.

"The name of the branch to import from" is where the updated UFOs will be taken
from, e.g. `fb-wip`. The name of the target branch will be derived from that by
prepending `import-`, e.g. `import-fb-wip`. The target branch will be created
if it does not exist, or updated with a new commit otherwise.

If all goes according to plan, the workflow will create a new `import-...` branch,
and you will have to open a PR for it (we can't do it automatically because of the CLA bot).
If a PR already exists, it will be updated.

Otherwise, check the CI log for the run (accessible at the link above) to investigate why it failed.

The designspaces imported are determined by the `sources/config.yaml` file.
To add a new designspace, update the file on the source branch (the one not starting `import-...`) and then run the import workflow again.
