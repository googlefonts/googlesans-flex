# Copyright 2020 Google Sans Authors
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
import logging
import shutil
import sys
from pathlib import Path
from typing import List, Optional

from fontTools.subset import main as subset_main
from fontTools.ttLib import TTFont


def main(args: Optional[List[str]] = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("fonts", nargs="+", type=Path, help="Fonts to subset in-place.")
    parsed_args = parser.parse_args(args)

    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.WARNING)
    LOGGER = logging.getLogger(__name__)

    for font in parsed_args.fonts:
        local_filepath = font.resolve()
        local_filepath_subset = f"{local_filepath}.subset"

        # The subsetter configuration preserves all OT feature support.
        # It will remove unused, unencoded glyphs.
        subset_args_expert = [
            str(local_filepath),
            "--unicodes=*",
            "--no-ignore-missing-glyphs",
            "--notdef-outline",
            "--layout-features=*",
            "--name-IDs=*",
            "--name-languages=*",
            "--glyph-names",
            "--no-prune-unicode-ranges",
            "--recalc-bounds",
            "--recalc-average-width",
            f"--output-file={local_filepath_subset}",
        ]

        try:
            subset_main(subset_args_expert)
        except Exception as e:
            LOGGER.error(
                "ERROR: subsetting error during attempt to subset %s: %s",
                local_filepath,
                str(e),
            )
            sys.exit(1)

        try:
            shutil.move(local_filepath_subset, local_filepath)
        except Exception as e:
            LOGGER.error(
                "ERROR: during move of subset file %s: %s",
                local_filepath,
                str(e),
            )
            sys.exit(1)

        # As of fontTools 4.38.0, the `--recalc-average-width` flag above is
        # ignored, so we need to manually trigger the recalculation.
        font_again = TTFont(local_filepath)
        font_again["OS/2"].recalcAvgCharWidth(font_again)
        font_again.save(local_filepath)


if __name__ == "__main__":
    main()
