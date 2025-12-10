# MenuTitle: Duplicate Selected Node

from GlyphsApp import Glyphs, QCURVE, CURVE, LINE

layer = Glyphs.font.selectedLayers[0]

selectedNode = layer.selection[0]
compareString = layer.compareString()
indexPath = layer.indexPathOfNode_(selectedNode)
pathIndex = indexPath.indexAtPosition_(0)
nodeIndex = indexPath.indexAtPosition_(1)
for currLayer in layer.parent.layers:
	if currLayer.compareString() != compareString:
		continue
	path = currLayer.shapes[pathIndex]
	node = path.nodes[nodeIndex].copy()
	if node.type == QCURVE or node.type == CURVE:
		node.type = LINE
	path.nodes.insert(nodeIndex + 1, node)
