# MenuTitle: Align With Sharp

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
