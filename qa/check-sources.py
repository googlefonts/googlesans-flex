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

from fontbakery.callable import check, condition
from fontbakery.checkrunner import FAIL, PASS, WARN, Section, Status, Message
from fontbakery.fonts_profile import profile_factory

from ufoLib2 import Font


CheckStatus = Iterable[Tuple[Status, Union[Message, str]]]

profile_imports = ()
profile = profile_factory(default_section=Section("Google Sans Flex Source Checks"))


@condition
def ufo_font(ufo: str) -> Font:
    return Font.open(ufo)


@check(id="com.google.fonts/check/googlesansflex/sources/same_tabular_width")
def check_same_tabular_widths(ufo: str, ufo_font: Font) -> CheckStatus:
    """Confirms that tabular glyphs have the same width within the same master."""

    widths_ok = True

    for layer in ufo_font.layers:
        tabulars = {name for name in layer.keys() if ".tf" in name}
        if not tabulars:
            continue

        if "zero.tf" in tabulars:
            width_glyph = "zero.tf"
        else:
            width_glyph = iter(next(tabulars))
        width = layer[width_glyph].width
        if width is None:
            yield FAIL, f"{ufo}, layer {layer.name}: {width_glyph} has no width, stopping check"
            return

        for name in tabulars:
            glyph = layer[name]
            if glyph.width != width:
                widths_ok = False
                yield FAIL, f"{ufo}, layer {layer.name}: {name} ({glyph.width}) has different width than {width_glyph} ({width})"

    if widths_ok:
        yield PASS, "Tabular glyphs, if they exist, have the same width"


@check(id="com.google.fonts/check/googlesansflex/sources/suspicious_kerning_values")
def check_suspicious_kerning_values(ufo_font: Font) -> CheckStatus:
    """Check for small and large kerning values outside a range and other
    things."""

    kerning_ok = True

    # Accept kerning values in the range [20, 200] for 1000 upM fonts.
    threshold_low = round(20 * ufo_font.info.unitsPerEm / 1000)
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

    for (first, second), value in ufo_font.kerning.items():
        if value == 0:
            if first in ufo_font.groups and second in ufo_font.groups:
                yield WARN, f"Group-to-group pairs like {(first, second)} (e.g. {describe_pair(first, second)}) don't need zero values"
        elif abs(value) not in threshold:
            kerning_ok = False
            yield WARN, f"Pair {(first, second)} (e.g. {describe_pair(first, second)}) has suspicious kerning value {value}"

    if kerning_ok:
        yield PASS, "No suspicion raised"


profile.auto_register(globals())
