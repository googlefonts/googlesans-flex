# Copyright 2022 Google Sans Authors
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


"""Highlight statistical outliers in the Designspace.

They may or may not indicate interpolation issues and have to be checked by
hand.
"""


# Plan:
# For each glyph:
#   For each node:
#      gather properties of the nodes from all UFOs that have this glyph
#      For each property:
#         look for outliers = a couple UFOs where the property has a different value than in most


# Ideas for properties:
# * angle of the triplet of points (prev point + current + next point) = can spot issues with colinearity for example
# * is the node occluded/hidden inside a stroke? (would spot nodes that "poke out" in some part of the designspace)
# * for both incoming segment and outgoing segment separately:
#   * "curviness" (= in all UFOs it's a curvy segment except in one it's straight = forgot to round one UFO?)

# pyright: basic
from __future__ import annotations

import argparse
import csv
import itertools
import json
import urllib.parse
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
from fontTools.designspaceLib import DesignSpaceDocument
from ufoLib2 import Font
from ufoLib2.objects import Contour, Glyph, Point


Location = Tuple[Tuple[str, float], ...]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("designspace", type=Path)
    parser.add_argument(
        "--outfile",
        type=Path,
        default=Path(
            f"find-smooth-unsmooth-{datetime.now().isoformat(timespec='seconds').replace(':', '-')}.csv"
        ),
    )
    parsed_args = parser.parse_args()
    designspace_path: Path = parsed_args.designspace
    designspace = DesignSpaceDocument.fromfile(designspace_path)
    designspace.loadSourceFonts(Font.open)

    reports = []
    for axis_focus in ({"ROND": 0.0}, {"ROND": 100.0}):
        default_location = designspace.newDefaultLocation()
        default_location.update(axis_focus)

        default_source = next(
            iter(s for s in designspace.sources if s.location == default_location)
        )
        assert default_source is not None
        assert default_source.font is not None
        glyph_names = default_source.font.keys()

        name2tag = {a.name: a.tag for a in designspace.axes}
        for name in glyph_names:
            default_glyph = default_source.font[name]
            if not default_glyph.contours:
                continue
            reference = curve_points(default_glyph)
            for source in designspace.sources:
                if source is default_source:
                    continue
                if not set(axis_focus.items()).issubset(
                    source.getFullDesignLocation(designspace).items()
                ):
                    continue

                location_key = tuple(
                    (name2tag[name], value) for name, value in source.location.items()
                )
                assert source.font is not None
                if source.layerName is None:
                    glyphset = source.font
                else:
                    glyphset = source.font.layers[source.layerName]
                other = curve_points(glyphset[name])
                if not all(
                    len(reference) > contour_id
                    and relevant_points.keys() == reference[contour_id].keys()
                    for contour_id, relevant_points in enumerate(other)
                ):
                    print(f"Glyph {name} at {location_key} is incompatible")
                    continue
                outlier_counters_and_points: list[tuple[int, list[int]]] = []
                for contour_idx, (contour_ref, contour_other) in enumerate(
                    zip(reference, other)
                ):
                    outlier_points = []
                    for point_idx, smooth in contour_ref.items():
                        smooth_other = contour_other[point_idx]
                        if smooth_other != smooth:
                            outlier_points.append(point_idx)
                    if outlier_points:
                        outlier_counters_and_points.append(
                            (contour_idx, outlier_points)
                        )
                if outlier_counters_and_points:
                    reports.append(
                        Report(
                            glyph_name=name,
                            code_points=[],
                            points=outlier_counters_and_points,
                            axis_focus=axis_focus,
                            location=dict(location_key),
                        )
                    )

    with open(parsed_args.outfile, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "glyph_name",
                "list of contour, on-curve points",
                "axis_focus",
                "location",
                "fontra_url",
                "videoproof_url",
            ]
        )
        for r in sorted(reports, key=lambda r: (r.glyph_name)):
            writer.writerow(
                [
                    r.glyph_name,  # "glyph_name",
                    r.points,  # "points",
                    r.axis_focus,  # "axis_focus",
                    r.location,  # "location",
                    f"""=HYPERLINK("{r.get_fontra_url().replace('"', '""')}")""",  # "fontra_url",
                    f"""=HYPERLINK("{r.get_videoproof_url().replace('"','""')}")""",  # "videoproof_url",
                ]
            )


def curve_points(glyph: Glyph) -> list[dict[int, bool]]:
    return [
        {
            point_index: point.smooth
            for point_index, point in enumerate(
                point for point in contour if point.segmentType is not None
            )
        }
        for contour in glyph.contours
    ]


@dataclass
class Report:
    glyph_name: str
    code_points: List[int]
    points: Optional[List[Tuple[int, list[int]]]]
    axis_focus: Dict[str, float]
    location: Dict[str, float]

    def get_fontra_url(self):
        params = urllib.parse.urlencode(
            {
                "text": f'"/{self.glyph_name}"',
                "location": json.dumps(self.location),
            }
        )
        return f"http://localhost:8000/editor/-/GoogleSansFlex.designspace?{params}"

    def get_videoproof_url(self):
        # Example: opsz6,wdth66,wght803
        location = urllib.parse.quote(
            ",".join(f"{tag}{value}" for tag, value in self.location.items())
        )
        text = urllib.parse.quote(
            "".join(chr(code_point) for code_point in self.code_points)
        )
        return f"https://videoproof.graphicore.de/#2022-12-14T11:08:44Z;GoogleSansFlex%20opsz18-wdth100-wght400-ROND0,Version%205.000;{location};type-your-own&{text};0"


if __name__ == "__main__":
    main()
