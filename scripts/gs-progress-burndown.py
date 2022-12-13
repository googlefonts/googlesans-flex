# Copyright 2021 Google Sans Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import colorsys
import os
import posixpath
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import matplotlib.pyplot as plt
from ufoLib2.objects import Font, Glyph


@dataclass
class Config:
    repo_path: Path
    git_rev_since: str
    git_rev_current: str
    milestones: Sequence[Milestone]


@dataclass
class Milestone:
    name: str
    ufo_filter_predicate: Callable[[str], bool]
    start_date: datetime
    due_date: datetime
    total_ufos: int
    total_glyphs: int
    statuses: Sequence[Status]
    """Statuses ordered from most done to least done."""


SimpleColor = Literal["red", "yellow", "green", "blue", "purple"]


@dataclass
class Status:
    plot_color: str
    progress_percent: int
    mark_color: Optional[Union[SimpleColor, Tuple[float, float, float, float]]] = None
    lib_key_name: Optional[str] = None
    lib_key_value: Optional[Any] = None


# Small helper functions to count UFOs; they just return the number of args
def _count(*args):
    return len(args)


opsz = wdth = wght = ROND = ital = _count


# Green - design finished and ready for Google's review
# Yellow - in progress
# Red - not started
# Blue - in progress and for v1.1 ()
GSFLEX_CONFIG = Config(
    repo_path=Path(__file__).parent.parent,
    git_rev_since="Alpha-v1.0",
    git_rev_current="origin/fb-wip",
    milestones=[
        Milestone(
            name="Roman - version 1.000",
            start_date=datetime(2022, 10, 19),
            due_date=datetime(2023, 1, 16),
            total_glyphs=340,
            total_ufos=(
                opsz(6) * wdth(25, 100, 151) * wght(1, 400, 1000) * ROND(0, 100)
                # These two optical sizes have more widths (85 and 91.999), only in the ROND 0
                + opsz(18, 144)
                * wdth(25, 85, 91.9999, 100, 151)
                * wght(1, 400, 1000)
                * ROND(0)
                # These two optical sizes have 3 widhts in the ROND 100
                + opsz(18, 144) * wdth(25, 100, 151) * wght(1, 400, 1000) * ROND(100)
            ),
            ufo_filter_predicate=lambda path: (
                ("sources/regular" in path or "sources/roman" in path)
                and "GRAD" not in path
            ),
            statuses=[
                Status(
                    plot_color="green",
                    progress_percent=100,
                    mark_color="green",
                ),
                Status(
                    plot_color="yellow",
                    progress_percent=50,
                    mark_color="yellow",
                ),
                Status(plot_color="red", progress_percent=0),
            ],
        ),
        Milestone(
            name="Version 1.100",
            start_date=datetime(2022, 12, 19),
            due_date=datetime(2023, 2, 28),
            total_glyphs=340,
            total_ufos=(
                opsz(6, 18, 144)
                * wdth(25, 100, 151)
                * wght(1, 400, 1000)
                * ROND(0, 100)
                * ital(0, 1)
            ),
            ufo_filter_predicate=lambda path: (
                "sources/italic" in path and "GRAD" not in path
            ),
            statuses=[
                Status(
                    plot_color="green",
                    progress_percent=100,
                    mark_color="green",
                ),
                Status(
                    plot_color="blue",
                    progress_percent=50,
                    mark_color="blue",
                ),
                Status(plot_color="red", progress_percent=0),
            ],
        ),
    ],
)


