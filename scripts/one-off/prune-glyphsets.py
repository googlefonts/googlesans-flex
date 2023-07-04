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

from __future__ import annotations

import argparse

from ufoLib2 import Font
from fontTools.designspaceLib import DesignSpaceDocument


def main(args: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("designspace_target", type=DesignSpaceDocument.fromfile)
    parser.add_argument("designspace_source", type=DesignSpaceDocument.fromfile)
    parsed_args = parser.parse_args()
    designspace_target: DesignSpaceDocument = parsed_args.designspace_target
    designspace_source: DesignSpaceDocument = parsed_args.designspace_source

    assert len(designspace_target.sources) == len(designspace_source.sources)
    assert all(
        t.asdict() == s.asdict()
        for t, s in zip(designspace_target.sources, designspace_source.sources)
    )

    ufos_target = designspace_target.loadSourceFonts(Font.open)
    designspace_source.loadSourceFonts(Font.open)

    for target, source in zip(designspace_target.sources, designspace_source.sources):
        if source.layerName is not None:
            import_glyphset = source.font.layers[source.layerName]
            target_glyphset = target.font.layers[source.layerName]
        else:
            import_glyphset = source.font.layers.defaultLayer
            target_glyphset = target.font.layers.defaultLayer

        for name in target_glyphset.keys() - import_glyphset.keys():
            del target_glyphset[name]

    for ufo in ufos_target:
        ufo.save()


if __name__ == "__main__":
    main()
