# MenuTitle: Calculate OS/2 Sub/Superscript
# -*- coding: utf-8 -*-

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