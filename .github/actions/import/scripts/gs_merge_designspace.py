#!/usr/bin/env python3
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

"""Merge an incoming Designspace into an existing Designspace.

This script will import glyphs and groups specified in import text files
(one name per line) and kerning pairs that mention either of them. It will
also update each UFO's public.glyphOrder and public.postscriptNames lib keys
with entries for all imported glyphs, as well as public.skipExportGlyphs in
Designspace and UFOs.

It does not import any font info, global or local guidelines or features.
Designspace rules are also left untouched. Glyphs.app brace layers are not
supported.
"""

from __future__ import annotations

import argparse
import copy
import logging
import shutil
import sys
from pathlib import Path
from typing import Dict, List

from fontTools.designspaceLib import DesignSpaceDocument, SourceDescriptor
from .internal.reachable_glyphs import referenced_as_components
from ufoLib2 import Font
from ufoLib2.objects import LayerSet, Layer

MASTER_ID_KEY = "com.schriftgestaltung.fontMasterID"
SKIP_EXPORT_GLYPHS_KEY = "public.skipExportGlyphs"

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


def main(
    source_path: Path,
    target_path: Path,
    import_glyphs_file: Path,
    replace_target_designspace: bool = False,
    follow_glyphs: bool = False,
):
    # Read in stuff to import.
    import_glyphs_verbatim = [
        name.strip() for name in import_glyphs_file.read_text().split("\n") if name
    ]
    import_glyphs = set(import_glyphs_verbatim)

    replace_target_designspace: bool = replace_target_designspace
    follow_glyphs: bool = follow_glyphs

    # Load all sources.
    designspace_import = DesignSpaceDocument.fromfile(source_path)
    designspace_import.loadSourceFonts(Font.open)
    sources_to_delete = set()
    if replace_target_designspace:
        designspace_target = DesignSpaceDocument.fromfile(source_path)

        # Gather all layer names to import, so we leave out debris.
        import_layer_names: set[str] = set()
        for source in designspace_import.sources:
            import_layer_names.add(
                source.layerName or source.font.layers.defaultLayer.name
            )

        loaded_fonts: dict[str, Font] = {}
        for source, target in zip(
            designspace_import.sources, designspace_target.sources
        ):
            target.path = None
            assert source.font is not None
            assert target.filename is not None
            if target.filename in loaded_fonts:
                # We might hit the same filename multiple times when different
                # sources refer to different layers.
                target.font = loaded_fonts[target.filename]
            else:
                # When replacing a target UFO completely, make a hollow copy of
                # the source UFO, including all layers the Designspace refers
                # to. This also copies the name of the default layer.
                target.font = Font(
                    info=copy.deepcopy(source.font.info),
                    lib={"public.glyphOrder": import_glyphs_verbatim},
                    layers=LayerSet.from_iterable(
                        [
                            Layer(name=layer.name)
                            for layer in source.font.layers
                            if layer.name in import_layer_names
                        ],
                        defaultLayerName=source.font.layers.defaultLayer.name,
                    ),
                )

        # Delete sources that don't exist anymore later, if they exist at all.
        if target_path.exists():
            designspace_target_old = DesignSpaceDocument.fromfile(target_path)
            old_filenames = {
                Path(source.filename) for source in designspace_target_old.sources
            }
            new_filenames = {
                Path(source.filename) for source in designspace_target.sources
            }
            sources_to_delete = old_filenames - new_filenames
    else:
        designspace_target = DesignSpaceDocument.fromfile(target_path)
        designspace_target.loadSourceFonts(Font.open)

    if not import_glyphs:
        logging.error("You should provide at least one file with stuff to import.")
        sys.exit(1)

    # Update skip export glyphs list.
    skip_export_glyphs_import = set(
        designspace_import.lib.get(SKIP_EXPORT_GLYPHS_KEY, [])
    )
    skip_export_glyphs_target = set(
        designspace_target.lib.get(SKIP_EXPORT_GLYPHS_KEY, [])
    )
    skip_export_glyphs_target.update(
        n for n in skip_export_glyphs_import if n in import_glyphs
    )
    skip_export_glyphs = sorted(skip_export_glyphs_target)
    if skip_export_glyphs_target:
        designspace_target.lib[SKIP_EXPORT_GLYPHS_KEY] = skip_export_glyphs

    default_import_source = designspace_import.findDefault()
    assert default_import_source is not None
    assert default_import_source.font is not None
    actual_import_glyphs = default_import_source.font.keys()
    if not import_glyphs.issubset(actual_import_glyphs):
        missing_glyphs = import_glyphs.difference(actual_import_glyphs)
        logging.warning(
            "Sources to import are missing some glyphs, skipping: %s",
            ", ".join(sorted(missing_glyphs)),
        )
        import_glyphs.intersection_update(actual_import_glyphs)

    # Actually import now.
    for import_source in designspace_import.sources:
        assert import_source.font is not None
        import_font = import_source.font
        target_source = find_matching_source(
            import_source, designspace_import, designspace_target
        )
        if target_source is None:
            continue
        assert target_source.font is not None
        target_font: Font = target_source.font
        if import_source.layerName is not None:
            import_glyphset = import_font.layers[import_source.layerName]
            target_glyphset = target_font.layers[import_source.layerName]
        else:
            import_glyphset = import_font.layers.defaultLayer
            target_glyphset = target_font.layers.defaultLayer

        # Snatch up any bracket glyphs for glyphs without them being explicitly
        # listed in the import file. ".BRACKET." is a glyphsLib convention.
        # TODO: Do this up front on the default source?
        if import_source.layerName is not None:
            import_glyphs_layer = import_glyphs & import_glyphset.keys()
        else:
            import_glyphs_layer = copy.copy(import_glyphs)
        for name in import_glyphset.keys():
            if ".BRACKET." not in name:
                continue
            base = name.split(".BRACKET.")[0]
            if base in import_glyphs_layer:
                import_glyphs_layer.add(name)
                logging.warning(
                    "Added bracket glyph '%s', manually add to the Designspace rules.",
                    name,
                )

        if follow_glyphs:
            import_glyphs_layer.update(
                referenced_as_components(
                    import_font, import_glyphset, import_glyphs_layer
                )
            )

        for glyph_name in import_glyphs_layer:
            try:
                target_glyphset[glyph_name] = import_glyphset[glyph_name]
            except KeyError as e:
                if import_source.layerName is None:
                    # FIXME: revert this to being a fatal error when we know all
                    # glyphs are present
                    logging.warning(
                        "Glyph %s does not exist in the source UFO %s",
                        str(e),
                        str(import_source.filename),
                    )

        # Only font-level import below this point.
        if import_source.layerName is not None:
            continue

        # Gather all groups that mention any of the imported glyphs. They can
        # already exist in the target font (adding new glyphs to existing
        # groups) or not (new script-specific groups).
        import_font_groups = set()
        for group, glyphs in import_font.groups.items():
            if any(n in import_glyphs for n in glyphs):
                import_font_groups.add(group)

        # Clean glyphs to be imported from the target UFO kerning groups, so
        # importing the source kerning then does not lead to duplicate group
        # membership if their memebership changed.
        kerning_groups_to_be_cleaned = []
        for group_name in list(target_font.groups.keys()):
            members = target_font.groups[group_name]
            new_members = [member for member in members if member not in import_glyphs]
            if new_members:
                target_font.groups[group_name] = new_members
            else:
                del target_font.groups[group_name]
                kerning_groups_to_be_cleaned.append(group_name)
        target_font.kerning = {
            (f, s): v
            for (f, s), v in target_font.kerning.items()
            if f not in kerning_groups_to_be_cleaned
            and s not in kerning_groups_to_be_cleaned
        }

        # Importing a group that already exists should extend the existing group with
        # imported glyphs instead of overwriting the group.
        target_groups_extended = set()
        for group_name in import_font_groups:
            try:
                group_glyphs = import_font.groups[group_name]
            except KeyError as e:
                logging.warning(
                    "Kerning group %s does not exist in the source UFO %s, skipping.",
                    str(e),
                    str(import_source.filename),
                )
                continue
            if group_name in target_font.groups:
                target_groups_extended.add(group_name)
                existing = set(target_font.groups[group_name])
                for name in sorted(group_glyphs):
                    if name not in existing and name in import_glyphs:
                        target_font.groups[group_name].append(name)
            else:
                target_font.groups[group_name] = import_font.groups[group_name]

        # Import kerning where either side of a pair is an imported glyph or group.
        # NOTE: Existing groups extended with new glyphs are a special case, as they
        #       "contaminate" the below logic and would also let through a pair of
        #       extended group and completely script-unrelated group. I.e., if
        #       Armenian extended `public.kern2.dash` with new glyphs and
        #       accidentally changed the pair `public.kern1.L, public.kern2.dash`,
        #       The change would be picked up even though it had nothing to do with
        #       the script in question. This is the more relevant the more out-of-sync
        #       a source font is relative to the target font. One solution is to
        #       remove extended groups from the set of groups to check for inclusion.
        import_groups_to_check = import_font_groups - target_groups_extended
        for key, value in import_font.kerning.items():
            first, second = key
            if (first not in import_font and first not in import_font.groups) or (
                second not in import_font and second not in import_font.groups
            ):
                # Skip spurious pairs.
                continue
            if (
                first in import_groups_to_check
                or first in import_glyphs
                or second in import_groups_to_check
                or second in import_glyphs
            ):
                target_font.kerning[key] = value

        # Import public.glyphOrder while keeping order:
        target_glyph_order: List[str] = target_font.lib["public.glyphOrder"]
        target_glyph_order_set = set(target_glyph_order)
        for name in import_font.lib["public.glyphOrder"]:
            if name not in target_glyph_order_set and name in import_glyphs:
                target_glyph_order.append(name)

        # Import public.postscriptNames for imported glyphs:
        try:
            target_ps_names: Dict[str, str] = target_font.lib["public.postscriptNames"]
            for key, value in import_font.lib["public.postscriptNames"].items():
                if key in import_glyphs:
                    target_ps_names[key] = value
        except KeyError:
            logging.info(
                "public.postscriptNames does not exist in both the source & target UFO, skipping",
            )

        # Write global public.skipExportGlyphs list to all UFOs.
        target_font.lib[SKIP_EXPORT_GLYPHS_KEY] = skip_export_glyphs

    # Avoid typos:
    del target_font

    for target_source in designspace_target.sources:
        filename = target_path.parent / target_source.filename
        filename.parent.mkdir(exist_ok=True, parents=True)
        target_source.font.save(filename, overwrite=True)

    designspace_target.write(target_path)

    for source in sorted(sources_to_delete):
        path = target_path.parent / source
        print(f"Removing leftover {path}")
        shutil.rmtree(path)