def main() -> None:
    config = GSFLEX_CONFIG
    counts_by_date_by_milestone: List[Dict[datetime, List[int]]] = [
        defaultdict(lambda: [0 for _ in milestone.statuses])
        for milestone in config.milestones
    ]
    # Data just for testing the graph
    # counts_by_date_by_milestone = [
    #     {
    #         datetime(2022, 12, 1): [0, 1000, 40000],
    #         datetime(2022, 12, 10): [1000, 20000, 20000],
    #         datetime(2022, 12, 20): [11000, 20000, 10000],
    #         datetime(2022, 12, 30): [31000, 10000, 0],
    #     },
    #     {
    #         datetime(2022, 12, 1): [0, 1000, 40000],
    #         datetime(2022, 12, 10): [1000, 20000, 20000],
    #         datetime(2022, 12, 20): [11000, 20000, 10000],
    #         datetime(2022, 12, 30): [31000, 10000, 0],
    #     },
    # ]
    print("Preparing git worktree")
    for tmpdir, date in iter_revisions(
        config.repo_path, config.git_rev_since, config.git_rev_current
    ):
        glyph_instances_in_last_revision_per_milestone = [0 for _ in config.milestones]
        print("Opening UFOs", end="")
        for ufo_path in tmpdir.glob("**/*.ufo"):
            milestones_for_ufo = [
                (i, milestone)
                for (i, milestone) in enumerate(config.milestones)
                if milestone.ufo_filter_predicate(posix(ufo_path))
            ]
            if not milestones_for_ufo:
                continue
            ufo = Font.open(ufo_path)
            print(".", end="")
            for glyph in ufo:
                for i, milestone in milestones_for_ufo:
                    glyph_instances_in_last_revision_per_milestone[i] += 1
                    counts = counts_by_date_by_milestone[i][date]
                    for j, status in enumerate(milestone.statuses):
                        if glyph_matches_status(glyph, status):
                            counts[j] += 1
                            break
        print(" done")
    for i, milestone in enumerate(config.milestones):
        print(
            f"Milestone #{i} {milestone.name}: "
            f"expected {milestone.total_glyphs*milestone.total_ufos} instances, "
            f"found {glyph_instances_in_last_revision_per_milestone[i]} "
            f"glyph instances in the last revision."
        )
        plot_to_images(
            milestone,
            counts_by_date_by_milestone[i],
            glyph_instances_in_last_revision_per_milestone[i],
            Path("."),
        )


@dataclass
class Repo:
    path: Path

    def git(self, *args: str, check=True) -> str:
        command = ["git", "-C", str(self.path), *args]
        # print(f"Running {' '.join(command)}")
        res = run(command, check=check, capture_output=True, encoding="utf-8")
        return res.stdout


def iter_revisions(repo_path, rev_since, rev_current):
    """Iterate through the given git revisions, and for each checkout the
    repository into a temp folder and yield that, along with the date of the
    revision.
    """
    repo = Repo(repo_path)
    out = repo.git("rev-list", "--format=tformat:%H %aI", f"{rev_since}..{rev_current}")
    shas_and_dates = []
    for line in out.splitlines():
        if line.startswith("commit"):
            continue
        sha, date_iso = line.split(maxsplit=1)
        shas_and_dates.append((sha, datetime.fromisoformat(date_iso)))
    try:
        with TemporaryDirectory() as tmpdir:
            repo.git("worktree", "add", "-d", tmpdir, shas_and_dates[0][0])
            worktree = Repo(tmpdir)
            for i, (sha, date) in enumerate(shas_and_dates):
                print(f"Processing commit {i+1}/{len(shas_and_dates)}")
                worktree.git("checkout", "-d", sha)
                yield Path(tmpdir), date
    finally:
        repo.git("worktree", "remove", tmpdir, check=False)


# Adapted from https://github.com/fonttools/fonttools/blob/main/Lib/fontTools/designspaceLib/__init__.py#L47
def posix(path: Path) -> str:
    """Normalize paths using forward slash to work also on Windows."""
    new_path = posixpath.join(*str(path).split(os.path.sep))
    if str(path).startswith("/"):
        # The above transformation loses absolute paths
        new_path = "/" + new_path
    elif str(path).startswith(r"\\"):
        # The above transformation loses leading slashes of UNC path mounts
        new_path = "//" + new_path
    return new_path


def glyph_matches_status(glyph: Glyph, status: Status) -> bool:
    if status.mark_color is not None:
        if glyph.markColor is None:
            return False
        r, g, b, _a = parse_mark_color(glyph.markColor)
        if isinstance(status.mark_color, str):
            return describe_color(r, g, b) == status.mark_color
        return (r, g, b) == status.mark_color[:3]
    if status.lib_key_name is not None:
        return glyph.lib.get(status.lib_key_name, None) == status.lib_key_value
    # Catch-all state
    return True


def parse_mark_color(color: str) -> Tuple[float, float, float, float]:
    # https://unifiedfontobject.org/versions/ufo3/conventions/#colors
    r, g, b, a = color.split(",")
    return float(r), float(g), float(b), float(a)


