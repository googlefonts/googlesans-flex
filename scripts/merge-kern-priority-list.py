#!/usr/bin/env python3
# Copyright 2023 Google Sans Authors
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

"""Print a priority list (most to least interesting) of kerning pairs to check.

Interesting-ness is based on how often designers kern that particular
combination, see Simon Cozens findings in
https://typedrawers.com/discussion/2707/most-common-kern-pairs.
"""


from __future__ import annotations

from pathlib import Path

import glyphsLib.glyphdata

MANUAL_LIST = Path(__file__).parent / "data" / "interesting_kern_pairs.txt"
FREQUENCY_LIST = Path(__file__).parent / "data" / "top-10000.txt"


def main() -> None:
    # Prime GLYPHDATA:
    glyphsLib.glyphdata.get_glyph("a")
    glyph_data = glyphsLib.glyphdata.GLYPHDATA

    frequency_list: dict[tuple[str, str], int] = {}
    for line in FREQUENCY_LIST.read_text().splitlines():
        if not line:
            continue
        frequency, first, second = line.strip().split()
        frequency_list[(first, second)] = int(frequency)

    manual_pairs = set()
    manual_pairs2text = {}
    for line_number, line in enumerate(MANUAL_LIST.read_text().splitlines(), start=1):
        if not line:
            continue
        line = line.strip()
        if len(line) != 2:
            print(
                f"Invalid line at line number {line_number}: {line}; should always be 2 characters per line"
            )
            continue
        first, second = line.strip()

        first_name = glyph_data.unicodes[f"{ord(first):04X}"]["name"]
        second_name = glyph_data.unicodes[f"{ord(second):04X}"]["name"]
        pair = first_name, second_name

        if pair in frequency_list:
            manual_pairs.add(pair)
            manual_pairs2text[pair] = line
        else:
            print(f"No frequency data for '{line}' {pair}")

    print(
        "\n".join(
            manual_pairs2text[pair]
            for pair in sorted(manual_pairs, key=lambda pair: -frequency_list[pair])
        )
    )


if __name__ == "__main__":
    main()
