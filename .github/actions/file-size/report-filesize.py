# Copyright 2021 Google Sans Flex Authors

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys

from fontTools.ttLib import TTFont
from rich.console import Console
from rich.table import Table


def main(argv):
    total_filesize = 0
    total_encoded_glyphs = 0
    total_glyphs = 0

    print(f"\n\n{'='*30} FILE SIZE REPORT {'='*30}\n")
    for filepath in sorted(argv):
        tt = TTFont(filepath)
        this_file_size = os.path.getsize(filepath)
        total_filesize += this_file_size
        total_encoded_glyphs += len(tt.getBestCmap())
        total_glyphs += len(tt["glyf"].glyphs)
        clean_name = filepath.replace("/github/workspace/", "", 1).replace(
            "fonts/", "", 1
        )
        print(f"{this_file_size} bytes: {clean_name}")

    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Summary Stats", style="dim", width=25, justify="right")
    table.add_column("Size (B)", justify="right")
    table.add_row(
        "Total",
        f"{total_filesize/1.0:.2f}",
    )
    table.add_row("Avg per font", f"{total_filesize/len(argv):.2f}")
    table.add_row("Avg per encoded glyph", f"{total_filesize/total_encoded_glyphs:.2f}")
    table.add_row("Avg per total glyph", f"{total_filesize/total_glyphs:.2f}")
    console.print(table)
    print(f"\n{'='*78}")


if __name__ == "__main__":
    main(sys.argv[1:])