def plot_to_images(
    milestone: Milestone,
    counts_by_date: Mapping[datetime, Sequence[int]],
    total_glyph_instances: int,
    images_path: Path,
):
    # Example code from https://matplotlib.org/stable/gallery/lines_bars_and_markers/stackplot_demo.html#sphx-glr-gallery-lines-bars-and-markers-stackplot-demo-py
    dates = []
    counts_by_status: List[List[int]] = [[] for _ in milestone.statuses]
    for date, counts in sorted(counts_by_date.items()):
        dates.append(date)
        for i, count in enumerate(counts):
            counts_by_status[i].append(count)

    fig, ax = plt.subplots()
    fig.set_size_inches(16, 9)
    ax.stackplot(
        dates,
        counts_by_status,
        colors=[status.plot_color for status in milestone.statuses],
    )
    ax.plot(
        [milestone.start_date, milestone.due_date],
        [0, total_glyph_instances],
    )
    ax.set_title(f"Progress towards milestone: {milestone.name}")
    ax.set_xlabel("Commit date")
    ax.set_ylabel("Number of glyph sources")
    ax.tick_params(axis="x", labelrotation=50)

    fig.tight_layout()
    fig.savefig(images_path / f"{sanitize(milestone.name)}_counts.png")

    # ====================================
    dates = []
    progresses_by_status: List[List[float]] = [[] for _ in milestone.statuses]
    for date, counts in sorted(counts_by_date.items()):
        dates.append(date)
        for i, (count, status) in enumerate(zip(counts, milestone.statuses)):
            progresses_by_status[i].append(count * status.progress_percent / 100.0)

    fig, ax = plt.subplots()
    fig.set_size_inches(16, 9)
    ax.stackplot(
        dates,
        progresses_by_status,
        colors=[status.plot_color for status in milestone.statuses],
    )
    ax.plot(
        [milestone.start_date, milestone.due_date],
        [0, total_glyph_instances],
    )
    ax.set_title(f"Progress towards milestone: {milestone.name}")
    ax.set_xlabel("Commit date")
    ax.set_ylabel("Progress on glyph sources")
    ax.tick_params(axis="x", labelrotation=50)

    fig.tight_layout()
    fig.savefig(images_path / f"{sanitize(milestone.name)}_progress.png")


def sanitize(string: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.\-]+", "_", string)


# https://en.wikipedia.org/wiki/Hue#24_hues_of_HSL/HSV
HUE_TO_COLOR: List[Tuple[int, SimpleColor]] = [
    (30, "red"),  # Up to 30°, classify as red
    (75, "yellow"),
    (165, "green"),
    (255, "blue"),
    (315, "purple"),
    (360, "red"),
]


def describe_color(r: float, g: float, b: float) -> SimpleColor:
    h, _l, _s = colorsys.rgb_to_hls(r, g, b)
    for degrees, color_name in HUE_TO_COLOR:
        if h <= degrees / 360.0:
            return color_name
    return HUE_TO_COLOR[-1][1]


# Colors found in fb-wip branch:
# [(10, '0.2288,1,0.4511,1', '#3AFF73FF'),
assert describe_color(0.2288, 1, 0.4511) == "green"
#  (18, '0.9908,1,0.037,1', '#FDFF09FF'),
assert describe_color(0.9908, 1, 0.037) == "yellow"
#  (49, '0.8687,0.1142,0.999,1', '#DE1DFFFF'),
assert describe_color(0.8687, 0.1142, 0.999) == "purple"
#  (200, '1,0,0,1', '#FF0000FF'),
assert describe_color(1, 0, 0) == "red"
#  (244, '1,1,0,1', '#FFFF00FF'),
assert describe_color(1, 1, 0) == "yellow"
#  (349, '0,0,1,1', '#0000FFFF'),
assert describe_color(0, 0, 1) == "blue"
#  (1257, '0.0941,0.7922,0.9961,1', '#18CAFEFF'),
assert describe_color(0.0941, 0.7922, 0.9961) == "blue"
#  (1800, '0.884,0.8791,0.0317,1', '#E1E008FF'),
assert describe_color(0.884, 0.8791, 0.0317) == "yellow"
#  (2361, '0.1227,0.9628,0.999,1', '#1FF6FFFF'),
assert describe_color(0.1227, 0.9628, 0.999) == "blue"
#  (4020, '0.2431,0.9922,0.5255,1', '#3EFD86FF'),
assert describe_color(0.2431, 0.9922, 0.5255) == "green"
#  (4304, '0.1313,0.9997,0.0236,1', '#21FF06FF')]
assert describe_color(0.1313, 0.9997, 0.0236) == "green"


if __name__ == "__main__":
    main()
