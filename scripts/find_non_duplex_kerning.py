# Copyright 2026 Google Sans Project Authors

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Small script to identify kerning variation for a specific pair in duplex
scripts within a designspace -- put together quickly for debugging, but not
heavily tested."""

from fontTools.designspaceLib import DesignSpaceDocument
from fontTools.ufoLib.kerning import lookupKerningValue
from ufoLib2 import Font

DESIGNSPACE = "sources/GoogleSansFlex.designspace"
PAIR = ("uni02BB", "icircumflex")

if __name__ == "__main__":
    doc = DesignSpaceDocument.fromfile(DESIGNSPACE)
    doc.loadSourceFonts(Font.open)

    # Get the kerning values for each contributing source.
    results = {}
    for source in doc.sources:
        if source.layerName is not None:
            continue

        ufo = source.font
        assert isinstance(ufo, Font)

        value = lookupKerningValue(PAIR, ufo.kerning, ufo.groups)

        # Group by axes that can vary kerning, then show variation by value.
        loc = source.getFullDesignLocation(doc)
        shared = (
            loc.pop("Weight"),
            loc.pop("Width"),
            loc.pop("Optical Size"),
            loc.pop("Slant"),
        )
        results.setdefault(shared, {}).setdefault(value, []).append(source.styleName)

    # Print a tree of results.
    for shared, values in sorted(results.items()):
        if len(values) <= 1:
            # No variation.
            continue

        print(shared)
        for value, styles in sorted(values.items()):
            print(f"\t{value}")
            for style in sorted(styles):
                print(f"\t\t{style}")
        print()
