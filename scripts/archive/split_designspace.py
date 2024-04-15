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

"""This script provides a function that uses DS5 to derive three variable fonts
from a main designspace, each containing:
1. All sources
2. Upright-only sources
3. Slanted-only sources

In addition, a CLI interface is provided to write a separate designspace file
for each of these VFs, to support tooling that must associate designspaces with
a single VF only."""

from argparse import ArgumentParser
from pathlib import Path

from fontTools.designspaceLib import (
    AxisDescriptor,
    DesignSpaceDocument,
    RangeAxisSubsetDescriptor,
    ValueAxisSubsetDescriptor,
    VariableFontDescriptor,
)
from fontTools.designspaceLib.split import splitVariableFonts

SLANT_AXIS = "Slant"


def get_split_vfs(doc: DesignSpaceDocument, name: str) -> list[VariableFontDescriptor]:
    axis_names = [axis.name for axis in doc.axes]

    slant_axis = doc.getAxis(SLANT_AXIS)
    assert isinstance(slant_axis, AxisDescriptor)

    return [
        VariableFontDescriptor(
            name="Full",
            filename=f"{name}",
            axisSubsets=[
                RangeAxisSubsetDescriptor(name=axis_name) for axis_name in axis_names
            ],
        ),
        VariableFontDescriptor(
            name="Upright",
            filename=f"{name}",
            axisSubsets=[
                RangeAxisSubsetDescriptor(name=axis_name)
                if axis_name != SLANT_AXIS
                else ValueAxisSubsetDescriptor(name=axis_name, userValue=0)
                for axis_name in axis_names
            ],
        ),
        VariableFontDescriptor(
            name="Italic",
            filename=f"{name}-Italic",
            axisSubsets=[
                RangeAxisSubsetDescriptor(name=axis_name)
                if axis_name != SLANT_AXIS
                else ValueAxisSubsetDescriptor(
                    name=axis_name, userValue=slant_axis.minimum
                )
                for axis_name in axis_names
            ],
        ),
    ]


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("designspace", type=Path)
    args = parser.parse_args()

    from_path: Path = args.designspace

    doc = DesignSpaceDocument.fromfile(from_path)
    doc.variableFonts = get_split_vfs(doc, from_path.stem)

    for vf, (name, sub_doc) in zip(doc.getVariableFonts(), splitVariableFonts(doc)):
        parent_folder = from_path.parent / name
        parent_folder.mkdir(exist_ok=True)

        assert vf.filename is not None
        to_path = parent_folder / f"{vf.filename}.designspace"
        sub_doc.write(to_path)
