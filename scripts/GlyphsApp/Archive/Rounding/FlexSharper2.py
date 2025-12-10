# MenuTitle: Sharper 2

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

# from importlib import reload
# import flexLib
# reload(flexLib)

import time
from GlyphsApp import Glyphs, GSPath, GSNode, distance, OFFCURVE, QCURVE
from flexLib import axesValues
from Cocoa import NSMakePoint


def pointOnLine(P0, P1, t):
	return NSMakePoint(P0.x + ((P1.x - P0.x) * t), P0.y + ((P1.y - P0.y) * t))


def handleRoundCorners(path, startIdx):
	nodeIdx = startIdx
	middleIdx = -1
	nodeIdx += 1
	secondOffNode = path.nodes[nodeIdx]
	nodeIdx += 1
	middleNode = path.nodes[nodeIdx]
	nodeIdx += 1
	middleIdx = nodeIdx
	if middleNode.type == OFFCURVE:
		thirdOffNode = middleNode
		middleIdx -= 1
		middleNode = None
	else:
		thirdOffNode = path.nodes[nodeIdx]
		nodeIdx += 1
	nodeIdx += 1

	firstCornerPos = secondOffNode.position
	secondCornerPos = thirdOffNode.position
	middlePos = None
	if middleNode:
		middlePos = middleNode.position
	else:
		middlePos = pointOnLine(firstCornerPos, secondCornerPos, 0.5)
		path.nodes.insert(middleIdx % len(path.nodes), GSNode(middlePos, QCURVE))
		middleIdx += 1
		if middleIdx >= len(path.nodes):
			middleIdx += 1

	path.nodes.insert(middleIdx % len(path.nodes), GSNode(middlePos))


def handleSharpCorners(path, startIdx):
	nodeIdx = startIdx
	middleIdx = -1
	firstOnNode = path.nodes[nodeIdx - 1]
	nodeIdx += 1
	secondOffNode = path.nodes[nodeIdx]
	nodeIdx += 1
	middleNode = path.nodes[nodeIdx]
	nodeIdx += 1
	middleIdx = nodeIdx
	if middleNode.type == OFFCURVE:
		thirdOffNode = middleNode
		middleIdx -= 1
		middleNode = None
	else:
		thirdOffNode = path.nodes[nodeIdx]
		nodeIdx += 1
	nodeIdx += 1
	secondOnNode = path.nodes[nodeIdx]

	firstCornerPos = secondOffNode.position
	secondCornerPos = thirdOffNode.position
	firstOnNode.position = firstCornerPos
	if middleNode:
		middleNode.position = firstCornerPos
	else:
		path.nodes.insert(middleIdx % len(path.nodes), GSNode(firstCornerPos, QCURVE))
		middleIdx += 1
		if middleIdx >= len(path.nodes):
			middleIdx += 1
	path.nodes.insert(middleIdx % len(path.nodes), GSNode(secondCornerPos))
	secondOnNode.position = secondCornerPos


font = Glyphs.font
roundAxis = font.axisForTag_("ROND")
roundAxisIdx = font.axes.index(roundAxis)


def adjustCornerInGlyph(glyph, pathIdx, nodeIdx):
	for layer in glyph.layers:
		m = layer.master
		axisValueList = axesValues(m)
		isRound = axisValueList[roundAxisIdx] > 0
		path = layer.shapes[pathIdx]
		if isRound:
			handleRoundCorners(path, nodeIdx)
			pass
		else:
			handleSharpCorners(path, nodeIdx)


def adjustSimpleCornerInGlyph(glyph, pathIdx, nodeIdx):
	for layer in glyph.layers:
		m = layer.master
		axisValueList = axesValues(m)
		isRound = axisValueList[roundAxisIdx] > 0
		path = layer.shapes[pathIdx]
		if not isRound:
			node = path.nodes[nodeIdx]
			nextNode = path.nodes[nodeIdx + 1]
			overPrevNode = path.nodes[nodeIdx - 2]
			nextNode.position = node.position
			overPrevNode.position = node.position


def findCornerInPath(path, pathIdx):
	if not isinstance(path, GSPath):
		return
	prevNode = path.nodes[-1]
	processedNodes = []
	nodeCount = len(path.nodes)
	nodeIdx = nodeCount + 1
	previousCornerIdx = 1000
	while nodeIdx > -2:
		node = path.nodes[nodeIdx]
		if (
			node.type == OFFCURVE
			and prevNode.type == OFFCURVE
			and distance(node.position, prevNode.position) < 0.1
		):
			if previousCornerIdx - nodeIdx < 4 and previousCornerIdx - nodeIdx > 1:
				adjustCornerInGlyph(path.parent.parent, pathIdx, nodeIdx)
				processedNodes.append(node)
				processedNodes.append(prevNode)
				processedNodes.append(path.nodes[previousCornerIdx])
				previousCornerIdx = 1000
				nodeIdx -= 2
				node = path.nodes[nodeIdx]
			else:
				previousCornerIdx = nodeIdx
		nodeIdx -= 1
		prevNode = node

	for nodeIdx in range(len(path) + 2):
		node = path.nodes[nodeIdx]
		overPrevNode = path.nodes[nodeIdx - 2]
		nextNode = path.nodes[nodeIdx + 1]
		if (
			node.type == OFFCURVE
			and prevNode.type == OFFCURVE
			and distance(node.position, prevNode.position) < 0.1
			and distance(node.position, nextNode.position) > 0.1
			and distance(node.position, overPrevNode.position) > 0.1
		):
			adjustSimpleCornerInGlyph(path.parent.parent, pathIdx, nodeIdx)
		prevNode = node


def findCornerInGlyph(glyph):
	try:
		glyph.beginUndo()
		layer = glyph.layers[0]
		pathIdx = 0
		start = time.time()
		layer.stopUpdates()
		for path in layer.shapes:
			findCornerInPath(path, pathIdx)
			pathIdx += 1
	except:
		import traceback
		print(traceback.format_exc())
	finally:
		layer.startUpdates()
		glyph.endUndo()
		print("__time", time.time() - start)


selectedLayer = font.selectedLayers[0]
findCornerInGlyph(selectedLayer.parent)
