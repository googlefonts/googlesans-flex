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

This script assumes that a Fontra instance is running in the background,
pointing at `sources/regular/`, like so from the fontra repository:

    > hatch run fontra --launch filesystem ../googlesans-flex/sources/regular/
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
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from functools import singledispatch
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Tuple

import numpy as np
from fontTools.designspaceLib import DesignSpaceDocument
from fontTools.pens.pointInsidePen import PointInsidePen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._f_v_a_r import table__f_v_a_r
from fontTools.ttLib.tables._g_v_a_r import table__g_v_a_r
from fontTools.varLib.models import piecewiseLinearMap
from ufoLib2 import Font
from ufoLib2.objects import Contour, Glyph, Point

Location = Mapping[str, float]
LocationKey = Tuple[Tuple[str, float], ...]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source", type=Path, help="Designspace or variable font to check."
    )
    parser.add_argument(
        "--outfile",
        type=Path,
        default=Path(
            f"find-problems-{datetime.now().isoformat(timespec='seconds').replace(':', '-')}.csv"
        ),
    )
    parsed_args = parser.parse_args()
    font_source: DesignSpaceDocument | TTFont
    font_source_path: Path = parsed_args.source
    if font_source_path.suffix == ".designspace":
        font_source = DesignSpaceDocument.fromfile(font_source_path)
        font_source.loadSourceFonts(Font.open)
    else:
        font_source = TTFont(font_source_path)

    reports = []
    for axis_focus in ({"ROND": 0.0}, {"ROND": 100.0}):
        props_by_name_by_point_by_source: dict[
            str, dict[int, dict[str, Dict[LocationKey, Any]]]
        ] = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
        for design_location, glyphset in glyphsets(font_source, axis_focus):
            key = location_key(design_location)
            for name, glyph in glyphset.items():
                props_by_name = props_by_name_by_point_by_source[name]
                for current_point_index, (prev, curr, next_) in on_curve_points(
                    glyph.contours
                ):
                    props_by_source = props_by_name[current_point_index]
                    props_by_source["angle"][key] = angle(prev, curr, next_)
                    # If points are occluded on-curves in all masters, skip
                    # later.
                    if prev.segmentType is not None and next_.segmentType is not None:
                        pip = PointInsidePen(glyphset, (prev.x, prev.y))
                        glyph.draw(pip)
                        prev_inside = pip.getResult()
                        pip = PointInsidePen(glyphset, (curr.x, curr.y))
                        glyph.draw(pip)
                        cur_inside = pip.getResult()
                        pip = PointInsidePen(glyphset, (next_.x, next_.y))
                        glyph.draw(pip)
                        next_inside = pip.getResult()
                        if prev_inside and cur_inside and next_inside:
                            props_by_source["obscured"][key] = True
                        else:
                            props_by_source["obscured"][key] = False
                    else:
                        props_by_source["obscured"][key] = None

        for (
            glyph_name,
            props_by_point_by_source,
        ) in props_by_name_by_point_by_source.items():
            for point, props_by_source in props_by_point_by_source.items():
                obscured_values = props_by_source["obscured"]
                if all(obscured_values.values()):
                    print(
                        f"Glyph {glyph_name}, point {point} is obscured in all masters, skipping"
                    )
                    continue
                for prop_name, values_by_source in props_by_source.items():
                    if prop_name == "obscured":
                        continue
                    # Find outliers
                    values = list(values_by_source.values())
                    mean = np.mean(values)
                    tolerance = 3
                    std = np.std(values)
                    if std <= 0.01 or np.isnan(mean):
                        # No variance = all the same
                        # NaNs = not applicable
                        continue
                    outliers = {
                        location: (value, abs((value - mean) / std))
                        for location, value in values_by_source.items()
                        if not (
                            mean - std * tolerance <= value <= mean + std * tolerance
                        )
                    }
                    for design_location, (prop_value, score) in outliers.items():
                        reports.append(
                            Report(
                                glyph_name=glyph_name,
                                point=point,
                                axis_focus=axis_focus,
                                location=dict(design_location),
                                prop_name=prop_name,
                                prop_mean=mean,
                                prop_value=prop_value,
                                score=score,
                            )
                        )

    with open(parsed_args.outfile, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "glyph_name",
                "point",
                "axis_focus",
                "location",
                "prop_name",
                "prop_mean",
                "prop_value",
                "score",
                "fontra_url",
                # "videoproof_url",
            ]
        )
        for r in sorted(
            reports, key=lambda r: (r.glyph_name, r.axis_focus.items(), -r.score)
        ):
            writer.writerow(
                [
                    r.glyph_name,  # "glyph_name",
                    r.point,  # "points",
                    r.axis_focus,  # "axis_focus",
                    r.location,  # "location",
                    r.prop_name,  # "prop_name",
                    r.prop_mean,  # "prop_mean",
                    r.prop_value,  # "prop_value",
                    r.score,  # "score",
                    f"""=HYPERLINK("{r.get_fontra_url().replace('"', '""')}")""",  # "fontra_url",
                    # f"""=HYPERLINK("{r.get_videoproof_url().replace('"','""')}")""",  # "videoproof_url",
                ]
            )


