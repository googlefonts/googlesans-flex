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

from fontTools.unicodedata import normalize
from ufoLib2 import Font

UFOS = [
    "sources/GoogleSansFlex-wg1-wd25-oz6-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz6-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz6-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz6-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz6-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz6-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz6-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz6-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz18-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz18-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz18-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz18-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz18-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz18-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz18-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz18-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz144-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz144-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz144-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz144-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz144-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz144-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz144-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd25-oz144-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz6-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz6-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz6-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz6-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz6-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz6-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz6-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz6-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz18-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz18-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz18-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz18-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz18-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz18-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz18-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz18-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz144-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz144-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz144-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz144-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz144-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz144-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz144-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd100-oz144-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz6-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz6-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz6-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz6-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz6-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz6-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz6-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz6-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz18-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz18-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz18-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz18-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz18-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz18-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz18-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz18-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz144-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz144-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz144-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz144-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz144-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz144-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz144-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1-wd151-oz144-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz6-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz6-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz6-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz6-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz6-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz6-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz6-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz6-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz18-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz18-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz18-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz18-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz18-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz18-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz18-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz18-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz144-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz144-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz144-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz144-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz144-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz144-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz144-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd25-oz144-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz6-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz6-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz6-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz6-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz6-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz6-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz6-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz6-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz18-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz18-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz18-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz18-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz18-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz18-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz18-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz18-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz144-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz144-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz144-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz144-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz144-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz144-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz144-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd100-oz144-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz6-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz6-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz6-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz6-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz6-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz6-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz6-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz6-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz18-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz18-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz18-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz18-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz18-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz18-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz18-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz18-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz144-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz144-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz144-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz144-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz144-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz144-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz144-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg400-wd151-oz144-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz6-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz6-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz6-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz6-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz6-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz6-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz6-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz6-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz18-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz18-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz18-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz18-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz18-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz18-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz18-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz18-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz144-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz144-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz144-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz144-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz144-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz144-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz144-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd25-oz144-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz6-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz6-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz6-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz6-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz6-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz6-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz6-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz6-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz18-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz18-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz18-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz18-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz18-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz18-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz18-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz18-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz144-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz144-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz144-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz144-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz144-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz144-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz144-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd100-oz144-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz6-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz6-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz6-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz6-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz6-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz6-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz6-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz6-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz18-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz18-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz18-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz18-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz18-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz18-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz18-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz18-GD100-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz144-GD0-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz144-GD0-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz144-GD0-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz144-GD0-RD100-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz144-GD100-RD0-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz144-GD100-RD0-sl0.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz144-GD100-RD100-sl-10.ufo",
    "sources/GoogleSansFlex-wg1000-wd151-oz144-GD100-RD100-sl0.ufo",
]

# Copied from current feature file
# Maybe not needed?
# CombiningTopAccents = [
#     "gravecomb",
#     "acutecomb",
#     "circumflexcomb",
#     "tildecomb",
#     "macroncomb",
#     "brevecomb",
#     "dotaccentcomb",
#     "dieresiscomb",
#     "ringcomb",
#     "hungarumlautcomb",
#     "caroncomb",
#     "commaturnedabovecomb",
# ]


def main():
    # Extract glyph names just from 1 UFO
    first = UFOS[0]
    font = Font.open(first)
    cmap = {}
    precomposed = []
    for glyph in font:
        for code_point in glyph.unicodes:
            cmap[code_point] = glyph.name
            nfd = normalize("NFD", chr(code_point))
            if len(nfd) >= 2:
                precomposed.append((glyph.name, nfd))

    ccmp = [
        "lookup ccmp_top_accents {",
        "  lookupflag UseMarkFilteringSet @CombiningTopAccents;",
    ]
    errors = []
    for glyph, decomposed in sorted(precomposed):
        try:
            comment = glyph in font.lib.get("public.skipExportGlyphs", [])
            if comment:
                ccmp.append(f"  # {glyph} isn't currently exported")
            ccmp.append(
                f" {' #' if comment else ''} sub {glyph}' @CombiningTopAccents by {' '.join(cmap[ord(part_code_point)] for part_code_point in decomposed)};"
            )
        except KeyError:
            errors.append(f"# Error: No ccmp for {glyph}")
    ccmp.append("} ccmp_top_accents;")

    print("\n".join(ccmp))
    print("\n".join(errors))

    print("Insert the above by hand into the Glyphs.app source file, then test")


if __name__ == "__main__":
    main()
