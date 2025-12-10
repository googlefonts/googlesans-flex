# MenuTitle: Sharper
import math

# from importlib import reload
# import flexLib
# reload(flexLib)

from GlyphsApp import Font, Layer, subtractPoints, GSPathSegment, distance, OFFCURVE

from flexLib import axesValues, GSUnitVectorFromTo, stemThickness, GSGeometrie
from AppKit import NSClassFromString, NSMakePoint

RoundedFont = NSClassFromString("RoundedFont")


def getRound():
	pass


def contactPoints(leftSegment, rightSegment, stem):
	result = RoundedFont.contactPointsLeft_right_M_K1_K2_t1_t2_stem_(
		leftSegment, rightSegment, None, None, None, None, None, stem
	)
	if result[0] is False:
		return False
	top = result[1]
	p1 = leftSegment[0]
	p2 = rightSegment[0]
	angle = GSGeometrie.angleOfVector_(subtractPoints(p1, p2))
	top.x -= math.cos(math.radians(-angle + 90)) * stem * 0.5
	top.y += math.sin(math.radians(-angle + 90)) * stem * 0.5
	return result[2], top, result[3]


def getSharpPos(startPos, firstCornerPos, midPos, secondCornerPos, endPos):
	angle1 = GSGeometrie.angleBetweenVector_andVector_(subtractPoints(startPos, firstCornerPos), subtractPoints(firstCornerPos, midPos))
	angle2 = GSGeometrie.angleBetweenVector_andVector_(subtractPoints(midPos, secondCornerPos), subtractPoints(secondCornerPos, endPos))

	stem = stemThickness(startPos, firstCornerPos, secondCornerPos, endPos)
	seg2_3 = distance(firstCornerPos, secondCornerPos)
	seg1 = stem / 2
	seg2 = seg2_3 / 2
	seg3 = seg2
	seg4 = stem / 2
	angle1_ = (90.0 / angle1) ** 0.8
	angle2_ = (90.0 / angle2) ** 0.8

	seg1 *= angle2_
	seg2 *= angle2_
	seg3 *= angle1_
	seg4 *= angle1_
	seg2 *= seg2_3 / (seg2 + seg3)
	seg3 *= seg2_3 / (seg2 + seg3)

	u1 = GSUnitVectorFromTo(firstCornerPos, startPos)
	u2 = GSUnitVectorFromTo(firstCornerPos, midPos)
	# u3 = GSUnitVectorFromTo(secondCornerPos, midPos)
	u4 = GSUnitVectorFromTo(secondCornerPos, endPos)

	new_startPos = NSMakePoint(firstCornerPos.x + u1.x * seg1, firstCornerPos.y + u1.y * seg1)
	new_midPos_1 = NSMakePoint(firstCornerPos.x + u2.x * seg2, firstCornerPos.y + u2.y * seg2)
	# new_midPos_2 = NSMakePoint(secondCornerPos.x + u3.x * seg3, secondCornerPos.y + u3.y * seg3)
	new_endPos = NSMakePoint(secondCornerPos.x + u4.x * seg4, secondCornerPos.y + u4.y * seg4)
	return new_startPos, new_midPos_1, new_endPos


def sharpen(firstPrevOn, firstNextOn, secondNextOn, startPos, firstCornerPos, secondCornerPos, endPos, startIdx, endIdx, path):
	angle1 = GSGeometrie.angleOfVector_(subtractPoints(startPos, firstCornerPos))
	angle2 = GSGeometrie.angleOfVector_(subtractPoints(secondCornerPos, endPos))
	stem = stemThickness(startPos, firstCornerPos, secondCornerPos, endPos)

	shiftedFirstCornerPos = NSMakePoint(firstCornerPos.x, firstCornerPos.y)
	shiftedSecondCornerPos = NSMakePoint(secondCornerPos.x, secondCornerPos.y)
	# if False:
	if True:
		shiftedFirstCornerPos.x -= math.cos(math.radians(-angle1)) * stem * 0.05
		shiftedFirstCornerPos.y += math.sin(math.radians(-angle1)) * stem * 0.05
		shiftedSecondCornerPos.x += math.cos(math.radians(-angle2)) * stem * 0.05
		shiftedSecondCornerPos.y -= math.sin(math.radians(-angle2)) * stem * 0.05

	if firstPrevOn.type != OFFCURVE:
		firstOverPrevOn = path.nodes[startIdx - 3]
		inSegment = GSPathSegment.alloc().initWithLinePoint1_point2_options_(shiftedFirstCornerPos, firstOverPrevOn.position, 0)
	else:
		return
		pass  # make curve segment

	if secondNextOn != OFFCURVE:
		secondOverNextOn = path.nodes[endIdx + 2]
		outSegment = GSPathSegment.alloc().initWithLinePoint1_point2_options_(shiftedSecondCornerPos, secondOverNextOn.position, 0)
	else:
		return

	result = contactPoints(inSegment, outSegment, stem)
	if result is False:
		return
	new_startPos, new_midPos, new_endPos = result

	new_midPos_, _ = GSGeometrie.nearestPointUnlimited_onLineP1_p2_t_(new_midPos, firstCornerPos, secondCornerPos, None)
	if firstPrevOn.type != OFFCURVE:
		firstPrevOn.position = new_startPos
	if firstNextOn.type != OFFCURVE:
		firstNextOn.position = new_midPos_
	if secondNextOn.type != OFFCURVE:
		secondNextOn.position = new_endPos


