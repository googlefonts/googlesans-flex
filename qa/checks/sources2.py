#!/usr/bin/env -S uv run --script
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
    FAIL,
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
from glyphsLib import GSFont, GSGlyph, GSLayer


def get_sources(font_file: Path, context: CheckContext) -> GSFont:
    if (sources := context.cache.get("sources")) is not None:
        return sources
    sources = context.cache["sources"] = glyphsLib.load(font_file)
    return sources


@check(
    id="googlesansflex/sources/same_tabular_width",
    title="Check that tabular glyphs have the same width within the same master",
    rationale="Tabularity requires the same width.",
    applies_to="GLYPHSPACKAGE",
)
def check_same_tabular_width(font_file: Path, context: CheckContext) -> CheckStatuses:
    font = get_sources(font_file, context)

    # Glyphs that intentionally have a half tabular width:
    HALF_WIDTH = {
        # https://github.com/googlefonts/googlesans-flex/issues/937
        "space.tf",
        # https://github.com/googlefonts/googlesans-flex/issues/1077#issuecomment-2457455141
        "colon.tf",
        "comma.tf",
        "period.tf",
        "semicolon.tf",
    }

    masters = {m.name for m in font.masters}
    tabulars = {g for g in font.glyphs if ".tf" in g.name}

    full = {g for g in tabulars if g.name not in HALF_WIDTH}
    full_layers: dict[str, list[GSLayer]] = defaultdict(list)
    for glyph in full:
        for layer in glyph.layers:
            if layer.name not in masters:
                continue
            full_layers[layer.name].append(layer)

    half = {g for g in tabulars if g.name in HALF_WIDTH}
    half_layers: dict[str, list[GSLayer]] = defaultdict(list)
    for glyph in half:
        for layer in glyph.layers:
            if layer.name not in masters:
                continue
            half_layers[layer.name].append(layer)

    warnings_by_layer: dict[str, list[tuple[str, float, str, float]]] = {}
    for group in (full_layers.items(), half_layers.items()):
        for layer_name, layers in group:
            reference, *rest = sorted(layers)
            width = reference.width
            if width is None:
                yield (
                    FAIL,
                    f"layer {layer_name}: {reference} has no width, stopping check",
                )
                return

            for layer in rest:
                if layer.width != width:
                    assert isinstance(reference.parent, GSGlyph)
                    warnings_by_layer.setdefault(layer_name, []).append(
                        (reference.parent.name, layer.width, reference.name, width)
                    )

    if not warnings_by_layer:
        yield PASS, "Tabular glyphs, if they exist, have the same width"
    else:
        for layer_name, warnings in warnings_by_layer.items():
            listing = "\n".join(
                f"* {name} ({width}) has different width than in layer '{ref_name}' ({ref_width})"
                for (name, width, ref_name, ref_width) in warnings
            )
            yield (
                FAIL,
                Message(
                    "mismatching-tabular-widths", f"layer '{layer_name}':\n\n{listing}"
                ),
            )


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
    plugin.register_check(check_same_tabular_width)
    plugin.register_check(check_suspicious_kerning_values)
    plugin.register_filetype("GLYPHSPACKAGE", "*.glyphspackage")

    plugin.register_profile(
        "google-sans-flex-source-checks",
        ProfileDefinition(
            sections={
                "Python Example Checks": [
                    "googlesansflex/sources/same_tabular_width",
                    "googlesansflex/sources/suspicious_kerning_values",
                    # "googlesansflex/sources/kerning_present",
                    # "googlesansflex/sources/decomposed_by_skip",
                    # "googlesansflex/sources/decomposed_by_mix",
                    # "googlesansflex/sources/decomposed_by_var_transform",
                    # "ufo_consistent_curve_type",
                    # "designspace_has_consistent_groups",
                    # "ufo_no_open_corners",
                ]
            }
        ),
    )

    # TODO: fontbakery checks


if __name__ == "__main__":
    raise SystemExit(plugin_main(register, plugin_name="source-checks-plugin"))
