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

The "Use workflow from" determines the branch you're merging into.
For a new merge, you'll want this to be `main`.
To update an on-going merge, select the appropriate `import-` branch.

"The name of the branch to import from" is where the updated UFOs will be taken from, e.g. `fb-wip`.

If all goes according to plan, the workflow will open a new PR or update the existing one.
Otherwise, check the CI log for the run (accessible at the link above) to investigate why it failed.