def canonical_location(
    location: Dict[str, float], designspace: DesignSpaceDocument
) -> Dict[str, float]:
    """Returns a canonical location from a raw Designspace location.

    Vendor sources are inconsistent, so using user values and tags to match
    source axes is hopefully more reliable.
    """
    name_to_axis = {a.name: a for a in designspace.axes}
    name_to_tag = {a.name: a.tag for a in designspace.axes}
    return {
        name_to_tag[k]: name_to_axis[k].map_backward(v) for k, v in location.items()
    }


def find_matching_source(
    import_source: SourceDescriptor,
    designspace_import: DesignSpaceDocument,
    designspace_target: DesignSpaceDocument,
) -> SourceDescriptor | None:
    # Fill in the defaults if the import DS does not have e.g. a GRAD axis.
    # Match axes by tags because those are more consistent across vendor sources.
    import_source_location = canonical_location(
        import_source.location, designspace_import
    )
    full_import_source_location = {
        **canonical_location(designspace_target.default.location, designspace_target),
        **import_source_location,
    }

    # Match import to target UFO.
    try:
        target_source = next(
            s
            for s in designspace_target.sources
            if (
                canonical_location(s.location, designspace_target)
                == full_import_source_location
            )
        )
    except StopIteration:
        try:
            target_source = next(
                s
                for s in designspace_target.sources
                if s.font.lib[MASTER_ID_KEY] == import_source.font.lib[MASTER_ID_KEY]
            )
        except (StopIteration, KeyError):
            # FIXME: Have a proper way to add new sources
            logging.warning(
                "Cannot find target for source %s because there's no target location %s "
                "and no target with a matching master ID.",
                import_source.name,
                full_import_source_location,
            )
            return None

    return target_source


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        help="Path to source .designspace file.",
        required=True,
    )
    parser.add_argument(
        "--target",
        type=Path,
        help="Path to target .designspace file.",
        required=True,
    )
    parser.add_argument(
        "--import-glyphs-file",
        type=Path,
        help=(
            "Path to text file with glyph names to import (one per line). "
            "Also imports any kerning pair that mentions them."
        ),
        required=True,
    )
    parser.add_argument(
        "--replace-target-designspace",
        action="store_true",
        help=(
            "Import the source Designspace verbatim, for when it is in flux and "
            "matching sources makes little sense."
        ),
    )
    parser.add_argument(
        "--follow-glyphs",
        action="store_true",
        help=(
            "Also import glyphs that are referenced but not explicitly listed in "
            "the import list."
        ),
    )
    parsed_args = parser.parse_args()
    main(
        parsed_args.source,
        parsed_args.target,
        parsed_args.import_glyphs_file,
        parsed_args.replace_target_designspace,
        parsed_args.follow_glyphs,
    )
