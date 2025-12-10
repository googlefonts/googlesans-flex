# MenuTitle: Clean Unaccessible Kerning

from GlyphsApp import Glyphs

font = Glyphs.font

for master in font.masters:
	if not font.kerning.get(master.id):
		continue
	mappedId = font.masterIDforMetrics_(master.id)
	if mappedId != master.id:
		print("!! unneeded kerning in master", master.name)
		del font.kerning[master.id]