def handleRoundingAt(startIdx, endIdx, path):
	firstNode = path.nodes[startIdx]
	firstCornerPos = firstNode.position
	firstPrevOn = path.nodes[startIdx - 2]
	firstNextOn = path.nodes[startIdx + 1]

	startPos = firstPrevOn.position
	if firstPrevOn.type == OFFCURVE:
		startPos = NSMakePoint((startPos.x + firstCornerPos.x) / 2.0, (startPos.y + firstCornerPos.y) / 2.0)
	midPos1 = firstNextOn.position
	if firstNextOn.type == OFFCURVE:
		midPos1 = NSMakePoint((midPos1.x + firstCornerPos.x) / 2.0, (midPos1.y + firstCornerPos.y) / 2.0)
	secondCorner = path.nodes[endIdx]
	secondCornerPos = secondCorner.position
	secondPrevOn = path.nodes[endIdx - 2]
	secondNextOn = path.nodes[endIdx + 1]
	midPos2 = secondPrevOn.position
	if secondPrevOn.type == OFFCURVE:
		midPos2 = NSMakePoint((midPos2.x + secondCornerPos.x) / 2.0, (midPos2.y + secondCornerPos.y) / 2.0)
	endPos = secondNextOn.position
	if secondNextOn.type == OFFCURVE:
		endPos = NSMakePoint((endPos.x + secondCornerPos.x) / 2.0, (endPos.y + secondCornerPos.y) / 2.0)

	sharpen(firstPrevOn, firstNextOn, secondNextOn, startPos, firstCornerPos, secondCornerPos, endPos, startIdx, endIdx, path)


def getStem(path):
	master = path.parent.master
	font = master.font
	for stem in font.stems:
		if not stem.horizontal:
			return master.stems[stem.id]
	raise "No Stem"


def simpleRoundingAt(idx, path):
	stem = getStem(path)
	cornerNode = path.nodes[idx]
	cornerPos = cornerNode.position
	prevOn = path.nodes[idx - 2]
	startPos = prevOn.position
	nextOn = path.nodes[idx + 1]
	endPos = nextOn.position

	angle1 = GSGeometrie.angleOfVector_(subtractPoints(startPos, cornerPos))
	angle2 = GSGeometrie.angleOfVector_(subtractPoints(cornerPos, endPos))

	shiftedFirstCornerPos = NSMakePoint(cornerPos.x, cornerPos.y)
	shiftedSecondCornerPos = NSMakePoint(cornerPos.x, cornerPos.y)

	shiftedFirstCornerPos.x += math.cos(math.radians(-angle1)) * stem * 0.55
	shiftedFirstCornerPos.y -= math.sin(math.radians(-angle1)) * stem * 0.55
	shiftedSecondCornerPos.x -= math.cos(math.radians(-angle2)) * stem * 0.55
	shiftedSecondCornerPos.y += math.sin(math.radians(-angle2)) * stem * 0.55

	prevOn.position = shiftedFirstCornerPos
	nextOn.position = shiftedSecondCornerPos


def checkPath(path):
	prevNode = path.nodes[-1]

	previousCornerIdx = -100
	processedNodes = []
	nodeCount = len(path)
	for idx in range(nodeCount + 2):
		node = path.nodes[idx]
		if (
			node.type == OFFCURVE
			and prevNode.type == OFFCURVE
			and distance(node.position, prevNode.position) < 0.1
		):
			# secondCornerPos = node.position
			if idx - previousCornerIdx < 4:
				handleRoundingAt(previousCornerIdx, idx, path)
				processedNodes.append(idx % nodeCount)
				processedNodes.append(previousCornerIdx % nodeCount)
			previousCornerIdx = idx
		prevNode = node
	for idx in range(len(path) + 2):
		node = path.nodes[idx]
		if (
			node.type == OFFCURVE
			and prevNode.type == OFFCURVE
			and distance(node.position, prevNode.position) < 0.1
			and idx % nodeCount not in processedNodes
			and previousCornerIdx % nodeCount not in processedNodes
		):
			simpleRoundingAt(idx, path)
		previousCornerIdx = idx
		prevNode = node


def allMasters():
	roundAxis = Font.axisForTag_("ROND")
	wdthAxis = Font.axisForTag_("wdth")
	roundAxisIdx = Font.axes.index(roundAxis)
	wdthAxisIdx = Font.axes.index(wdthAxis)
	for currLayer in Layer.parent.layers:
		m = currLayer.master
		axisValueList = axesValues(m)
		if axisValueList[roundAxisIdx] > 0 or axisValueList[wdthAxisIdx] < 2:
			continue
		# print(l)
		for shape in currLayer.shapes:
			checkPath(shape)


# checkPath(Layer.shapes[0])
for shape in Layer.shapes:
	checkPath(shape)
