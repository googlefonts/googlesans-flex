# MenuTitle: Sharper Rounder

from GlyphsApp import Glyphs, Message, GSNode, GSPathSegment, QCURVE, LINE, OFFCURVE, distance, pointOnLine
from importlib import reload
import objc
import FlexRounder2
reload(FlexRounder2)
from FlexRounder2 import handleRoundingAt
from Cocoa import NSValue

try:
	GSGeometry = objc.lookUpClass("GSGeometry")
except:
	GSGeometry = objc.lookUpClass("GSGeometrie")

font = Glyphs.font
roundAxis = font.axisForTag_("ROND")
roundAxisIdx = font.axes.index(roundAxis)


def shiftOffcurve(path, nodeIdx, strokeWidth):

	node = path.nodes[nodeIdx]
	if node.type == LINE:
		points = []
		points.append(NSValue.valueWithPoint_(node.position))
		idx = nodeIdx + 1
		nextNode = path.nodes[idx]

		if nextNode.type != OFFCURVE:
			return

		nodeDistance = distance(node.position, nextNode.position)

		t = strokeWidth * 0.8 / nodeDistance
		t = t ** 0.5
		if t < 0.6:
			t = 0.6
		if abs(t - 1) > 0.1:
			newPos = pointOnLine(node.position, nextNode.position, t / 0.9)
			currNode = nextNode
			while currNode.type == OFFCURVE:
				points.append(NSValue.valueWithPoint_(currNode.position))
				idx += 1
				currNode = path.nodes[idx]
			points.append(NSValue.valueWithPoint_(currNode.position))
			segment = GSPathSegment.alloc().initWithQuadratic_(points)
			if len(segment) < 3:
				return

			segment.shortenFromTime_(t)
			nextNode.position = newPos
			idx = 2
			while (idx == 2 or currNode.type == OFFCURVE):
				currNode = path.nodes[nodeIdx + idx]
				pos = segment[idx]
				idx += 1
				currNode.position = pos
		midPoint, _ = GSGeometry.nearestPointUnlimited_onLineP1_p2_t_(nextNode.position, node.position, path.nodes[nodeIdx + 2].position, None)
		nextNode.position = pointOnLine(nextNode.position, midPoint, 0.2)

	elif node.type == QCURVE:
		points = []
		points.append(NSValue.valueWithPoint_(node.position))
		idx = nodeIdx - 1
		prevNode = path.nodes[idx]

		if prevNode.type != OFFCURVE:
			return

		nodeDistance = distance(node.position, prevNode.position)

		t = strokeWidth * 0.8 / nodeDistance
		t = t ** 0.5
		if t < 0.6:
			t = 0.6
		if abs(t - 1) < 0.1:
			newPos = pointOnLine(node.position, prevNode.position, t / 0.9)
			currNode = prevNode
			while currNode.type == OFFCURVE:
				points.append(NSValue.valueWithPoint_(currNode.position))
				idx -= 1
				currNode = path.nodes[idx]
			points.append(NSValue.valueWithPoint_(currNode.position))
			segment = GSPathSegment.alloc().initWithQuadratic_(points)
			if len(segment) < 3:
				return

			segment.shortenFromTime_(t)
			prevNode.position = newPos
			idx = 2
			while (idx <= 2 or currNode.type == OFFCURVE):
				currNode = path.nodes[nodeIdx - idx]
				pos = segment[idx]
				idx += 1
				currNode.position = pos
		midPoint, _ = GSGeometry.nearestPointUnlimited_onLineP1_p2_t_(prevNode.position, node.position, path.nodes[nodeIdx - 2].position, None)
		prevNode.position = pointOnLine(prevNode.position, midPoint, 0.2)


def addExtraNodes(path, nodeIdx, doRound):
	node1 = path.nodes[nodeIdx]
	node2 = path.nodes[nodeIdx + 1]

	if not (node1.type == LINE or node1.type == QCURVE):
		complainSelection()
		return False
	strokeWidth = distance(node1.position, node2.position)

	shiftOffcurve(path, nodeIdx, strokeWidth)
	shiftOffcurve(path, nodeIdx + 1, strokeWidth)

	nodeCount = len(path.nodes)
	nextNode = path.nodes[nodeIdx + 2]

	nodeIdx2 = nodeIdx + 2

	if nodeIdx2 > nodeCount:
		nodeIdx2 = nodeIdx2 % nodeCount

	if nextNode.type == LINE:
		newNode = GSNode(node2.position, QCURVE)
		path.nodes.insert(nodeIdx2, newNode)
	newNode = GSNode(node2.position, OFFCURVE)
	path.nodes.insert(nodeIdx2, newNode)
	newNode = GSNode(node2.position, OFFCURVE)
	path.nodes.insert(nodeIdx2, newNode)

	nodeIdx = path.nodes.index(node1)
	newNode = GSNode(node1.position, OFFCURVE)
	path.nodes.insert(nodeIdx, newNode)
	newNode = GSNode(node1.position, OFFCURVE)
	path.nodes.insert(nodeIdx, newNode)
	if node1.type == LINE:
		newNode = GSNode(node1.position, LINE)
		path.nodes.insert(nodeIdx, newNode)
		node1.type = QCURVE

	if doRound:
		handleRoundingAt(node1.index, node2.index, path)

	return True


def complainSelection():
	Message("Please select two nodes that are connected by a line segment")


def main():
	font = Glyphs.font
	font.disableUpdateInterface()
	layer = font.selectedLayers[0]
	if len(layer.selection) != 2:
		complainSelection()
		return
	node1 = layer.selection[0]
	node2 = layer.selection[1]
	indexPath1 = layer.indexPathOfNode_(node1)
	indexPath2 = layer.indexPathOfNode_(node2)
	pathIndex1 = indexPath1.indexAtPosition_(0)
	pathIndex2 = indexPath2.indexAtPosition_(0)
	nodeIndex1 = indexPath1.indexAtPosition_(1)
	nodeIndex2 = indexPath2.indexAtPosition_(1)
	if pathIndex1 != pathIndex2:
		complainSelection()
		return
	path = layer.shapes[pathIndex1]
	if (nodeIndex1 == 0 and nodeIndex2 == len(path.nodes) - 1):
		nodeIdx = nodeIndex2
	elif (nodeIndex2 == 0 and nodeIndex1 == len(path.nodes) - 1):
		nodeIdx = nodeIndex1
	elif nodeIndex1 + 1 == nodeIndex2:
		nodeIdx = nodeIndex1
	elif nodeIndex2 + 1 == nodeIndex1:
		nodeIdx = nodeIndex2
	else:
		complainSelection()
		return

	for currLayer in layer.parent.layers:
		if not currLayer.isMasterLayer:
			continue
		path = currLayer.shapes[pathIndex1]
		roundMaster = currLayer.master
		roundValue = roundMaster.internalAxesValues[roundAxis.axisId]
		if not addExtraNodes(path, nodeIdx, roundValue > 10):
			return

	font.enableUpdateInterface()


if __name__ == "__main__":

	main()
