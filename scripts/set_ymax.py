# Copyright 2024 Google Sans Flex Authors
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

"""Tiny script for setting the yMax of a font."""

from argparse import ArgumentParser
from pathlib import Path

from fontTools.ttLib import TTFont


def main():
    parser = ArgumentParser()
    parser.add_argument("ttf", type=Path)
    parser.add_argument("ymax", type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    ttf = TTFont(args.ttf)
    ymax: int = args.ymax

    print(f"ymax {ttf['head'].yMax} -> {ymax}")
    ttf["head"].yMax = ymax
    ttf.save(args.output)


if __name__ == "__main__":
    main()
