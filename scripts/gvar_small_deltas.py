from argparse import ArgumentParser
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_v_a_r import TupleVariation

DEFAULT_TTF_PATH = (
    Path(__file__).parent.parent
    / "fonts/variable/GoogleSansFlex[GRAD,ROND,opsz,slnt,wdth,wght].ttf"
)


def main(ttf_path: Path, threshold: float = 20.0, verbose: bool = False) -> None:
    font = TTFont(ttf_path)
    gvar = font["gvar"]

    insignificant_tuple_variation_block_count = 0
    tuple_variation_block_count = 0
    for glyph_name, tuple_variations in gvar.variations.items():
        for tuple_variation in tuple_variations:
            assert isinstance(tuple_variation, TupleVariation)

            tuple_variation_block_count += 1
            if all(
                abs(coord[0]) < threshold and abs(coord[1]) < threshold
                for coord in tuple_variation.coordinates
                if coord is not None
            ):
                insignificant_tuple_variation_block_count += 1
                if verbose:
                    pos = {
                        axis: value
                        for axis, (_min, value, _max) in tuple_variation.axes.items()
                        if value != 0
                    }
                    print(f"{glyph_name} @ {pos}")

    print(
        f"{insignificant_tuple_variation_block_count}/{tuple_variation_block_count} insignificant"
    )


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
        default=20.0,
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
        args.verbose,
    )