@singledispatch
def glyphsets(
    font_source: DesignSpaceDocument | TTFont, axis_focus: Location | None
) -> Iterable[tuple[Location, Mapping[str, Glyph]]]:
    raise NotImplementedError


@glyphsets.register
def _(
    font_source: DesignSpaceDocument, axis_focus: Location | None
) -> Iterable[tuple[Location, Mapping[str, Glyph]]]:
    name2tag = {a.name: a.tag for a in font_source.axes}
    for source in font_source.sources:
        assert source.font is not None
        location: Location = {  # type: ignore
            name2tag[k]: v for k, v in source.getFullDesignLocation(font_source).items()
        }
        if axis_focus is not None and not set(axis_focus.items()).issubset(
            location.items()
        ):
            continue
        glyphset: Mapping[str, Glyph]
        if source.layerName is None:
            glyphset = {glyph.name: glyph for glyph in source.font}
        else:
            glyphset = {
                glyph.name: glyph for glyph in source.font.layers[source.layerName]
            }
        yield location, glyphset


@glyphsets.register
def _(
    font_source: TTFont, axis_focus: Location | None
) -> Iterable[tuple[Location, Mapping[str, Glyph]]]:
    locations = font_user_locations(font_source)
    for location in locations:
        if axis_focus is not None and not set(axis_focus.items()).issubset(
            location.items()
        ):
            continue
        font_glyphset = font_source.getGlyphSet(location=location)
        glyphset = {}
        for name, glyph in font_glyphset.items():
            ufo_glyph = Glyph(name)
            glyph.drawPoints(ufo_glyph.getPointPen())
            glyphset[name] = ufo_glyph
        yield location, glyphset


def location_key(location: Location) -> LocationKey:
    return tuple(location.items())


# XXX: Need to convert to design location I think!
def font_user_locations(font: TTFont) -> list[Location]:
    gvar: table__g_v_a_r = font["gvar"]  # type: ignore
    fvar: table__f_v_a_r = font["fvar"]  # type: ignore
    axes_mapping = {
        a.axisTag: {-1: a.minValue, 0: a.defaultValue, 1: a.maxValue} for a in fvar.axes
    }
    default_location = {a.axisTag: 0 for a in fvar.axes}

    # Gather all "master" locations
    locs = set()
    for variations in gvar.variations.values():
        for var in variations:
            loc = []
            for tag, val in sorted(var.axes.items()):
                loc.append((tag, val[1]))
            locs.add(tuple(loc))

    # Rebuild locs as dictionaries
    new_locs: list[Location] = [{}]
    for loc in sorted(locs, key=lambda v: (len(v), v)):
        l = {}
        for tag, val in {**default_location, **dict(loc)}.items():
            axis_mapping = axes_mapping[tag]
            l[tag] = piecewiseLinearMap(val, axis_mapping)
        new_locs.append(l)
    locs = new_locs
    del new_locs
    # locs is all master locations now

    return locs


@dataclass
class Report:
    glyph_name: str
    point: int
    axis_focus: Dict[str, float] | None
    location: Dict[str, float]
    prop_name: str
    prop_mean: float | np.floating
    prop_value: float | str
    score: float

    def get_fontra_url(self) -> str:
        params = urllib.parse.urlencode(
            {
                "text": f'"/{self.glyph_name}"',
                "editing": json.dumps(True),
                "location": json.dumps(self.location),
                "selectedGlyph": json.dumps("0/0"),
                "selection": json.dumps([f"point/{self.point}"]),
            }
        )
        return f"http://localhost:8000/editor/-/GoogleSansFlex.designspace?{params}"

    # def get_videoproof_url(self) -> str:
    #     # Example: opsz6,wdth66,wght803
    #     location = urllib.parse.quote(
    #         ",".join(f"{tag}{value}" for tag, value in self.location.items())
    #     )
    #     text = urllib.parse.quote(
    #         "".join(chr(code_point) for code_point in self.code_points)
    #     )
    #     return f"https://videoproof.graphicore.de/#2022-12-14T11:08:44Z;GoogleSansFlex%20opsz18-wdth100-wght400-ROND0,Version%205.000;{location};type-your-own&{text};0"


def on_curve_points(
    contours: list[Contour],
) -> Iterable[tuple[int, tuple[Point, Point, Point]]]:
    current_point_index = 0
    for contour in contours:
        # Shift list by 1 element to make the first curr the first point:
        shifted_contour = contour[-1:] + contour[:-1]
        for prev, curr, next_ in zip(
            shifted_contour,
            itertools.islice(itertools.cycle(shifted_contour), 1, None),
            itertools.islice(itertools.cycle(shifted_contour), 2, None),
        ):
            if curr.segmentType is None:
                current_point_index += 1
                continue
            yield current_point_index, (prev, curr, next_)
            current_point_index += 1


def angle(p1: Point, p2: Point, p3: Point) -> float:
    incoming = (p2.x - p1.x, p2.y - p1.y)
    outgoing = (p3.x - p2.x, p3.y - p2.y)
    return np.arccos(
        np.dot(incoming, outgoing)
        / (np.linalg.norm(incoming) * np.linalg.norm(outgoing))
    )


def dist(p1: Point, p2: Point) -> np.floating:
    return np.linalg.norm((p2.x - p1.x, p2.y - p1.y))


if __name__ == "__main__":
    main()
