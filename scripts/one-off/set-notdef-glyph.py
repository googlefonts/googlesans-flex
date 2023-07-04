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
    parser.add_argument("designspace", type=DesignSpaceDocument.fromfile)
    parsed_args = parser.parse_args()
    designspace: DesignSpaceDocument = parsed_args.designspace

    ufos = designspace.loadSourceFonts(Font.open)

    default_source = designspace.findDefault().font
    assert default_source is not None
    default_notdef = default_source[".notdef"]

    for source in designspace.sources:
        if source.layerName is None:
            source.font[".notdef"] = default_notdef
        else:
            source.font.layers[source.layerName][".notdef"] = default_notdef

    for ufo in ufos:
        ufo.save()


if __name__ == "__main__":
    main()
