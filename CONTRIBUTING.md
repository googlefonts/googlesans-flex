Want to contribute? Great! First, read this page (including the small print
at the end).

# Font source changes

Beyond the usual changes made using your font editor, there may be some additional changes to make in order for the pipeline to pass.

## Formatting sources

If you want any changes to the Designspace or UFOs, please run `scripts/gs-normalize-designspace.py` to reformat everything appropriately.

## Adding/Removing glyphs

For glyphs with overlap, please add the name to `sources/glyphs-with-overlap.txt`.
Glyphs with overlap are not currently detected automatically.

We track glyph set changes in the `qa/definitions` folder.
If you're adding, removing, or otherwise changing the glyph order, you need to build all TTFs and then run `scripts/gs-update-glyphset-qa-files.py`.
Please check the changes to the glyph sets are as you expect before committing.

## Shaping changes (feature code, respacing, et. al)

We have a regression testing suite built on HarfBuzz that integrates with Fontbakery, which lives under `qa/shaping`.
To update the expectations, you need all the TTFs built, and then to run `update_all_shaping.sh` from within the `qa` folder.
Please check the shaping changes match your expectations before committing.

If you're adding or removing feature code, you may also want to update the test strings and configurations for these shaping tests.
For this, you're looking in `qa/shaping_input` for a relevant TOML file for the feature you're updating.
If one doesn't exist, create it.
Looking at other configurations will give you an idea of what's supported.
After making changes, don't forget to run the `update_all_shaping.sh` script as previously described.

# Contributor License Agreement

Before we can use your code, you must sign the
[Google Individual Contributor License
Agreement](https://cla.developers.google.com/about/google-individual) 
(CLA), which you can do online. The CLA is necessary mainly because you own the
copyright to your changes, even after your contribution becomes part of our
codebase, so we need your permission to use and distribute your code. We also
need to be sure of various other things—for instance that you'll tell us if you
know that your code infringes on other people's patents. You don't have to sign
the CLA until after you've submitted your code for review and a member has
approved it, but you must do it before we can put your code into our codebase.
Before you start working on a larger contribution, you should get in touch with
us first through the issue tracker with your idea so that we can help out and
possibly guide you. Coordinating up front makes it much easier to avoid
frustration later on.

# Code reviews

All submissions, including submissions by project members, require review.
We use GitHub pull requests for this purpose.

---

### The small print

Contributions made by corporations are covered by a different agreement than
the one above, the [Software Grant and Corporate Contributor License
Agreement](https://cla.developers.google.com/about/google-corporate).

Also see [TRADEMARKS.md](/TRADEMARKS.md) regarding naming issues.
