# pyright: basic
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

import copy
from pathlib import Path
from typing import Dict, List, Set, Tuple, Union

import ufo2ft
import ufoLib2
from fontTools.designspaceLib import (
    DesignSpaceDocument,
    InstanceDescriptor,
    RuleDescriptor,
    SourceDescriptor,
)
from fontTools.misc.transform import Transform
from glyphsLib.builder.bracket_layers import _expand_kerning_to_brackets

from . import gdef

MASTER_ID_KEY = "com.schriftgestaltung.fontMasterID"


def scrub_designspace(designspace: DesignSpaceDocument, project_root: Path) -> None:
    designspace.loadSourceFonts(ufoLib2.Font.open)
    skip_export_glyphs = set(designspace.lib.get("public.skipExportGlyphs", []))
    rules = designspace.rules
    ot_categories = infer_opentype_categories(designspace.default.font)

    for source in designspace.sources:
        scrub_source(source, skip_export_glyphs, rules, ot_categories)

    scrub_groups(designspace.default, designspace.sources)

    for instance in designspace.instances:
        scrub_instance(instance, project_root)

    if skip_export_glyphs:
        designspace.lib["public.skipExportGlyphs"] = sorted(skip_export_glyphs)
    designspace.lib = {
        k: v
        for k, v in designspace.lib.items()
        if k.startswith("public.")
        or k.startswith("com.github.googlei18n.ufo2ft.")
        or k == "GSDimensionPlugin.Dimensions"
    }


def scrub_instance(instance: InstanceDescriptor, project_root: Path) -> None:
    lib = instance.lib
    if not lib:
        return

    # Custom parameters influence the build.
    keys_to_keep = {"com.schriftgestaltung.customParameters"}

    # Exporting is the default, only remember if not exporting.
    if lib.get("com.schriftgestaltung.export") is False:
        keys_to_keep.add("com.schriftgestaltung.export")

    instance.lib = {
        k: v for k, v in lib.items() if k.startswith("public.") or k in keys_to_keep
    }

    # Trick DesignSpaceDocument.updatePaths() into doing the right thing.
    filename = Path(instance.filename)
    instance.filename = None
    # TODO: Adapt to Flex
    instance.path = str(
        project_root / "build" / "GoogleSans" / "instance_ufo" / filename.name
    )


def scrub_source(
    source: SourceDescriptor,
    skip_export_glyphs: Set[str],
    rules: List[RuleDescriptor],
    ot_categories: Dict[str, str],
) -> None:
    scrub_ufo(source.font, skip_export_glyphs, rules, ot_categories)


