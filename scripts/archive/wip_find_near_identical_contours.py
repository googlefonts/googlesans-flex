# Copyright 2024 Google Sans Flex Authors
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

"""
Rough script to detect similar contours across glyphs, to show where components
may reduce file size.
"""

from dataclasses import dataclass
from typing import Iterable, NamedTuple
from fontTools.designspaceLib import DesignSpaceDocument
from ufoLib2 import Font
from ufoLib2.objects import Layer, Point


DEVIATION_THRESHOLD = (20.0, 20.0)
THRESHOLD_X, THRESHOLD_Y = DEVIATION_THRESHOLD


# FIXME: this needs to be a 2D co-ordinate not single float
@dataclass(frozen=True)
class RangedFloat(NamedTuple):
    low: float
    high: float

    # FIXME doesn't check threshold
    def could_fit(self, value: float) -> bool:
        return value >= self.low and value <= self.high

    def _remaining_space(self) -> float:
        pass


class ApproximateCounter:
    _buckets: dict[
        # the largest and smallest values contained in this bucket
        RangedFloat,
        # all the values within the bucket with their source information
        list[tuple[float, str | None]],
    ] = {}

    def add(self, value: float, source: str | None = None) -> bool:
        relevant_bucket_values = []
        for bucket, bucket_values in self._buckets.items():
            if value in bucket:
                relevant_bucket_values = bucket_values
                break
        relevant_bucket_values.append((value, source))
        
        # TODO: finish


def get_layers(doc: DesignSpaceDocument) -> list[Layer]:
    return [
        (
            source.font.layers.defaultLayer  # type: ignore
            if source.layerName is None
            else source.font.layers[source.layerName]  # type: ignore
        )
        for source in doc.sources
    ]


def deviation(points: Iterable[Point]) -> tuple[float, float]:
    x_min = min(point.x for point in points)
    x_max = max(point.x for point in points)
    y_min = min(point.y for point in points)
    y_max = max(point.y for point in points)
    return (abs(x_max - x_min), abs(y_max - y_min))


def suspicious(deltas: Iterable[tuple[float, float]]) -> bool:
    """All deviations are under the threshold of "probably intentional" but
    there are some non-zero"""
    threshold_x, threshold_y = DEVIATION_THRESHOLD
    non_zero = False
    for dx, dy in deltas:
        if dx > 0.0 or dy > 0.0:
            non_zero = True
        # FIXME: this is fundamentally broken as there are always expected
        #        outliers
        # if dx > threshold_x or dy > threshold_y:
        #     return False
    return non_zero


def main(doc: DesignSpaceDocument):
    layers = get_layers(doc)
    unexported = set(doc.lib.get("public.skipExportGlyphs", []))
    glyph_names = {glyph for layer in layers for glyph in layer.keys()} - unexported

    for glyph_name in sorted(glyph_names):
        clustered_points: list[
            # All the contours of a given index (i.e. all the first contours,
            # then all the second contours)
            list[
                # The different point lists for that contour, 'tagged' with
                # their layer
                tuple[tuple[Point], Layer],
            ],
        ] = []
        for layer in layers:
            if glyph := layer.get(glyph_name):
                for contour_index, contour in enumerate(glyph):
                    tup = (tuple(contour.points), layer)
                    try:
                        clustered_points[contour_index].append(tup)
                    except IndexError:
                        clustered_points.append([tup])

        for contour_index, points_layer in enumerate(clustered_points):
            deltas = [deviation(points) for points in next(zip(*points_layer))]
            if suspicious(deltas):
                print(glyph_name)
                for point_index, (dx, dy) in enumerate(deltas):
                    if dx > 0 or dy > 0:
                        layer = points_layer[point_index][1]
                        print(
                            f"  - {layer.name} contour {contour_index} point {point_index}"
                        )
                print()


if __name__ == "__main__":
    doc = DesignSpaceDocument.fromfile("sources/GoogleSansFlex.designspace")
    doc.loadSourceFonts(Font.open)
    main(doc)
