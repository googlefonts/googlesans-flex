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
from collections import defaultdict

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
from subprocess import run
from tempfile import TemporaryDirectory
from typing import Any, Callable, List, Mapping, Optional, Sequence

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
    ufo_filter_predicate: Callable[[Path], bool]
    due_date: datetime
    statuses: Sequence[Status]
    """Statuses ordered from most done to least done."""


@dataclass
class Status:
    plot_color: str
    progress_percent: int
    mark_color: Optional[str] = None
    lib_key_name: Optional[str] = None
    lib_key_value: Optional[Any] = None


# RoboCJK not using UFOs
# ROBOCJK_CONFIG = Config(
#     git_rev_since="main",
#     git_rev_current="master",
#     milestones=[
#         Milestone(
#             name="Test milestone",
#             ufo_filter_predicate:
#             due_date=datetime.now(),
#             statuses=[
#                 Status(plot_color="green")
#             ],
#         )
#     ],
# )

# Green - design finished and ready for Google's review
# Yellow - in progress
# Red - not started
# Blue - in progress and for v1.1 ()
GSFLEX_CONFIG = Config(
    repo_path=Path(__file__).parent.parent,
    git_rev_since="main",
    git_rev_current="fb-wip",
    milestones=[
        Milestone(
            name="Roman - version 1.000",
            due_date=datetime(2023, 1, 16),
            ufo_filter_predicate=lambda path: "Italic" not in str(path),
            statuses=[
                Status(plot_color="green", progress_percent=100, mark_color="green"),
                Status(plot_color="yellow", progress_percent=50, mark_color="yellow"),
                # Status(plot_color="red", progress_percent=0, mark_color="red"),
            ],
        ),
        Milestone(
            name="Version 1.100",
            due_date=datetime(2023, 2, 28),
            ufo_filter_predicate=lambda path: True,
            statuses=[
                Status(plot_color="green", progress_percent=100, mark_color="green"),
                Status(plot_color="blue", progress_percent=50, mark_color="blue"),
                # Status(plot_color="red", progress_percent=0, mark_color="red"),
            ],
        ),
    ],
)


def main():
    config = GSFLEX_CONFIG
    for milestone in config.milestones:
        counts_by_date = {}
        for tmpdir, date in iter_revisions(
            config.repo_path, config.git_rev_since, config.git_rev_current
        ):
            counts = [0 for _ in milestone.statuses]
            for ufo in iter_ufos(milestone, tmpdir):
                for glyph in ufo:
                    for i, status in enumerate(milestone.statuses):
                        if glyph_matches_status(glyph, status):
                            counts[i] += 1
                            break
            counts_by_date[date] = counts
        plot_to_images(milestone, counts_by_date, Path("."))


@dataclass
class Repo:
    path: Path

    def git(self, *args, check=True) -> str:
        res = run(
            ["git", "-C", str(self.path), *args],
            check=check,
            capture_output=True,
            encoding="utf-8",
        )
        return res.stdout


def iter_revisions(repo_path, rev_since, rev_current):
    """Iterate through the given git revisions, and for each checkout the
    repository into a temp folder and yield that, along with the date of the
    revision.
    """
    repo = Repo(repo_path)
    out = repo.git(
        "rev-list", "--format=format:%H %ai%n", f"{rev_since}..{rev_current}"
    )
    shas_and_dates = []
    for line in out.splitlines():
        sha, date_iso = line.split(maxsplit=1)
        shas_and_dates.append((sha, datetime.fromisoformat(date_iso)))
    try:
        with TemporaryDirectory() as tmpdir:
            repo.git("worktree", "add", "-d", tmpdir, shas_and_dates[0][0])
            worktree = Repo(tmpdir)
            for sha, date in shas_and_dates:
                worktree.git("checkout", "-d", sha)
                yield Path(tmpdir), date
    finally:
        repo.git("worktree", "remove", tmpdir, check=False)


def iter_ufos(milestone: Milestone, path: Path):
    for ufo_path in path.glob("**/*.ufo"):
        if not milestone.ufo_filter_predicate(ufo_path):
            continue
        ufo = Font.open(ufo_path)
        yield ufo


def glyph_matches_status(glyph: Glyph, status: Status) -> bool:
    if status.mark_color is not None:
        return glyph.markColor == status.mark_color
    if status.lib_key_name is not None:
        return glyph.lib.get(status.lib_key_name, None) == status.lib_key_value
    raise Exception(f"Status {status} needs either a mark_color or a lib_key_name")


def plot_to_images(
    milestone: Milestone,
    counts_by_date: Mapping[datetime, Sequence[int]],
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
    ax.stackplot(
        dates,
        counts_by_status,
        colors=[status.plot_color for status in milestone.statuses],
    )
    ax.set_title(f"Milestone: {milestone.name}")
    ax.set_xlabel("Commit date")
    ax.set_ylabel("Number of glyph sources")

    plt.savefig(images_path / f"{sanitize(milestone.name)}_counts.png")

    # ====================================
    dates = []
    progresses_by_status: List[List[float]] = [[] for _ in milestone.statuses]
    for date, counts in sorted(counts_by_date.items()):
        dates.append(date)
        for i, (count, status) in enumerate(zip(counts, milestone.statuses)):
            progresses_by_status[i].append(count * status.progress_percent / 100.0)

    fig, ax = plt.subplots()
    ax.stackplot(
        dates,
        progresses_by_status,
        colors=[status.plot_color for status in milestone.statuses],
    )
    ax.set_title(f"Milestone: {milestone.name}")
    ax.set_xlabel("Commit date")
    ax.set_ylabel("Progress on glyph sources")

    plt.savefig(images_path / f"{sanitize(milestone.name)}_progress.png")


def sanitize(string: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.\-]+", "_", string)
