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
import shutil
import yaml

from scripts.gs_merge_designspace import main as merge
from scripts.gs_normalize_designspace import main as normalize
from scripts.fix_metadata_in_sources import main as fix_metadata

REPLACE_TARGET_DESIGNSPACE = True
FOLLOW_GLYPHS = True  # while sources are in flux

WORKSPACE_ROOT = Path("/github/workspace")
SOURCE_DIR = WORKSPACE_ROOT / "source"
TARGET_DIR = WORKSPACE_ROOT / "target"
GLYPH_LIST = Path("/glyph-list.txt")
CONFIG_FILE = Path("sources/config.yaml")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Takes designspaces specified in the sources/config.yaml of the SOURCE branch
file_text = (SOURCE_DIR / CONFIG_FILE).read_text()
gftools_config = yaml.safe_load(file_text)
for designspace_path in gftools_config["sources"]:
    logging.info(f"Merging {designspace_path}")
    src_ds_path = designspace_path.replace("regular", "roman", 1)
    merge(
        SOURCE_DIR / "sources" / src_ds_path,
        TARGET_DIR / "sources" / designspace_path,
        GLYPH_LIST,
        REPLACE_TARGET_DESIGNSPACE,
        FOLLOW_GLYPHS,
    )

    ds_sources_dir = Path(designspace_path).parent
    logging.info(f"Normalising {ds_sources_dir}")
    normalize(
        TARGET_DIR / "sources" / ds_sources_dir,
    )

    logging.info(f"Fixing metadata")
    fix_metadata(
        TARGET_DIR / "sources" / designspace_path,
    )

logging.info("Done!")
