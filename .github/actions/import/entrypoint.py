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

import logging
from pathlib import Path
import yaml

from scripts.gs_merge_designspace import merge_designspace
from scripts.gs_normalize_designspace import normalize_in_dir
from scripts.fix_metadata_in_sources import fix_metadata

REPLACE_TARGET_DESIGNSPACE = False
FOLLOW_GLYPHS = True  # while sources are in flux

WORKSPACE_ROOT = Path("/github/workspace")
SOURCE_DIR = WORKSPACE_ROOT / "source"
TARGET_DIR = WORKSPACE_ROOT / "target"
GLYPH_LISTS_DIR = Path("/glyph-lists")
DEFAULT_GLYPH_LIST_PATH = GLYPH_LISTS_DIR / "regular.txt"
CONFIG_FILE = Path("sources/config.yaml")


def get_glyph_list_path(designspace_path: str) -> Path:
    # designspace_path: "regular/GoogleSansFlex.designspace", so parent is "regular"
    style = Path(designspace_path).parent
    preferred_path = GLYPH_LISTS_DIR / f"{style}.txt"
    if preferred_path.exists():
        return preferred_path
    else:
        logging.info(f"no specific glyph list for {style}, using default")
        return DEFAULT_GLYPH_LIST_PATH


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Takes designspaces specified in the sources/config.yaml of the SOURCE branch
    file_text = (SOURCE_DIR / CONFIG_FILE).read_text()
    gftools_config = yaml.safe_load(file_text)
    for designspace_path in gftools_config["sources"]:
        if designspace_path == "GoogleSansFlex.designspace":
            # Skip this (Full) designspace because italics is already imported by italic/GoogleSansFlex-Italic.designspace
            continue
        logging.info(f"Merging {designspace_path}")
        designspace_path_target = designspace_path.replace("roman/", "regular/", 1)
        merge_designspace(
            SOURCE_DIR / "sources" / designspace_path,
            TARGET_DIR / "sources" / designspace_path_target,
            get_glyph_list_path(designspace_path),
            REPLACE_TARGET_DESIGNSPACE,
            FOLLOW_GLYPHS,
        )

        ds_sources_dir = Path(designspace_path_target).parent
        logging.info(f"Normalising {ds_sources_dir}")
        normalize_in_dir(
            TARGET_DIR / "sources" / ds_sources_dir,
        )

        logging.info("Fixing metadata")
        fix_metadata(
            TARGET_DIR / "sources" / designspace_path_target,
        )

    logging.info("Done!")


if __name__ == "__main__":
    main()
