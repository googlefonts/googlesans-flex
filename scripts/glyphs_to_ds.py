# Copyright 2023 Google Sans Flex Authors
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

"""Convert sources from a Glyphs 3 .glyphs or .glyphspackage file into a
designspace + UFO that can be used for building this font project."""

import glyphsLib
from glyphsLib import GSFont
from pathlib import Path
from ufoLib2 import Font
from fontTools.designspaceLib import DesignSpaceDocument
from tempfile import TemporaryDirectory
from argparse import ArgumentParser

# Incompatible glyphs, that should not be included in the final build.
INCOMPATIBLE = set(
    [
        "acircumflex.alt",
        "acircumflex",
        "Acircumflex",
        "circumflex",
        "circumflexcomb",
        "ecircumflex",
        "Ecircumflex",
        "four.denominator",
        "four.numerator",
        "four.sinf",
        "four.tf",
        "foursubscript",
        "foursuperior",
        "foursuperscript",
        "hungarumlaut",
        "hungarumlautcomb",
        "icircumflex",
        "Icircumflex",
        "ocircumflex",
        "Ocircumflex",
        "ohungarumlaut",
        "Ohungarumlaut",
        "onequarter",
        "t",
        "threequarters",
        "ucircumflex",
        "Ucircumflex",
        "uhungarumlaut",
        "Uhungarumlaut",
        "wcircumflex",
        "Wcircumflex",
        "ycircumflex",
        "Ycircumflex",
    ]
)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("glyphs", type=Path)
    parser.add_argument("designspace", type=Path)
    args = parser.parse_args()

    glyphs_source: Path = args.glyphs
    designspace_target: Path = args.designspace

    ##################
    ### Preprocess ###
    ##################

    font = GSFont(glyphs_source)

    # Partially clear background layers.
    # Motivation: references to missing components crash glyphsLib.
    for glyph in font.glyphs:
        for layer in glyph.layers:
            layer.background.components = []

    # Add axis mappings based on min and max of each axis.
    # Motivation: required for glyphsLib to set axes bounds correctly.
    #             https://github.com/googlefonts/glyphsLib/issues/942
    font.customParameters["Axis Mappings"] = {
        "opsz": {"6": 6, "144": 144},
        "wdth": {"25": 25, "151": 151},
        "wght": {"1": 1, "1000": 1000},
        "slnt": {"0": 0, "-10": -10},
        "ROND": {"0": 0, "100": 100},
        "GRAD": {"0": 0, "50": 50},
    }

    # Give every brace layer a name.
    # Motivation: required for glyphsLib to export unnamed brace layers.
    #             https://github.com/googlefonts/glyphsLib/issues/952
    for glyph in font.glyphs:
        for layer in glyph.layers:
            if layer._is_brace_layer():
                layer.name = layer._brace_layer_name()

    # Clear feature imports.
    # Motivation: glyphsLib tries to export disabled features
    font.featurePrefixes = []

    ###############
    ### Convert ###
    ###############

    with TemporaryDirectory() as temp_sources:
        # Save modified Glyphs sources to disk to reference in build_masters().
        temp_source = Path(temp_sources, "Temporary.glyphs")
        font.save(temp_source)

        # Convert glyphs sources to DS+UFO.
        glyphsLib.build_masters(
            temp_source,
            designspace_target.parent,
            designspace_instance_dir=None,
            designspace_path=designspace_target,
            # minimize_glyphs_diffs=options.no_preserve_glyphsapp_metadata,
            propagate_anchors=False,
            # normalize_ufos=options.normalize_ufos,
            # create_background_layers=options.create_background_layers,
            # generate_GDEF=options.generate_GDEF,
            # store_editor_state=not options.no_store_editor_state,
            # write_skipexportglyphs=options.write_public_skip_export_glyphs,
            # expand_includes=options.expand_includes,
            # ufo_module=__import__(options.ufo_module),
            minimal=True,  # Motivation: avoids crash in background layer.
            # glyph_data=options.glyph_data or None,
        )

    ########################
    ### Tidy designspace ###
    ########################

    doc = DesignSpaceDocument.fromfile(designspace_target)

    # Extend skipped glyphs to include incompatible glyphs, both in the DS...
    already_skipped = set(doc.lib.get("public.skipExportGlyphs", []))
    doc.lib["public.skipExportGlyphs"] = sorted(already_skipped | INCOMPATIBLE)

    # ...and in every UFO.
    ufos = doc.loadSourceFonts(Font.open)
    for ufo in ufos:
        already_skipped = set(ufo.lib.get("public.skipExportGlyphs", []))
        ufo.lib["public.skipExportGlyphs"] = sorted(already_skipped | INCOMPATIBLE)

    # Remove all kerning, to avoid incompatible features across sources.
    for ufo in ufos:
        ufo.kerning.clear()
    
    # Rename the default UFO's style name to "Regular"; this is necessary to
    # produce a correct name table, but otherwise inconvenient to have in
    # upstream (unimported) sources.
    default_source = doc.findDefault()
    assert default_source is not None

    default_ufo = default_source.font
    assert isinstance(default_ufo, Font)
    default_ufo.info.styleName = "Regular"
    default_ufo.info.styleMapFamilyName = "Google Sans Flex"
    # TODO: Apply this to the italic when it is added.

    # Save everything that we have tidied.
    doc.write(designspace_target)
    for ufo in ufos:
        ufo.save()
