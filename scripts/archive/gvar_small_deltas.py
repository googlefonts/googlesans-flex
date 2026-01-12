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

from argparse import ArgumentParser
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_v_a_r import TupleVariation

DEFAULT_TTF_PATH = (
    Path(__file__).parent.parent
    / "fonts/variable/GoogleSansFlex[GRAD,ROND,opsz,slnt,wdth,wght].ttf"
)
FINE_ADJUSTMENT_AXES = ("GRAD", "ROND", "slnt")


def main(
    ttf_path: Path,
    threshold: float = 20.0,
    strip: Path | None = None,
    verbose: bool = False,
) -> None:
    font = TTFont(ttf_path)
    gvar = font["gvar"]

    insignificant_tuple_variation_block_count = 0
    tuple_variation_block_count = 0
    for glyph_name, tuple_variations in gvar.variations.items():
        to_remove = []
        for tv_index, tuple_variation in enumerate(tuple_variations):
            assert isinstance(tuple_variation, TupleVariation)

            tuple_variation_block_count += 1
            if all(
                abs(coord[0]) < threshold and abs(coord[1]) < threshold
                for coord in tuple_variation.coordinates
                if coord is not None
            ):
                insignificant_tuple_variation_block_count += 1
                pos = {
                    axis: value
                    for axis, (_min, value, _max) in tuple_variation.axes.items()
                    if value != 0
                }
                if verbose:
                    print(f"{glyph_name} @ {pos}")
                # Remove insignificant delats, only if the delta isn't for a
                # 'fine adjustment' axis
                if strip is not None and all(
                    axis not in pos for axis in FINE_ADJUSTMENT_AXES
                ):
                    to_remove.append(tv_index)

        for tv_index in sorted(to_remove, reverse=True):
            del tuple_variations[tv_index]

    percent = (
        insignificant_tuple_variation_block_count / tuple_variation_block_count * 100
    )
    print(
        f"{insignificant_tuple_variation_block_count}/{tuple_variation_block_count} ({percent:.1f}%) insignificant"
    )

    if new_path := strip:
        font.save(new_path.with_suffix(".ttf"))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "ttf_path",
        type=Path,
        nargs="?",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        type=float,
        default=5.0,
    )
    parser.add_argument(
        "--strip",
        type=Path,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
    )

    args = parser.parse_args()
    main(
        args.ttf_path if args.ttf_path is not None else DEFAULT_TTF_PATH,
        args.threshold,
        args.strip,
        args.verbose,
    )
