# Progress burndown chart generator script

## What it does

The script generates a chart showing completed glyphs over time.
It does this by reading color mark info out of UFO sources, using git to see what's changed over time.
Milestones can be added to the chart for ease of tracking progress towards a goal.

## How it works

For each commit in the specified range*:

1. Create a [git worktree](https://git-scm.com/docs/git-worktree)
2. Count the number of glyphs with each recognised color mark

Then, using the counts along with the commit dates, plots a chart to show progress

(* if there are multiple commits in a single calendar day, only the last one is considered, as a time saving measure)

## How to configure it

The bulk of desired configuration can be done by changing the `Config` dataclass that's assigned as `config` in `main()`.

`Config` fields include:
* `repo_path: Path`: the directory in which the project UFOs can be found
* `git_rev_since: str`: the git revision to start the chart at (i.e. the first commit to analyse)
* `git_rev_current: str`: the git revision to end the chart at, typically a branch name
* `ufo_finder: (Path -> list[Path])`: a Python function that searches the given `Path` for UFOs, returning a list of `.ufo` paths
* `statuses: list[Status]`: see Status heading
* `milestones: list[Milestone]`: see Milestone heading

### `Status`

* `name: str`: the name of the group of glyphs with a given color (shown in the legend of the chart)
* `plot_color: str`: the hex color (with `#` prefix) of the area of the chart for these glyphs
* `glyph_type: GlyphType (Literal[str])`: the type of glyph, which must be mapped in the constant `GLYPH_TYPES` in order to be detected. Currently "drawn" and "composite" are supported
* `mark_color: SimpleColor (Literal[str])`: the name of the color of the mark. Colors that can be used must be defined in the type and the constant `HUE_TO_COLOR`

### `Milestone`

Trendlines drawn to indicate estimated/target progress.
Trendlines will start at 0 unless `starts_from_previous` is set to `True`.
The y axis "Number of glyph sources" is calculated by multiplying `total_glyphs` and `total_ufos`.

* `name: str`: the name of the milestone (shown at the end of the trendline)
* `plot_color: str`: the hex color (with `#` prefix) to drawn the line
* `start_date: Optional[datetime]`: the start date for the target. Can be excluded if `starts_from_previous` is `True`
* `starts_from_previous: Optional[bool]`: indicates whether to start the current milestone from the previous one. Can be excluded if `start_date` is set
* `due_date: datetime`: the deadline for the milestone (where the line will end on the x axis)
* `total_glyphs: int`: the number of glyphs expected to be in a single master when the milestone is complete
* `total_ufos: int`: the number of masters/UFOs there are expected to be when the milestone is complete
