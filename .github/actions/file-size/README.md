# file-size GitHub action

Runs the `report-filesize.py` script on built TTFs, assumed to be within `/github/workspace/fonts`

## Running locally

Simply:

```sh
make file-size
```

The font will be built if it hasn't already

Alternatively, if you only want to run on select TTFs:

```sh
. venv/bin/activate
python .github/actions/file-size/report-filesize.py <path to TTF>...
```

## Maintenance

`requirements.txt` is currently maintained by hand.
Versions are pinned to ensure reproducible builds.
It's probably recommended to keep the versions inline with those that are used to build `<repo root>/requirements.txt`

The local invocation of the script that's in the Makefile relies on the assumption that the requirements of `report-filesize.py` is a subset of the main `requirements.txt` at the repo root, as it reuses the build venv to run
