# MenuTitle: Show all out of sync layers

from GlyphsApp import Glyphs

layers = []
for layer in Glyphs.font.selectedLayers[0].parent.layers:
	if layer.isMasterLayer and layer.metricsKeysOutOfSync():
		print(layer)
		layers.append(layer)

Glyphs.font.newTab(layers)
