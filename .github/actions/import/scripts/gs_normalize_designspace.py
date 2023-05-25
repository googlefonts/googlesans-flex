#!/usr/bin/env python3
# Copyright 2022 Google Sans Authors
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

"""Normalize all Designspaces and attached UFOs in a directory to match the
source conventions."""

import argparse
from pathlib import Path
from typing import Sequence, Optional

from fontTools.designspaceLib import DesignSpaceDocument

from .internal import normalize

ROOT_DIR = Path(__file__).parent.parent


def main(args: Optional[Sequence[str]] = None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=ROOT_DIR / "sources",
        help="Path to source directory.",
    )
    parsed_args = parser.parse_args(args=args)
    normalize_in_dir(parsed_args.source_dir)


def normalize_in_dir(source_dir: Path) -> None:
    for designspace_path in source_dir.glob("*.designspace"):
        designspace = DesignSpaceDocument.fromfile(designspace_path)

        normalize.scrub_designspace(designspace, ROOT_DIR)

        for source in designspace.sources:
            source.font.save()
        designspace.write(designspace_path)


if __name__ == "__main__":
    main()
