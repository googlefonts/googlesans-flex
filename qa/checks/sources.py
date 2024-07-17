# Copyright 2023 Google Sans Authors
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

from typing import Iterable, Tuple, Union

from fontbakery import utils
from fontbakery.callable import check, condition
from fontbakery.message import Message
from fontbakery.status import FAIL, INFO, PASS, SKIP, WARN, Status
from fontbakery.testable import Designspace, Ufo
from fontTools.designspaceLib import DesignSpaceDocument
from ufoLib2 import Font

CheckStatus = Iterable[Tuple[Status, Union[Message, str]]]


@condition(Ufo)
def ufo_font(ufo: Ufo) -> Font:
    return Font.open(ufo.file)


@condition(Designspace)
def ds(designspace: Designspace) -> DesignSpaceDocument:
    d = DesignSpaceDocument.fromfile(designspace.file)
    d.loadSourceFonts(Font.open)
    return d


@check(id="com.google.fonts/check/googlesansflex/sources/same_tabular_width")
def check_same_tabular_widths(ufo_font: Font, config) -> CheckStatus:
    """Confirms that tabular glyphs have the same width within the same master."""
    EXCLUDED_TABULARS = {
        # Intentionally has a different width:
        # https://github.com/googlefonts/googlesans-flex/issues/937
        "space.tf",
    }

    warnings_by_layer = {}
    for layer in ufo_font.layers:
        tabulars = {name for name in layer.keys() if ".tf" in name} - EXCLUDED_TABULARS
        if not tabulars:
            continue

        if "zero.tf" in tabulars:
            width_glyph = "zero.tf"
        else:
            width_glyph = next(iter(tabulars))
        width = layer[width_glyph].width
        if width is None:
            yield (
                FAIL,
                f"layer {layer.name}: {width_glyph} has no width, stopping check",
            )
            return

        for name in tabulars:
            glyph = layer[name]
            if glyph.width != width:
                warnings_by_layer.setdefault(layer.name, []).append(
                    (name, glyph.width, width_glyph, width)
                )

    if not warnings_by_layer:
        yield PASS, "Tabular glyphs, if they exist, have the same width"
    else:
        for layer_name, warnings in warnings_by_layer.items():
            yield (
                FAIL,
                Message(
                    "mismatching-tabular-widths",
                    f"layer '{layer_name}':\n\n"
                    f"""{utils.bullet_list(config, [f"{name} ({width}) has different width than {ref_name} ({ref_width})"
                     for (name, width, ref_name, ref_width) in warnings])}""",
                ),
            )


@check(id="com.google.fonts/check/googlesansflex/sources/suspicious_kerning_values")
def check_suspicious_kerning_values(ufo_font: Font, config) -> CheckStatus:
    """Check for small and large kerning values outside a range and other
    things."""

    # Accept kerning values in the range [10, 200] for 1000 upM fonts.
    threshold_low = round(10 * ufo_font.info.unitsPerEm / 1000)
    threshold_high = round(200 * ufo_font.info.unitsPerEm / 1000)
    threshold = range(threshold_low, threshold_high + 1)

    def describe_pair(first: str, second: str) -> str:
        glyphs = []
        if first in ufo_font.groups:
            glyphs.append(ufo_font.groups[first][0])
        else:
            glyphs.append(first)
        if second in ufo_font.groups:
            glyphs.append(ufo_font.groups[second][0])
        else:
            glyphs.append(second)
        return "".join(f"/{name}" for name in glyphs)

    suspicious_kerning = []
    for (first, second), value in ufo_font.kerning.items():
        # NOTE: Disable this for now, kerning can be cleaned up later.
        # if value == 0:
        #     if first in ufo_font.groups and second in ufo_font.groups:
        #         yield WARN, f"Group-to-group pairs like {(first, second)} (e.g. {describe_pair(first, second)}) don't need zero values"
        if value == 0:
            continue
        if abs(value) not in threshold:
            suspicious_kerning.append(
                ((first, second), describe_pair(first, second), value)
            )

    if not suspicious_kerning:
        yield PASS, "No suspicion raised"
    else:
        yield (
            WARN,
            Message(
                "suspicious-kerning-values",
                f"Kerning values outside the accepted range of [{threshold_low}, {threshold_high}]:\n\n"
                f"""{utils.bullet_list(
                    config,
                    [
                        f"Pair {pair} (e.g. {example}): {value}"
                        for (pair, example, value) in suspicious_kerning
                    ],
                )}""",
            ),
        )


