#!/usr/bin/env -S uv run --script

# Copyright 2020 Google Sans Authors

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# /// script
# dependencies = [
#     "fontspectorapi",
#     "fontTools",
#     "uharfbuzz",
# ]
# ///

import json
import sys
import textwrap
from pathlib import Path

import uharfbuzz
from fontspectorapi import (
    FAIL,
    PASS,
    SKIP,
    CheckStatuses,
    Plugin,
    check,
    plugin_main,
)
from fontTools.ttLib import TTFont

# Make Fontspector able to find the update_shaping_test_data package.
# TODO: is this still necessary now we're a Fontspector plugin?
sys.path.append(str(Path(__file__).parent.parent))

from qa.update_shaping_test_data import ComparisonMode, Direction, shape_texts


@check(
    id="shaping/regression",
    title="Check feature code behaviour",
    rationale="But does it still shape the same?",
)
def features_regression(font_path: Path) -> CheckStatuses:
    ttFont = TTFont(font_path)
    hb_font = uharfbuzz.Face(font_path.read_bytes())  # type: ignore

    if "Google Sans Flex TV" in ttFont["name"].getDebugName(1):  # type: ignore
        yield SKIP, "Font is not interesting to check."
        return

    shaping_file_found = False
    shaping_basedir = Path("qa", "shaping")
    for shaping_file in shaping_basedir.glob("*.json"):
        shaping_file_found = True
        shaping_input_doc = json.loads(shaping_file.read_text())

        try:
            shaping_input = shaping_input_doc["input"]
        except KeyError:
            yield FAIL, (f"{shaping_file}: Must have an 'input' key dict.")
            return
        try:
            shaping_texts = shaping_input["text"]
        except KeyError as e:
            yield FAIL, (f"{shaping_file}: 'input' key dict is missing {str(e)} key.")
            return
        shaping_features = shaping_input.get("features", {})
        shaping_script = shaping_input.get("script")
        shaping_language = shaping_input.get("language")
        shaping_comparison_mode = ComparisonMode(
            shaping_input.get("comparison_mode", "full")
        )
        shaping_direction = Direction(shaping_input.get("direction", "ltr"))
        try:
            shaping_output = shaping_input_doc["output"]
        except KeyError:
            yield FAIL, (f"{shaping_file}: Must have an 'output' key dict.")
            return
        try:
            shaped_texts_expected = shaping_output[font_path.name]
        except KeyError:
            yield FAIL, f"{shaping_file}: No entry found for {font_path.name}"
            return

        shaped_texts = shape_texts(
            ttFont,
            hb_font,
            shaping_texts,
            shaping_script,
            shaping_language,
            shaping_direction,
            shaping_features,
            shaping_comparison_mode,
        )

        if shaped_texts == shaped_texts_expected:
            yield PASS, f"{shaping_file}: No regression detected"
        else:
            if "fvar" in ttFont:
                assert isinstance(shaped_texts, dict)
                assert isinstance(shaped_texts_expected, dict)

                for key, shaped_text in shaped_texts.items():
                    try:
                        expected = shaped_texts_expected[key]
                    except KeyError as e:
                        yield (
                            FAIL,
                            (
                                f"{shaping_file}: No entry found for {font_path.name}, "
                                f" instance {e}"
                            ),
                        )
                        continue
                    if shaped_text != expected:
                        shaped_texts_str = textwrap.indent(
                            "\n".join(shaped_text), "\t  "
                        )
                        shaped_texts_expected_str = textwrap.indent(
                            "\n".join(expected), "\t  "
                        )
                        yield (
                            FAIL,
                            (
                                f"{shaping_file}: Expected and actual shaping not matching."
                                f"\n\tExpected for {key}:\n"
                                f"{shaped_texts_expected_str}"
                                "\n\tActual:\n"
                                f"{shaped_texts_str}"
                            ),
                        )
            else:
                assert isinstance(shaped_texts, list)
                assert isinstance(shaped_texts_expected, list)

                shaped_texts_str = textwrap.indent("\n".join(shaped_texts), "\t  ")
                shaped_texts_expected_str = textwrap.indent(
                    "\n".join(shaped_texts_expected), "\t  "
                )
                yield (
                    FAIL,
                    (
                        f"{shaping_file}: Expected and actual shaping not matching."
                        "\n\tExpected:\n"
                        f"{shaped_texts_expected_str}"
                        "\n\tActual:\n"
                        f"{shaped_texts_str}"
                    ),
                )

    if not shaping_file_found:
        yield SKIP, "No test files found."

def register(plugin: Plugin) -> None:
    plugin.register_simple_profile(
        "gs-shaping",
        (features_regression,),
        section_name="Google Sans Shaping Regression Checks",
    )


if __name__ == "__main__":
    raise SystemExit(plugin_main(register, plugin_name="gs-shaping"))
