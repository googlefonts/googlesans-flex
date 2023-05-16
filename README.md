# Google Sans Flex

## Building

Fonts are built automatically by GitHub Actions - take a look in the "Actions" tab for the latest build.

If you want to build fonts manually on your own computer:

* `make build` will produce font files.
* `make test` will run [FontBakery](https://github.com/googlefonts/fontbakery)'s quality assurance tests.
* `make proof` will generate HTML proof files.

## Releasing

To release, head to GitHub's releases page for the repo ([here](https://github.com/googlefonts/googlesans-flex/releases)).
Then:
1. Click "Draft a new release" (top right).
2. Open the dropdown "Choose a tag".
3. Either select the existing tag you want to make a release for, or type in the version you're releasing and then click "Create new tag: blah on publish".
4. Fill in the release title and description.
5. Adjust checkboxes for pre-release and latest as you see fit.
6. Click "Publish release".

That's everything you need to do done.
A GitHub workflow will kick off in the background which will compile the font and attach a .zip file to the GitHub release once complete.
You can track its progress [here](https://github.com/googlefonts/googlesans-flex/actions/workflows/build.yaml).

## Updating dependencies

Please run `make update` to update dependencies. This uses [pip-tools](https://github.com/jazzband/pip-tools) to resolve them and write them into the requirements.txt file. The requirements are then installed by the build scripting without further dependency resolution.

## Importing new sources

### From another branch on this repository

There it a GitHub workflow that covers this from start to finish, no local work required.
You can access it from [Actions > Update from sources > Run workflow](https://github.com/googlefonts/googlesans-flex/actions/workflows/import.yaml).

The "Use workflow from" determines which version of the import script will be used.
* As Marianna or Chris, you'll always want this to be `main`, to use the latest stable version.
* As a developer of the import script, you can select a branch on which you're
  implementing fixes to the workflow, e.g. `fix-import-crash`.

"The Git reference to import from" is where the updated UFOs will be taken
from, e.g. `fb-wip`. The name of the target branch will be derived from that by
prepending `import-`, e.g. `import-fb-wip`. The target branch will be created
if it does not exist, or updated with a new commit otherwise.

If all goes according to plan, the workflow will create a new `import-...` branch,
and you will have to open a PR for it (we can't do it automatically because of the CLA bot).
If a PR already exists, it will be updated.

Otherwise, check the CI log for the run (accessible at the link above) to investigate why it failed.

The designspaces imported are determined by the `sources/config.yaml` file.
To add a new designspace, update the file on the source branch (the one not starting `import-...`) and then run the import workflow again.

## Scripts

### find-problems.py

A script used to find angles (between the incoming and outgoing handles or point of an on-curve point) that statistically deviate from the same angle in other masters. Use like this:

1. First, `git clone https://github.com/BlackFoundryCom/fontra` somewhere and set it up inside a venv as described in [the Readme](https://github.com/BlackFoundryCom/fontra#install-from-the-source-code).
2. Then, start it by pointing it to the directory containing GoogleSansFlex.designspace, like so:
    * `fontra --launch filesystem ../googlesans-flex/sources/regular/`
3. In a separate terminal or tab, go to the root directory of GSF and activate the venv (e.g. run `make venv` and then `source venv/bin/activate`).
4. Run the script like this: `python scripts/find-problems.py ../googlesans-flex-fb-wip/sources/roman/GoogleSansFlex.designspace`. The Designspace can be anywhere, but the script should be run from your venv.
5. The script will create a CSV file where it lists glyph points and their locations where the angle of the incoming and outgoing handle or on-curve deviates from other masters. It gives you a link to click, which brings you to the glyph in Fontra and marks the offending point for you. Wiggle the location sliders to see if there is a problem or not.

You can also inspect variable TTFs. Note that the locations might be slightly off then.

### gs-ufo2glyphs.py, gs-glyphs2ufo.py, gs-merge-designspace.py

These work the same as in Google Sans.

This will produce a GoogleSansFlex.glyphs file next to the Designspace:

```sh
python3 scripts/gs-ufo2glyphs.py sources/regular/GoogleSansFlex.designspace
```

Going back should be done in a separate directory, because we have an extra merge step, to avoid polluting the sources with leftovers and accidents.

```sh
python3 scripts/gs-glyphs2ufo.py sources/regular/staging/GoogleSansFlex.glyphs
```

Merge the two with the following command. You need to have a import_glyphs.txt file describing which glyphs to import:

```sh
python3 scripts/gs-merge-designspace.py --source source/GoogleSans/staging/GoogleSansSomeScript.designspace --target sources/regular/GoogleSansFlex.designspace --import-glyphs-file sources/regular/staging/import_glyphs.txt
```
