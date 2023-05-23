#!/usr/bin/env python3
# Copyright 2020 Google Sans Authors
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

This script will import glyphs amd groups specified in import text files
(one name per line) and kerning pairs that mention either of them. It will
also update each UFO's public.glyphOrder and public.postscriptNames lib keys
with entries for all imported glyphs, as well as public.skipExportGlyphs in
Designspace and UFOs.

It does not import any font info, global or local guidelines or features.
Designspace rules are also left untouched. Glyphs.app brace layers are not
supported.
"""

import argparse
import collections
import copy
import logging
import sys
from pathlib import Path
from typing import Dict, List

import ufoLib2
from fontTools.designspaceLib import DesignSpaceDocument
from ufo2ft.util import makeOfficialGlyphOrder

from internal.normalize import location_to_key

MASTER_ID_KEY = "com.schriftgestaltung.fontMasterID"
SKIP_EXPORT_GLYPHS_KEY = "public.skipExportGlyphs"

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


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
)
parser.add_argument(
    "--import-groups-file",
    type=Path,
    help=(
        "Path to text file with group names to import (one per line). "
        "Also imports any kerning pair that mentions them."
    ),
)
parsed_args = parser.parse_args()


# Read in stuff to import.
if parsed_args.import_glyphs_file is not None:
    import_glyphs = {
        name.strip()
        for name in parsed_args.import_glyphs_file.read_text().split("\n")
        if name
    }
else:
    import_glyphs = set()

if parsed_args.import_groups_file is not None:
    import_groups = {
        name.strip()
        for name in parsed_args.import_groups_file.read_text().split("\n")
        if name
    }
else:
    import_groups = set()

if not import_glyphs and not import_groups:
    logging.error("You should provide at least one file with stuff to import.")
    sys.exit(1)


# Load all sources.
designspace_import = DesignSpaceDocument.fromfile(parsed_args.source)
designspace_import.loadSourceFonts(ufoLib2.Font.open)
designspace_target = DesignSpaceDocument.fromfile(parsed_args.target)
designspace_target.loadSourceFonts(ufoLib2.Font.open)


# Update skip export glyphs list.
skip_export_glyphs_import = set(designspace_import.lib.get(SKIP_EXPORT_GLYPHS_KEY, []))
skip_export_glyphs_target = set(designspace_target.lib.get(SKIP_EXPORT_GLYPHS_KEY, []))
skip_export_glyphs_target.update(
    n for n in skip_export_glyphs_import if n in import_glyphs
)
skip_export_glyphs = sorted(skip_export_glyphs_target)
if skip_export_glyphs_target:
    designspace_target.lib[SKIP_EXPORT_GLYPHS_KEY] = skip_export_glyphs

# Whether any of the sources to be imported is ungraded.
import_is_ungraded = False


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


# Actually import now.
for import_source in designspace_import.sources:
    if import_source.layerName is not None:
        logging.error(
            "Brace layers not supported currently: %s", import_source.asdict()
        )
        continue

    if "Grade" not in import_source.location:
        import_is_ungraded = True

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
            logging.error(
                "Cannot find target for source %s because there's no target location %s "
                "and no target with a matching master ID.",
                import_source.name,
                full_import_source_location,
            )
            sys.exit(1)

    import_font: ufoLib2.Font = import_source.font
    target_font: ufoLib2.Font = target_source.font

    # Snatch up any bracket glyphs for glyphs without them being explicitly
    # listed in the import file. ".BRACKET." is a glyphsLib convention.
    for name in import_font.keys():
        if ".BRACKET." not in name:
            continue
        base = name.split(".BRACKET.")[0]
        if base in import_glyphs:
            import_glyphs.add(name)
            logging.warning(
                "Added bracket glyph '%s', manually add to the Designspace rules.", name
            )

    for glyph_name in import_glyphs:
        try:
            target_font[glyph_name] = import_font[glyph_name]
        except KeyError as e:
            logging.error(
                "Glyph %s does not exist in the source UFO %s, aborting.",
                str(e),
                str(import_source.filename),
            )
            sys.exit(1)

    # If no group import list has been specified, gather all groups that mention
    # any of the imported glyphs. They can already exist in the target font
    # (adding new glyphs to existing groups) or not (new script-specific
    # groups).
    import_font_groups = set()
    if not import_groups:
        for group, glyphs in import_font.groups.items():
            if any(n in import_glyphs for n in glyphs):
                import_font_groups.add(group)

    # Use global groups list or, if non passed in, font specific one for checks below.
    import_groups_to_check = import_groups or import_font_groups

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
    for group_name in import_groups_to_check:
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
    import_groups_to_check = import_groups_to_check - target_groups_extended
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
    for name in makeOfficialGlyphOrder(import_font):
        if name not in target_glyph_order_set and name in import_glyphs:
            target_glyph_order.append(name)

    # Import public.postscriptNames for imported glyphs:
    target_ps_names: Dict[str, str] = target_font.lib["public.postscriptNames"]
    for key, value in import_font.lib["public.postscriptNames"].items():
        if key in import_glyphs:
            target_ps_names[key] = value

    # Write global public.skipExportGlyphs list to all UFOs.
    target_font.lib[SKIP_EXPORT_GLYPHS_KEY] = skip_export_glyphs

    target_font.save()


# If we import sources that don't have a GRAD axis yet, copy all imported glyphs
# and other data from above over to our existing GRAD sources.
if import_is_ungraded:
    default_grades = []
    grade_mapping = collections.defaultdict(list)
    for source in designspace_target.sources:
        if source.location["Grade"]:
            grade_mapping[location_to_key(source.location)].append(source)
        else:
            default_grades.append(source)

    for source in default_grades:
        for graded_source in grade_mapping[location_to_key(source.location)]:
            graded_default_layer = graded_source.font.layers.defaultLayer
            for glyph_name in import_glyphs:
                graded_default_layer.insertGlyph(
                    source.font[glyph_name], overwrite=True
                )

            graded_source.font.groups = source.font.groups
            graded_source.font.kerning = source.font.kerning

            graded_master_id = graded_source.font.lib.get(MASTER_ID_KEY)
            graded_source.font.lib = copy.copy(source.font.lib)
            graded_source.font.lib[MASTER_ID_KEY] = graded_master_id

            graded_source.font.save()


designspace_target.write(parsed_args.target)
