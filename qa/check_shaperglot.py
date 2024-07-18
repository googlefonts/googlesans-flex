#!/usr/bin/env python3

# Copyright 2024 Google Sans Authors
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
from sys import exit

from shaperglot.checker import Checker
from shaperglot.languages import Languages
from shaperglot.reporter import Reporter, Result

TARGET_LANGS_PATH = Path(__file__).parent / "target_langs.txt"


def get_worst_status(reporter: Reporter) -> Result:
    # SKIP means some checks were omitted because they weren't relevant to the
    # font, which is less important than any other status
    ORDERING = (Result.SKIP, Result.PASS, Result.WARN, Result.FAIL)
    return max(
        (message.result for message in reporter.results),
        key=ORDERING.index,
        # Can't be PASS/FAIL, otherwise doesn't really matter
        default=Result.WARN,
    )


def main(font_paths: list[Path]) -> int:
    shaperglot_lang_config = Languages()
    language_list = [
        shaperglot_lang_config[lang]
        for lang in TARGET_LANGS_PATH.read_text().splitlines()
    ]

    exit_status = 0
    for font_path in font_paths:
        print(f"{font_path}:")
        checker = Checker(font_path)
        for target_lang_config in language_list:
            report = checker.check(target_lang_config)
            worst = get_worst_status(report)
            if report.is_unknown:
                # Display unknown as SKIP
                print(
                    f"  {Result.SKIP.value} {target_lang_config['name']} "
                    "(not supported by shaperglot)"
                )
            elif worst == Result.PASS:
                print(f"  {worst.value} {target_lang_config['name']}")
            else:
                print(f"  {target_lang_config['name']}:")
                exit_status = 1
                for message in report.results:
                    if message.result == Result.PASS or message.result == Result.SKIP:
                        continue
                    print(f"    {message}")
        print()
    return exit_status


if __name__ == "__main__":
    parser = ArgumentParser(description="Check language coverage using shaperglot")
    parser.add_argument(
        "font_paths",
        help="TTF(s) to check",
        nargs="+",
        type=Path,
        metavar="ttf",
    )
    args = parser.parse_args()

    exit(main(args.font_paths))
