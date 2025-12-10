# MenuTitle: Calculate OS/2 Sub/Superscript
# -*- coding: utf-8 -*-

# Copyright 2024 Google Sans Project Authors

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ComputePositionsOfSmallNumbers import measure
from GlyphsApp import Glyphs

font = Glyphs.font

UPM = font.upm

def calcValues(master):
	
	height = measure(master, ".denominator")
	superGlyph = font.glyphs["onesuperior"]
	superLayer = superGlyph.layers[master.id]
	superComponent = superLayer.shapes[0]

	subGlyph = font.glyphs["onesubscript"]
	subLayer = subGlyph.layers[master.id]
	subComponent = subLayer.shapes[0]
	
	capHeight = master.capHeight
	
	size = round(UPM * height / capHeight)
	
	master.customParameters["subscriptXOffset"] = 0
	master.customParameters["subscriptXSize"] = size
	master.customParameters["subscriptYOffset"] = -subComponent.y
	master.customParameters["subscriptYSize"] = size

	master.customParameters["superscriptXOffset"] = 0
	master.customParameters["superscriptXSize"] = size
	master.customParameters["superscriptYOffset"] = superComponent.y
	master.customParameters["superscriptYSize"] = size

master = font.masters[0]
calcValues(master)