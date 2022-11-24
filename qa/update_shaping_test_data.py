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

"""Update a regression test file with the shaping output of a list of fonts."""

from __future__ import annotations

import enum
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

import toml
import uharfbuzz as hb  # type: ignore
from fontTools.ttLib import TTFont  # type: ignore


class ComparisonMode(enum.Enum):
    FULL = "full"  # Record glyph names, offsets and advance widths.
    GLYPHSTREAM = "glyphstream"  # Just glyph names.


class Direction(enum.Enum):
    LTR = "ltr"
    RTL = "rtl"
    TTB = "ttb"
    BTT = "btt"


def shape_run(
    hb_face: hb.Face,
    text: str,
    script: Optional[str],
    language: Optional[str],
    direction: Direction,
    features: Dict[str, bool],
    shaping_comparison_mode: ComparisonMode,
    variations: Optional[Dict[str, float]] = None,
) -> str:
    font = hb.Font(hb_face)
    if variations is not None:
        font.set_variations(variations)

    buf = hb.Buffer()
    buf.add_str(text)
    if script is not None:
        buf.script = script
    buf.direction = direction.value
    if language is not None:
        buf.language = language
    buf.guess_segment_properties()
    hb.shape(font, buf, features)

    infos = buf.glyph_infos
    positions = buf.glyph_positions

    if shaping_comparison_mode is ComparisonMode.FULL:
        out = []
        for info, pos in zip(infos, positions):
            s = f"{font.get_glyph_name(info.codepoint)}={info.cluster}"
            if pos.x_offset or pos.y_offset:
                s += f"@{pos.x_offset},{pos.y_offset}"
            if pos.x_advance or pos.y_advance:
                s += f"+{pos.x_advance},{pos.y_advance}"
            out.append(s)
        return "|".join(out)
    elif shaping_comparison_mode is ComparisonMode.GLYPHSTREAM:
        return "|".join(font.get_glyph_name(info.codepoint) for info in infos)
    else:
        raise ValueError(f"Unknown comparison mode {shaping_comparison_mode}.")


def shape_texts(
    font: TTFont,
    hb_face: hb.Face,
    texts: List[str],
    script: Optional[str],
    language: Optional[str],
    direction: Direction,
    features: Dict[str, bool],
    shaping_comparison_mode: ComparisonMode,
) -> Union[Dict[str, List[str]], List[str]]:
    if "fvar" in font:
        result = {}
        for instance in font["fvar"].instances:
            coordinate_str = ",".join(f"{k}={v}" for k, v in instance.coordinates.items())
            result[coordinate_str] = [
                shape_run(
                    hb_face,
                    text,
                    script,
                    language,
                    direction,
                    features,
                    shaping_comparison_mode,
                    instance.coordinates,
                )
                for text in texts
            ]
        return result
    else:
        return [
            shape_run(
                hb_face,
                text,
                script,
                language,
                direction,
                features,
                shaping_comparison_mode,
            )
            for text in texts
        ]


def toml2json(tomlpath: Path) -> None:
    with tomlpath.open() as tf:
        json_filepath = get_json_filepath(tomlpath)
        json_filepath.write_text(json.dumps(toml.load(tf), indent=2, ensure_ascii=False))


def get_json_filepath(tomlpath: Path) -> Path:
    return Path("shaping", tomlpath.with_suffix(".json").name)


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "shaping_file", type=Path, help="The .toml shaping definition file path."
    )
    parser.add_argument(
        "fonts",
        nargs="+",
        type=TTFont,
        help="The fonts to update the testing file with.",
    )
    parsed_args = parser.parse_args()

    shaping_file_toml: Path = parsed_args.shaping_file
    # convert toml definition file to
    # JSON format used for CI tests
    if shaping_file_toml.exists():
        toml2json(shaping_file_toml)
    else:
        sys.stderr.write(f"{shaping_file_toml} does not appear to be a valid file!\n")
        sys.exit(1)

    # open json file that was dumped above
    # and set the shaping data based on builds
    # defined on the command line
    shaping_file_json = get_json_filepath(shaping_file_toml)
    shaping_input_doc = json.loads(shaping_file_json.read_text())
    shaping_input = shaping_input_doc["input"]
    shaping_texts = shaping_input["text"]
    shaping_features = shaping_input.get("features", {})
    shaping_script = shaping_input.get("script")
    shaping_language = shaping_input.get("language")
    shaping_comparison_mode = ComparisonMode(shaping_input.get("comparison_mode", "full"))
    shaping_direction = Direction(shaping_input.get("direction", "ltr"))

    if "output" not in shaping_input_doc:
        shaping_input_doc["output"] = {}

    font: TTFont
    for font in parsed_args.fonts:
        filename = Path(font.reader.file.name)
        with open(filename, "rb") as fontfile:
            hb_face = hb.Face(fontfile.read())
        shaping_input_doc["output"][filename.name] = shape_texts(
            font,
            hb_face,
            shaping_texts,
            shaping_script,
            shaping_language,
            shaping_direction,
            shaping_features,
            shaping_comparison_mode,
        )

    shaping_file_json.write_text(
        json.dumps(shaping_input_doc, indent=2, ensure_ascii=False)
    )
