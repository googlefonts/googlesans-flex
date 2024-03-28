from pathlib import Path
from ufoLib2 import Font

from collections import defaultdict

results = defaultdict(list)
for ufo_path in Path("sources").glob("*.ufo"):
    font = Font.open(ufo_path, validate=False)
    results[tuple(font.info.openTypeOS2Panose)].append(ufo_path.name)

for panose, ufos in results.items():
    print(panose)
    for ufo in ufos:
        print(f"  - {ufo}")
    print()
