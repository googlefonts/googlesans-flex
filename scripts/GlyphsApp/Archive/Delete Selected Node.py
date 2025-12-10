# MenuTitle: Delete Selected Node

from GlyphsApp import Glyphs

layer = Glyphs.font.selectedLayers[0]

selectedNode = layer.selection[0]
indexPath = layer.indexPathOfNode_(selectedNode)
pathIndex = indexPath.indexAtPosition_(0)
nodeIndex = indexPath.indexAtPosition_(1)
for currLayer in layer.parent.layers:
	path = currLayer.shapes[pathIndex]
	node = selectedNode.copy()
	del path.nodes[nodeIndex]
