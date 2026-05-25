#!/usr/bin/env python

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

from pathlib import Path

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

# v1.100 feature set:
VAR_UPRIGHT_FEA = [
    "aalt",
    "calt",
    "ccmp",
    "dlig",
    "dnom",
    "frac",
    "kern",
    "liga",
    "lnum",
    "locl",
    "mark",
    "mkmk",
    "numr",
    "ordn",
    "pnum",
    "sinf",
    "ss01",
    "ss02",
    # Added in v4.000
    "ss09",
    "subs",
    "sups",
    "tnum",
    "zero",
]


@check(
    id="fea/included_features",
    title="Check feature inclusion",
    rationale="Confirms that the font builds contain expected feature tags.",
)
def included_features_variable_uprights(font_path: Path) -> CheckStatuses:
    """Confirms that the upright builds contain expected feature tags."""

    ttf = TTFont(font_path)

    if "fvar" not in ttf or "Italic" in font_path.stem:
        yield SKIP, "Not upright VF"
        return
    elif "Google Sans Flex TV" in ttf["name"].getDebugName(1):  # type: ignore
        yield SKIP, "Font is not interesting to check."
        return

    gpos = ttf.get("GPOS")
    gsub = ttf.get("GSUB")

    if gpos is None or gsub is None:
        yield FAIL, "Font must contain a 'GPOS' and 'GSUB' table"
        return

    fea_tags = set()

    for gpos_record in gpos.table.FeatureList.FeatureRecord:
        fea_tags.add(gpos_record.FeatureTag)

    for gsub_record in gsub.table.FeatureList.FeatureRecord:
        fea_tags.add(gsub_record.FeatureTag)

    if sorted(fea_tags) == VAR_UPRIGHT_FEA:
        yield PASS, "Font contains the expected feature tags"
    else:
        yield (
            FAIL,
            "Font does not contain the expected feature tags.\n"
            f"Found:{sorted(fea_tags)}\nExpected:{VAR_UPRIGHT_FEA}",
        )


def register(plugin: Plugin) -> None:
    plugin.register_simple_profile(
        "gs-fea",
        (included_features_variable_uprights,),
        section_name="Google Sans Custom Feature Support Checks",
    )


if __name__ == "__main__":
    raise SystemExit(plugin_main(register, plugin_name="gs-fea"))
