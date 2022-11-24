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

"""Rebuild Designspaces from the available UFOs."""

import argparse
from pathlib import Path

from fontTools.designspaceLib import DesignSpaceDocument

ROOT_DIR = Path(__file__).parent.parent


parser = argparse.ArgumentParser()
parser.add_argument(
    "--source-dir",
    type=Path,
    default=ROOT_DIR / "sources",
    help="Path to source directory.",
)
parsed_args = parser.parse_args()
source_dir: Path = parsed_args.source_dir

for designspace_path in source_dir.glob("*.designspace"):
    designspace = DesignSpaceDocument.fromfile(designspace_path)
    designspace.sources.clear()
    tag2name = {a.tag: a.name for a in designspace.axes}

    family_name = designspace_path.stem
    for ufo_path in  source_dir.glob(f"{family_name}-*.ufo"):
        location_strings = ufo_path.stem.split("-")[1:]
        location_by_tag = {tag2name[s[:4]]:float(s[4:]) for s in location_strings}
        designspace.addSourceDescriptor(filename=ufo_path.name, familyName=family_name, location=location_by_tag)

    designspace.write(designspace_path)

