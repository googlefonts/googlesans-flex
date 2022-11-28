# Copyright 2021 Google Sans Authors
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

from typing import Set

import ufo2ft.featureCompiler
import ufo2ft.util
from ufoLib2.objects import Font, Glyph


def reachable_glyphs(ufo: Font) -> Set[str]:
    """Return set of glyph names of glyphs reachable via Unicode value and
    feature substitutions."""

    features = ufo2ft.featureCompiler.parseLayoutFeatures(ufo)
    glyph_order = list(ufo.keys())
    gsub = ufo2ft.util.compileGSUB(features, glyph_order)
    reachable_glyphs = {g.name for g in ufo if g.unicode is not None}
    reachable_glyphs.add(".notdef")
    ufo2ft.util.closeGlyphsOverGSUB(gsub, reachable_glyphs)

    return reachable_glyphs


def referenced_as_components(ufo: Font, reachable_glyphs: Set[str]) -> Set[str]:
    """Return set of glyph names of glyphs used as components by glyphs in
    reachable_glyphs."""

    def _recurse(glyph: Glyph, seen: Set[str]) -> None:
        for component in glyph.components:
            seen.add(component.baseGlyph)
            _recurse(ufo[component.baseGlyph], seen)

    referenced_components = set()
    for name in reachable_glyphs:
        glyph = ufo[name]
        _recurse(glyph, referenced_components)

    return referenced_components
