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

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Takes designspaces specified in the sources/config.yaml of the SOURCE branch
with open("/github/workspace/source/sources/config.yaml", "r") as file:
    gftools_config = yaml.safe_load(file)
    for designspace_path in gftools_config["sources"]:
        logging.info(f"Merging {designspace_path}")
        src_ds_path = designspace_path.replace("regular", "roman", 1)
        merge(
            Path(f"/github/workspace/source/sources/{src_ds_path}"),
            Path(f"/github/workspace/target/sources/{designspace_path}"),
            Path("/glyph-list.txt"),
            REPLACE_TARGET_DESIGNSPACE,
            FOLLOW_GLYPHS,
        )

        sources_dir = Path(designspace_path).parent
        logging.info(f"Normalising {sources_dir}")
        normalize(
            Path(f"/github/workspace/target/sources/{sources_dir}"),
        )

        logging.info(f"Fixing metadata")
        fix_metadata(
            Path(f"/github/workspace/target/sources/{designspace_path}"),
        )

shutil.copy2(
    "/github/workspace/source/sources/config.yaml",
    "/github/workspace/target/sources/config.yaml",
)
logging.info("Done!")
