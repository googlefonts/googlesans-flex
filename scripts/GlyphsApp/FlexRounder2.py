# MenuTitle: Rounder 2

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
from GlyphsApp import Glyphs, GSPath, OFFCURVE, LINE, QCURVE, distance, subtractPoints, addPoints, scalePoint
from importlib import reload
import flexLib
reload(flexLib)
from flexLib import axesValues, stemThickness, masterNearestToPosition, GSUnitVectorFromTo, GSNormalVector1, p, GSIntersectLineLineUnlimited, GSRoundPoint, GSRoundPointToLine, GSGeometrie, copyLayers, GSPointOnLineWithDistance
from Cocoa import NSZeroPoint, NSMakePoint


def divideLine(P0, P1, t):
	return NSMakePoint(P0.x + ((P1.x - P0.x) * t), P0.y + ((P1.y - P0.y) * t))


def roundPath(path):
	prevNode = path.nodes[-1]
	idx = 0

	# find all double roundings
	for idx in range(len(path) + 2):
		node = path.nodes[idx]
		nextNode = path.nodes[idx + 1]
		overPrevNode = path.nodes[idx - 2]
		if (
			node.type == LINE
			and prevNode.type == QCURVE
			and distance(node.position, nextNode.position) < 0.1
			and distance(prevNode.position, overPrevNode.position) < 0.1
		):
			# secondCornerPos = node.position
			handleRoundingAt(idx - 1, idx, path)
		idx += 1
		prevNode = node

	# find single round corners
	idx = 0
	for node in path.nodes:
		if (
			node.type != OFFCURVE
			and prevNode.type == OFFCURVE
			and distance(node.position, prevNode.position) < 0.1
		):
			cornerPos = node.position
			startPos = path.nodes[idx - 3].position
			endPos = path.nodes[idx + 1].position
			# TODO
			roundCorner(startPos, cornerPos, endPos, prevNode, node)
		idx += 1
		prevNode = node


def roundCorner(startPos, cornerPos, endPos, node1, node2, node3, node4, factor1=1, factor2=1):
	assert distance(node1.position, node2.position) < 1
	assert node1.type == OFFCURVE
	assert node2.type == OFFCURVE
	assert node3.type != OFFCURVE
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
	if factor1 > factor2:
		node3.position = GSRoundPoint(endPos)
		if node4.type != OFFCURVE:
			node4.position = GSRoundPoint(startPos)
	else:
		node3.position = GSRoundPoint(startPos)
		if node4.type != OFFCURVE:
			node4.position = GSRoundPoint(endPos)


def addOvershoot(startPos, firstCornerPos, secondCornerPos, endPos, startIdx, endIdx, path):
	if endIdx < startIdx:
		startIdx -= len(path.nodes)
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
	firstCorner = path.nodes[startIdx]
	secondCorner = path.nodes[endIdx]
	stemWidth = distance(firstCorner.position, secondCorner.position)

	firstCornerPos = firstCorner.position
	firstPrevOn = path.nodes[startIdx - 3]
	firstNextOn = path.nodes[startIdx + 1]

	startPos = firstPrevOn.position
	if firstPrevOn.type == OFFCURVE:
		startPos = GSPointOnLineWithDistance(firstCornerPos, startPos, stemWidth * 0.5)
	else:
		startPos = GSPointOnLineWithDistance(firstCornerPos, path.nodes[startIdx - 4].position, stemWidth * 0.45)
	midPos = firstNextOn.position
	if firstNextOn.type == LINE:
		midPos = NSMakePoint((midPos.x + firstCornerPos.x) / 2.0, (midPos.y + firstCornerPos.y) / 2.0)

	secondCornerPos = secondCorner.position
	secondNextOn = path.nodes[endIdx + 3]
	endPos = secondNextOn.position
	if secondNextOn.type == OFFCURVE:
		endPos = GSPointOnLineWithDistance(secondCornerPos, endPos, stemWidth * 0.5)
	else:
		endPos = GSPointOnLineWithDistance(secondCornerPos, path.nodes[endIdx + 4].position, stemWidth * 0.45)

	roundCorner(startPos, firstCornerPos, midPos, path.nodes[startIdx - 2], path.nodes[startIdx - 1], firstCorner, firstPrevOn, factor1=1.125, factor2=1)
	roundCorner(midPos, secondCornerPos, endPos, path.nodes[endIdx + 1], path.nodes[endIdx + 2], secondCorner, secondNextOn, factor1=1, factor2=1.125)

	addOvershoot(startPos, firstCornerPos, secondCornerPos, endPos, startIdx - 1, endIdx + 2, path)


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
		for glyph in glyphs:
			roundMasters(glyph, sharpMaster, roundMaster)
	font.enableUpdateInterface()


if __name__ == "__main__":
	font = Glyphs.font
	selectedLayers = font.selectedLayers
	layer = selectedLayers[0]
	roundGlyphs([layer.parent], font)
