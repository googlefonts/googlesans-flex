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

"""Update the glyph_metadata.csv file."""

import argparse
from pathlib import Path

import ufo_glyphdata_manager.__main__
import glyphsLib.glyphdata


ROOT_DIR = Path(__file__).parent.parent


def main(csv_path: Path):
    glyphdata = ufo_glyphdata_manager.__main__.read_csv(csv_path)

    for name, data in glyphdata.items():
        unicodes = [hex(uv)[2:] for uv in data.unicodes]
        glyphsapp_data = glyphsLib.glyphdata.get_glyph(name, unicodes=unicodes)

        name_sanitized = name.replace("-", "")
        if (prod_name := glyphsapp_data.production_name) != name_sanitized:
            data.postscript_name = prod_name
        elif name != name_sanitized:
            print(
                f"INFO: automatically to specified postscript name for {name} by "
                "removing dashes"
            )
            data.postscript_name = name_sanitized
        else:
            data.postscript_name = None

    ufo_glyphdata_manager.__main__.write_csv(csv_path, glyphdata)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path, help="Path to the glyph data CSV.")
    parsed_args = parser.parse_args()
    main(parsed_args.csv)