def scrub_ufo(
    ufo: ufoLib2.Font,
    skip_export_glyphs: Set[str],
    rules: List[RuleDescriptor],
    ot_categories: Dict[str, str],
) -> None:
    # Clean global lib.
    keys_to_keep = {
        # UFOs don't need lastChanged because glyphs are separate files, keep it disabled.
        "com.schriftgestaltung.customParameter.GSFont.disablesLastChange",
        # May be useful for Glyphs.
        "com.schriftgestaltung.customParameter.GSFont.Enforce Compatibility Check",
        # Cuts down on ufo2glyphs Git diffs slightly.
        MASTER_ID_KEY,
    }
    keys_to_remove = {
        # Using production names is fontmake's default.
        "com.github.googlei18n.ufo2ft.useProductionNames"
    }
    ufo.lib = {
        k: v
        for k, v in ufo.lib.items()
        if (
            k.startswith("public.")
            or k.startswith("com.github.googlei18n.ufo2ft.")
            or k in keys_to_keep
        )
        and k not in keys_to_remove
    }

    if "public.skipExportGlyphs" in ufo.lib:
        ufo.lib["public.skipExportGlyphs"] = sorted(skip_export_glyphs)
    if "public.postscriptNames" in ufo.lib:
        ufo.lib["public.postscriptNames"] = {
            k: v for k, v in ufo.lib["public.postscriptNames"].items() if k in ufo
        }

    # Reset the ufo2ft filters.
    if "com.github.googlei18n.ufo2ft.filters" in ufo.lib:
        # TODO: use propagateAnchors filter?
        ufo.lib["com.github.googlei18n.ufo2ft.filters"] = [
            {"name": "decomposeTransformedComponents", "pre": True},
            {"name": "flattenComponents", "pre": True},
        ]

    # Delete non-build-relevant layers.
    layers_to_delete = []
    for layer in ufo.layers:
        if layer is ufo.layers.defaultLayer:
            continue
        if layer.name.startswith(("[", "{")) and ".background" not in layer.name:
            continue
        layers_to_delete.append(layer.name)
    for layer_name in layers_to_delete:
        del ufo.layers[layer_name]

    for layer in ufo.layers:
        layer.lib = {
            k: v
            for k, v in layer.lib.items()
            if k.startswith("public.")
            or not k.startswith("com.schriftgestaltung.layerOrderInGlyph.")
        }

    # Clean glifs.
    for layer in ufo.layers:
        for glyph in layer:
            # Turn coordinates like "123.0" into "123".
            glyph.width = clean_number(glyph.width)
            for anchor in glyph.anchors:
                anchor.x = clean_number(anchor.x)
                anchor.y = clean_number(anchor.y)
            for guideline in glyph.guidelines:
                if guideline.x is not None:
                    guideline.x = clean_number(guideline.x)
                if guideline.y is not None:
                    guideline.y = clean_number(guideline.y)
                if guideline.angle is not None:
                    guideline.angle = clean_number(guideline.angle)
            for contour in glyph:
                for point in contour:
                    point.x = clean_number(point.x)
                    point.y = clean_number(point.y)
            for component in glyph.components:
                t = component.transformation
                component.transformation = Transform(
                    clean_number(t.xx),
                    clean_number(t.xy),
                    clean_number(t.yx),
                    clean_number(t.yy),
                    clean_number(t.dx),
                    clean_number(t.dy),
                )

            if not glyph.lib:
                continue

            glyph.lib = {
                k: v
                for k, v in glyph.lib.items()
                if (k.startswith("public.") and k != "public.markColor")
                or (
                    k.startswith("com.schriftgestaltung.Glyphs.")
                    and k != "com.schriftgestaltung.Glyphs.lastChange"
                )
            }

    # Clean out empty/non-existing groups and kerning pairs.
    new_groups = {}
    for key, value in ufo.groups.items():
        new_value = [v for v in value if v in ufo]
        if new_value:
            new_groups[key] = new_value
    ufo.groups.clear()
    ufo.groups.update(new_groups)

    new_kerning = {}
    for key, value in ufo.kerning.items():
        first, second = key
        if (first in ufo.groups or first in ufo) and (
            second in ufo.groups or second in ufo
        ):
            new_kerning[key] = value
    ufo.kerning.clear()
    ufo.kerning.update(new_kerning)

    # Bracket glyphs are a Glyphs.app construct that inherit the kerning from
    # their parents.
    for rule in rules:
        for name, name_bracket in rule.subs:
            _expand_kerning_to_brackets(name, name_bracket, ufo)

    # Use OpenType GDEF categories inferred from default source.
    ufo.lib["public.openTypeCategories"] = ot_categories


def clean_number(v: Union[int, float]) -> float:
    if isinstance(v, int):
        return v
    if v.is_integer():
        return int(v)
    return v


def location_to_key(
    location: Dict[str, float], skip_axis: str = "Grade"
) -> Tuple[Tuple[str, float], ...]:
    return tuple((k, v) for k, v in location.items() if k != skip_axis)


def scrub_groups(
    default_source: SourceDescriptor, all_sources: List[SourceDescriptor]
) -> None:
    """Remove unused kerning groups."""

    used = set()
    for source in all_sources:
        for (first, second) in source.font.kerning:
            if first.startswith("public.kern1."):
                used.add(first)
            if second.startswith("public.kern2."):
                used.add(second)
    scrubbed_groups = {k: v for k, v in default_source.font.groups.items() if k in used}
    for source in all_sources:
        source.font.groups.clear()
        source.font.groups.update(scrubbed_groups)


def infer_opentype_categories(source: ufoLib2.Font) -> Dict[str, str]:
    # Update GDEF table. Anchors have to be propagated before we can construct
    # the GDEF table. Use the UFO copy so we can safely save the original with
    # just updated features.
    ufo_copy = copy.deepcopy(source)
    pre_filter, _ = ufo2ft.filters.loadFilters(ufo_copy)
    for pf in pre_filter:
        pf(font=ufo_copy)

    return gdef.update_opentype_categories(ufo_copy)
