# MenuTitle: Align With Sharp

from GlyphsApp import Glyphs, GSNode, Message
from importlib import reload
import FlexRounder
reload(FlexRounder)
# from FlexRounder import roundMasters
from flexLib import axesValues, masterNearestToPosition


def roundLayer(layer, font):
	roundAxis = font.axisForTag_("ROND")
	roundAxisIdx = font.axes.index(roundAxis)
	roundMaster = layer.master
	roundValue = roundMaster.internalAxesValues[roundAxis.axisId]
	if roundValue < 10:
		Message("please select a round master")
		return

	axisValueList = axesValues(roundMaster)
	axisValueList[roundAxisIdx] = 0
	sharpMaster = masterNearestToPosition(font, axisValueList)
	sharpValue = sharpMaster.internalAxesValues[roundAxis.axisId]
	if sharpValue > 10:
		print("Didn’t find a sharp master")
		return
	# roundMasters(layer.parent, sharpMaster, roundMaster)
	sharpLayer = layer.parent.layers[sharpMaster.id]
	print("__sharpLayer", sharpLayer)

	for element in layer.selection:
		if not isinstance(element, GSNode):
			continue

		indexPath = layer.indexPathOfNode_(element)
		sharpNode = sharpLayer.nodeAtIndexPath_(indexPath)
		element.position = sharpNode.position


if __name__ == "__main__":

	font = Glyphs.font
	font.disableUpdateInterface()
	layer = font.selectedLayers[0]
	roundLayer(layer, font)
	font.enableUpdateInterface()