@check(id="com.google.fonts/check/googlesansflex/sources/same_kerning_groups")
def check_same_kerning_groups(ds: DesignSpaceDocument) -> CheckStatus:
    """Confirms that all sources have the same kerning groups per Designspace."""

    default_source = ds.findDefault()
    reference = default_source.font.groups
    for source in ds.sources:
        if source is default_source:
            continue
        if source.font.groups == reference:
            yield PASS, f"{source.filename} has same kerning groups as default source"
        else:
            yield (
                WARN,
                f"{source.filename} does not have the same kerning groups as default source",
            )


@check(id="com.google.fonts/check/googlesansflex/sources/kerning_present")
def check_kerning_present(ds: DesignSpaceDocument) -> CheckStatus:
    """Check how much kerning pairs a source has, not counting exceptions."""

    for source in ds.sources:
        if "Skateboard" in source.filename:
            yield SKIP, f"Skipping {source.filename} because it is experimental"
            continue
        if source.layerName is not None:
            yield SKIP, f"Skipping {source.filename} because it is a sparse layer"
            continue

        ufo_font: Font = source.font
        effective_kerning = {}
        for (first, second), value in ufo_font.kerning.items():
            # Skip exceptions for now, as we're more interested in the
            # non-exceptions that make them meaningful.
            if value == 0:
                continue
            # Kerning of non-existent things, skip.
            if (first not in ufo_font.groups and first not in ufo_font) or (
                second not in ufo_font.groups and second not in ufo_font
            ):
                continue
            effective_kerning[(first, second)] = value

        if effective_kerning:
            yield (
                INFO,
                f"{source.filename}: Found {len(effective_kerning)} kerning pairs (not counting exceptions)",
            )
        else:
            yield (
                WARN,
                f"{source.filename}: Found no kerning pairs (not counting exceptions)",
            )


@check(id="com.google.fonts/check/googlesansflex/sources/all_quadratics")
def check_all_quadratics(config, ufo: Ufo) -> CheckStatus:
    """Checks all curves in the font are quadratic"""

    font = ufo.ufo_font  # type: ignore
    assert isinstance(font, Font)

    offending_glyphs = [
        glyph.name
        for layer in font.layers
        for glyph in layer
        if any(
            point.type == "curve"
            for contour in glyph.contours
            for point in contour.points
        )
    ]

    if offending_glyphs:
        yield (
            FAIL,
            Message(
                "cubics-found",
                f"{ufo.file_displayname} contains glyphs with cubic curves:\n\n"
                f"{utils.bullet_list(config, offending_glyphs)}\n",
            ),
        )
    else:
        yield (
            PASS,
            "No cubic curves found",
        )


@check(id="com.google.fonts/check/googlesansflex/sources/no_open_corners")
def check_no_open_corners(config, ufo: Ufo) -> CheckStatus:
    """Check the sources have no corners, as Google Sans Flex's design with ROND
    is incompatible with this approach"""
    from glyphsLib.filters.eraseOpenCorners import EraseOpenCornersPen
    from fontTools.pens.basePen import NullPen

    font = ufo.ufo_font  # type: ignore
    assert isinstance(font, Font)

    default_layer_name = font.layers.defaultLayer.name
    for layer in font.layers:
        offending_glyphs = []
        for glyph in layer:
            the_void = NullPen()
            erase_open_corners = EraseOpenCornersPen(the_void)
            for contour in glyph.contours:
                contour.draw(erase_open_corners)
            if erase_open_corners.affected:
                offending_glyphs.append(glyph.name)

        if offending_glyphs:
            location_str = (
                ufo.file_displayname
                if layer.name == default_layer_name
                else f"{ufo.file_displayname} (layer {layer.name})"
            )
            yield (
                FAIL,
                Message(
                    "open-corners-found",
                    f"{location_str} contains glyphs with open corners:\n\n"
                    f"{utils.bullet_list(config, offending_glyphs)}\n",
                ),
            )
