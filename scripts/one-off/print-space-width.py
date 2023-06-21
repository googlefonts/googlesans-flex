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

import argparse
import csv

from fontTools.ttLib import TTFont
from fontTools.misc.fixedTools import otRound

parser = argparse.ArgumentParser()
parser.add_argument("font", type=TTFont)
parsed_args = parser.parse_args()
font: TTFont = parsed_args.font


WGHTS = (
    1.0,
    400.0,
    449.0,
    450.0,
    579.0,
    580.0,
    698.999,
    699.0,
    699.999,
    700.0,
    1000.0,
)

csvfile = open("eggs.csv", "w", newline="")
csv_writer = csv.writer(csvfile)
csv_writer.writerow(("", *(f"{wght=}" for wght in WGHTS)))

for rond in (0.0, 100.0):
    for opsz in (6.0, 17.999, 18.0, 144.0):
        for wdth in (25.0, 39.999, 40.0, 50.0, 85.0, 100.0, 151.0):
            index_str = f"{opsz=}, {wdth=}, {rond=}"
            wght_wdths = []

            for wght in WGHTS:
                gs = font.getGlyphSet(
                    location={
                        "ROND": rond,
                        "opsz": opsz,
                        "wdth": wdth,
                        "wght": wght,
                    }
                )
                wght_wdths.append(otRound(gs["space"].width))
            csv_writer.writerow((index_str, *wght_wdths))
