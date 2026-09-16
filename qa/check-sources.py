#!/usr/bin/env -S uv run --script
#
# Copyright 2026 Google Sans Authors
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
#
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "fontspectorapi",
#     "glyphsLib",
# ]
# ///


from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import glyphsLib
from fontspectorapi import (
    ERROR,
    PASS,
    WARN,
    CheckContext,
    CheckStatuses,
    Message,
    Plugin,
    ProfileDefinition,
    check,
    plugin_main,
)
from glyphsLib import GSFont, GSGlyph


# XXX: Caching does not work in plugins as of the time of this writing, as each
# test is run in a new subprocess.
def get_sources(font_file: Path, context: CheckContext) -> GSFont:
    if (sources := context.cache.get("sources")) is not None:
        return sources
    sources = context.cache["sources"] = glyphsLib.load(font_file)
    return sources


@check(
    id="googlesansflex/sources/suspicious_kerning_values",
    title="Check for small and large kerning values outside a range and other things",
    rationale="Suspicously large kerning might be a mistake.",
    applies_to="GLYPHSPACKAGE",
)
def check_suspicious_kerning_values(
    font_file: Path, context: CheckContext
) -> CheckStatuses:
    font = get_sources(font_file, context)

    if font.kerningRTL:
        yield (
            ERROR,
            Message("rtl-unsupported", "RTL kerning is not supported, stopping."),
        )
        return

    if (space_glyph := font.glyphs["space"]) is None:
        yield (
            ERROR,
            Message(
                "space-glyph-missing",
                "Need to have a /space glyph to adjust thresholds with, stopping.",
            ),
        )
        return

    if (default_master_id := font.customParameters["Variable Font Origin"]) is None:
        yield (
            ERROR,
            Message(
                "variable-font-origin-missing",
                "Need to have the 'Variable Font Origin' custom parameter to know which master is the default one, stopping.",
            ),
        )
        return

    masters = {m.id: m.name for m in font.masters}
    default_space_width = space_glyph.layers[default_master_id].width

    # Accept kerning values in the range [10, 200] for 1000 upM fonts.
    threshold_low = round(10 * font.upm / 1000)
    threshold_high = round(200 * font.upm / 1000)

    groups: dict[str, list[str]] = defaultdict(list)
    glyph: GSGlyph
    for glyph in sorted(font.glyphs, key=lambda g: g.name):
        assert glyph.name
        if glyph.leftKerningGroup:
            groups[f"@MMK_R_{glyph.leftKerningGroup}"].append(glyph.name)
        if glyph.rightKerningGroup:
            groups[f"@MMK_L_{glyph.rightKerningGroup}"].append(glyph.name)

    def describe_pair(first: str, second: str) -> str:
        glyphs = []
        if first in groups:
            glyphs.append(groups[first][0])
        else:
            glyphs.append(first)
        if second in groups:
            glyphs.append(groups[second][0])
        else:
            glyphs.append(second)
        return "".join(f"/{name}" for name in glyphs)

    for master_id, kerning in font.kerning.items():
        master_name = masters[master_id]

        # Scale the threshold of each master according to its space glyph, as
        # different widths should have different thresholds. See
        # https://github.com/googlefonts/googlesans-flex/issues/828.
        specific_space_layer = space_glyph.layers[master_id]
        if specific_space_layer is None:
            yield (
                WARN,
                Message(
                    "specific-space-layer-missing",
                    f"The space glyph has no master for '{master_name}', cannot calibrate thresholds for checking, skipping.",
                ),
            )
            continue
        adjustment = specific_space_layer.width / default_space_width
        threshold = range(
            round(threshold_low * adjustment), round(threshold_high * adjustment) + 1
        )

        suspicious_kerning = []
        for first, seconds in kerning.items():
            for second, value in seconds.items():
                if value == 0:
                    continue
                if abs(value) not in threshold:
                    suspicious_kerning.append(
                        ((first, second), describe_pair(first, second), value)
                    )

        if not suspicious_kerning:
            yield PASS, f"No suspicion raised for master '{master_name}'"
        else:
            listing = "\n".join(
                f"* Pair {pair} (e.g. {example}): {value}"
                for (pair, example, value) in suspicious_kerning
            )
            threshold_low_adj = round(threshold_low * adjustment)
            threshold_high_adj = round(threshold_high * adjustment)
            yield (
                WARN,
                Message(
                    "suspicious-kerning-values",
                    f"In master '{master_name}', kerning values outside the accepted range of [{threshold_low_adj}, {threshold_high_adj}]:\n\n{listing}",
                ),
            )


def register(plugin: Plugin) -> None:
    plugin.register_check(check_suspicious_kerning_values)
    plugin.register_filetype("GLYPHSPACKAGE", "*.glyphspackage")

    plugin.register_profile(
        "google-sans-flex-source-checks",
        ProfileDefinition(
            sections={
                "Source Checks": [
                    "googlesansflex/sources/suspicious_kerning_values",
                ]
            }
        ),
    )


if __name__ == "__main__":
    raise SystemExit(plugin_main(register, plugin_name="source-checks-plugin"))
