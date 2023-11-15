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

import shutil
from argparse import ArgumentParser
from pathlib import Path

from fontTools.designspaceLib import DesignSpaceDocument
from ufoLib2 import Font

AXES_ORDER = {
    "Weight": "wg",
    "Width": "wd",
    "Optical Size": "oz",
    "Grade": "GD",
    "Roundness": "RD",
    "Slant": "sl",
}


def format_float(number: float) -> str:
    """Use an integer string representation if there is no fractional part,
    otherwise format as a normal float."""
    return str(int(number)) if number.is_integer() else str(number)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("designspace", type=Path)
    parser.add_argument("others", type=Path, nargs="*")
    args = parser.parse_args()

    doc_path: Path = args.designspace.resolve()

    doc = DesignSpaceDocument.fromfile(doc_path)

    # Confirm that there is only one layer in each UFO.
    ufos = doc.loadSourceFonts(lambda path: Font.open(path, lazy=False))
    for ufo in ufos:
        assert len(ufo.layers) == 1

    # Rename UFOs.
    path_mapping = {}
    for source in doc.sources:
        design_loc = source.getFullDesignLocation(doc)
        new_name = "GoogleSansFlex-" + "-".join(
            [
                f"{axis_abbrev}{format_float(design_loc.get(axis_name, 0.0))}"
                for axis_name, axis_abbrev in AXES_ORDER.items()
            ]
        )

        old_path = Path(source.path).resolve()

        if old_path not in path_mapping:
            new_path = doc_path.parent / f"{new_name}.ufo"
            path_mapping[old_path] = new_path
            shutil.rmtree(old_path)
            source.font.save(new_path, overwrite=True)
        else:
            new_path = path_mapping[old_path]

        source.path = str(new_path.resolve())

    doc.write(doc_path)

    # Correct other designspaces.
    for other_doc_path in args.others:
        other_doc = DesignSpaceDocument.fromfile(other_doc_path)
        for source in other_doc.sources:
            old_path = Path(source.path).resolve()
            new_path = path_mapping[old_path]
            source.path = str(new_path.resolve())
        other_doc.write(other_doc_path)
