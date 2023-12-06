# Google Sans Flex

## Building

### On GitHub

Fonts are built by triggering the build workflow in the [Actions tab](https://github.com/googlefonts/googlesans-flex/actions) of the repository.

1. Go to the [Actions tab](https://github.com/googlefonts/googlesans-flex/actions)
2. Click [Build font and specimen](https://github.com/googlefonts/googlesans-flex/actions/workflows/build.yaml)
3. Click the grey "Run workflow" dropdown button
4. Enter the name of the branch or commit you want to build in the text box
5. Press the green "Run workflow" button

#### How the CI pipeline builds the font

1. Create/Activate venv*
2. Install requirements.txt*
3. (if release) [`bumpfontversion`](https://github.com/simoncozens/bumpfontversion) sets the font version in the sources based on the tag name
4. Call gftools builder*
5. [font-v](https://github.com/source-foundry/font-v) sets TTF version strings
6. [`scripts/prune_font_binary.py`](./scripts/prune_font_binary.py) removes unused/unencoded glyphs from TTFs
7. [`scripts/set-overlap-bits.py`](./scripts/set-overlap-bits.py) adjusts overlap flags in the GLYF table
8. [OT Sanitizer](https://github.com/khaledhosny/ots) validates & sanitizes the TTFs
9. TTFs are archived for download (along with QA reports if not a release)

(*This is the part of the process [`fontc`](https://github.com/googlefonts/fontc) would speed-up/replace)

### On your computer

* `make build` will produce font files.
* `make test` will run [FontBakery](https://github.com/googlefonts/fontbakery)'s quality assurance tests.

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

### gs-progress-burndown.py

This script generates a burndown chart to show the font's development progress based on color marks left in the sources by font developers.
The script is configured entirely within the code (see the `GSFLEX_CONFIG` object in the file `scripts/gs-progress-burndown.py`).
For more information about the configuration of the script, please refer to the document `scripts/gs-progress-burndown-README.md`.

The script can be run locally by running `make progress-chart`

The GitHub workflow to run the script is called "Progress chart", and can be found [here](https://github.com/googlefonts/googlesans-flex/actions/workflows/burndown.yml).
The "Use workflow from" field determines *which version of the script to use, **not** the branch to generate the burndown chart for*. Currently, you should select `main` because the `main` branch has the latest version of the workflow.


The branch that is analysed to produce the burndown chart is configured within the script itself (see `git_rev_since` and `git_rev_current`).
To temporarily produce a burndown chart for a different branch on your local machine, simply update these two values to valid Git references (i.e. branch names or 7 character hashes), and run `make progress-chart`.
Updating the workflow's configuration will require a PR changing the script.
