# MenuTitle: Rounder

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

import math
from GlyphsApp import Glyphs, GSPath, OFFCURVE, distance, subtractPoints, addPoints, scalePoint
from importlib import reload
import flexLib
reload(flexLib)
from flexLib import axesValues, stemThickness, masterNearestToPosition, GSUnitVectorFromTo, GSNormalVector1, p, GSIntersectLineLineUnlimited, GSRoundPoint, GSRoundPointToLine, GSGeometrie, copyLayers
from AppKit import NSZeroPoint, NSMakePoint


def divideLine(P0, P1, t):
	return NSMakePoint(P0.x + ((P1.x - P0.x) * t), P0.y + ((P1.y - P0.y) * t))


def roundPath(path):
	prevNode = path.nodes[-1]
	idx = 0
	previousCornerIdx = -100
	# find all double roundings
	for idx in range(len(path) + 2):
		node = path.nodes[idx]
		if (
			node.type == OFFCURVE
			and prevNode.type == OFFCURVE
			and distance(node.position, prevNode.position) < 0.1
		):
			# secondCornerPos = node.position
			if idx - previousCornerIdx < 4:
				handleRoundingAt(previousCornerIdx, idx, path)
			previousCornerIdx = idx
		idx += 1
		prevNode = node

	# find single round corners
	idx = 0
	for node in path.nodes:
		if (
			node.type == OFFCURVE
			and prevNode.type == OFFCURVE
			and distance(node.position, prevNode.position) < 0.1
		):
			cornerPos = node.position
			startPos = path.nodes[idx - 2].position
			endPos = path.nodes[idx + 1].position
			roundCorner(startPos, cornerPos, endPos, prevNode, node)
		idx += 1
		prevNode = node


def roundCorner(startPos, cornerPos, endPos, node1, node2, factor1=1, factor2=1):
	print("__roundCorner cornerPos", p(startPos), p(cornerPos), p(endPos))
	assert distance(node1.position, node2.position) < 1
	assert node1.type == OFFCURVE
	assert node2.type == OFFCURVE
	fitFactor = 0.41
	fitAngle = GSGeometrie.angleBetweenVector_andVector_(
		subtractPoints(startPos, cornerPos),
		subtractPoints(cornerPos, endPos)
	)

	if fitAngle < 0:
		fitAngle += 180
	if fitAngle < 89:
		fitFactor *= math.sin(math.radians(fitAngle))  # ** 1.1
	if fitAngle > 91:
		fitFactor /= math.sin(math.radians(fitAngle)) ** 0.6

	node1.position = GSRoundPointToLine(divideLine(startPos, cornerPos, fitFactor * factor1), startPos, cornerPos)
	node2.position = GSRoundPointToLine(divideLine(endPos, cornerPos, fitFactor * factor2), endPos, cornerPos)


def addOvershoot(startPos, firstCornerPos, secondCornerPos, endPos, startIdx, endIdx, path):
	# print("__addOv", p(startPos), p(firstCornerPos), p(secondCornerPos), p(endPos), startIdx, endIdx, path.nodes)
	stem = stemThickness(startPos, firstCornerPos, secondCornerPos, endPos)

	shiftDirection1 = GSUnitVectorFromTo(startPos, firstCornerPos)
	shiftDirection2 = GSUnitVectorFromTo(endPos, secondCornerPos)
	shiftDirection = GSUnitVectorFromTo(NSMakePoint(0, 0), addPoints(shiftDirection1, shiftDirection2))

	cutDirection = GSUnitVectorFromTo(firstCornerPos, secondCornerPos)
	normalCutDirection = GSNormalVector1(cutDirection)

	correctedShiftDirection = GSIntersectLineLineUnlimited(normalCutDirection, addPoints(cutDirection, normalCutDirection), NSZeroPoint, shiftDirection)

	if correctedShiftDirection.x < 10:
		# the correction is a bit too much, so we scale it back a bit
		scaleBack = scalePoint(subtractPoints(normalCutDirection, correctedShiftDirection), 0.3)
		shiftDirection = addPoints(correctedShiftDirection, scaleBack)

	shift = scalePoint(shiftDirection, stem * 0.055)

	for jdx in range(startIdx, endIdx):
		shiftNode = path.nodes[jdx]
		shiftNode.position = GSRoundPoint(addPoints(shiftNode.position, shift))


def handleRoundingAt(startIdx, endIdx, path):
	firstNode = path.nodes[startIdx]
	firstCornerPos = firstNode.position
	firstPrevOn = path.nodes[startIdx - 2]
	firstNextOn = path.nodes[startIdx + 1]

	startPos = firstPrevOn.position
	if firstPrevOn.type == OFFCURVE:
		startPos = NSMakePoint((startPos.x + firstCornerPos.x) / 2.0, (startPos.y + firstCornerPos.y) / 2.0)
	midPos = firstNextOn.position
	if firstNextOn.type == OFFCURVE:
		midPos = NSMakePoint((midPos.x + firstCornerPos.x) / 2.0, (midPos.y + firstCornerPos.y) / 2.0)
	secondCorner = path.nodes[endIdx]
	secondCornerPos = secondCorner.position
	secondNextOn = path.nodes[endIdx + 1]
	endPos = secondNextOn.position
	if secondNextOn.type == OFFCURVE:
		endPos = NSMakePoint((endPos.x + secondCornerPos.x) / 2.0, (endPos.y + secondCornerPos.y) / 2.0)

	roundCorner(startPos, firstCornerPos, midPos, path.nodes[startIdx - 1], firstNode, 1.125)
	roundCorner(midPos, secondCornerPos, endPos, path.nodes[endIdx - 1], secondCorner, 1, 1.125)

	addOvershoot(startPos, firstCornerPos, secondCornerPos, endPos, startIdx, endIdx, path)


def doRoundLayer(roundLayer):
	for shape in roundLayer.shapes:
		if not isinstance(shape, GSPath):
			return
		roundPath(shape)


def roundMasters(glyph, sharpMaster, roundMaster):
	sharpLayer = glyph.layers[sharpMaster.id]
	roundLayer = glyph.layers[roundMaster.id]
	copyLayers(sharpLayer, roundLayer)
	doRoundLayer(roundLayer)


def roundGlyphs(glyphs, font):
	font.disableUpdateInterface()
	roundAxis = font.axisForTag_("ROND")
	roundAxisIdx = font.axes.index(roundAxis)
	# roundSharpPairs = []
	for sharpMaster in font.masters:
		roundValue = sharpMaster.internalAxesValues[roundAxis.axisId]
		if roundValue > 10:
			continue
		axisValueList = axesValues(sharpMaster)
		axisValueList[roundAxisIdx] = 100
		roundMaster = masterNearestToPosition(font, axisValueList)
		roundValue = roundMaster.internalAxesValues[roundAxis.axisId]
		if roundValue < 10:
			continue
		print("__sharpMaster", sharpMaster)
		print("__roundMaster", roundMaster)
		print("__")
		for glyph in glyphs:
			roundMasters(glyph, sharpMaster, roundMaster)
	font.enableUpdateInterface()


if __name__ == "__main__":
	font = Glyphs.font
	selectedLayers = font.selectedLayers
	layer = selectedLayers[0]
	roundGlyphs([layer.parent], font)
