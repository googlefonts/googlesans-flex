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

import argparse
from pathlib import Path
import string

from fontTools.ttLib import TTFont

parser = argparse.ArgumentParser()
parser.add_argument(
    "font", type=Path, nargs="+", help="The font to sanitize the name table of."
)
args = parser.parse_args()
paths: Path = args.font


def ascii_alphanumeric_str(text: str) -> str:
    allowed = set(string.ascii_letters + string.digits + ".,; ")
    return "".join(c if c in allowed else "_" for c in text)


for path in paths:
    font: TTFont = TTFont(path)

    name = font["name"]
    for record in name.names:
        if record.nameID != 5:
            continue
        record.string = ascii_alphanumeric_str(record.toStr())

    font.save(path)
