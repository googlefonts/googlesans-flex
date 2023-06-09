import argparse
import csv

from fontTools.ttLib import TTFont
from fontTools.misc.fixedTools import otRound

parser = argparse.ArgumentParser()
parser.add_argument("font", type=TTFont)
parsed_args = parser.parse_args()
font: TTFont = parsed_args.font


WGHTS = (
    1.0,
    400.0,
    449.0,
    450.0,
    579.0,
    580.0,
    698.999,
    699.0,
    699.999,
    700.0,
    1000.0,
)

csvfile = open("eggs.csv", "w", newline="")
csv_writer = csv.writer(csvfile)
csv_writer.writerow(("", *(f"{wght=}" for wght in WGHTS)))

for opsz in (6.0, 17.999, 18.0, 144.0):
    for wdth in (25.0, 39.999, 40.0, 50.0, 85.0, 100.0, 151.0):
        for rond in (0.0, 100.0):
            for grad in (-50.0, 0.0, 50.0):
                index_str = f"{rond=}, {grad=}, {opsz=}, {wdth=}"
                wght_wdths = []

                for wght in WGHTS:
                    gs = font.getGlyphSet(
                        location={
                            "ROND": rond,
                            "GRAD": grad,
                            "opsz": opsz,
                            "wdth": wdth,
                            "wght": wght,
                        }
                    )
                    wght_wdths.append(otRound(gs["space"].width))
                csv_writer.writerow((index_str, *wght_wdths))
