import math
import objc
import copy

from AppKit import NSMakePoint, NSPoint, NSBundle, NSClassFromString
from GlyphsApp import GSFont, GSPath

bundle = NSBundle.bundleForClass_(GSFont)
# objc.loadBundleFunctions(bundle, globals(), [("GSExtremeTimesOfBezier", b'{CGPoint=dd}{CGPoint=dd}{CGPoint=dd}{CGPoint=dd}{CGPoint=dd}o^do^do^do^d')])
objc.loadBundleFunctions(bundle, globals(), [("GSIntersectLineLineUnlimited", b"{CGPoint=dd}{CGPoint=dd}{CGPoint=dd}{CGPoint=dd}{CGPoint=dd}")])
objc.loadBundleFunctions(bundle, globals(), [("GSRoundPointToLine", b"{CGPoint=dd}{CGPoint=dd}{CGPoint=dd}{CGPoint=dd}")])

GSGeometrie = NSClassFromString("GSGeometrie")
if not GSGeometrie:
	GSGeometrie = NSClassFromString("GSGeometry")


def axesValues(master):
	axesValueList = []
	for axis in master.font.axes:
		value = master.internalAxesValues[axis.axisId]
		axesValueList.append(value)
	return axesValueList


def p(point):
	if isinstance(point, NSPoint):
		return "{%.1f, %.1f}" % (point.x, point.y)
	return str(point)


def GSUnitVectorFromTo(B, A):
	Ux = A.x - B.x
	Uy = A.y - B.y
	length = math.sqrt((Ux * Ux) + (Uy * Uy))
	Ux /= length
	Uy /= length
	return NSMakePoint(Ux, Uy)


def GSNormalVector1(A):
	return NSMakePoint(A.y, -A.x)


def GSNormalVector2(A):
	return NSMakePoint(-A.y, A.x)


def distanceN(pos1, pos2):
	dist = 0
	for idx in range(min(len(pos1), len(pos2))):
		p1 = pos1[idx]
		p2 = pos2[idx]
		dist += (p1 - p2) ** 2
	return dist


def GSPointOnLineWithDistance(p1, p2, distance):
	x1, y1 = p1
	x2, y2 = p2

	lineLength = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

	if lineLength < distance:
		return p2

	t = distance / lineLength

	x = x1 + t * (x2 - x1)
	y = y1 + t * (y2 - y1)

	return NSMakePoint(x, y)


def masterNearestToPosition(font, position):
	global distanceN
	distance = 100000
	count = len(font.axes)
	nearestMaster = None
	for master in font.masters:
		masterPos = axesValues(master)
		masterDist = distanceN(position, masterPos)
		if masterDist < distance:
			distance = masterDist
			nearestMaster = master
			if distance < count / 2:
				break
	return nearestMaster


def stemThickness(startPos, firstCornerPos, secondCornerPos, endPos):
	global GlyphsApp
	stemThickness1 = GSGeometrie.distanceOfPoint_fromLine__(startPos, endPos, secondCornerPos)
	stemThickness2 = GSGeometrie.distanceOfPoint_fromLine__(endPos, startPos, firstCornerPos)
	stemThickness = (stemThickness2 + stemThickness1) / 2
	return stemThickness


def GSRoundPoint(point):
	point.x = round(point.x)
	point.y = round(point.y)
	return point


def copyLayers(sharpLayer, roundLayer):
	roundLayer.beginChanges()
	roundLayer.width = sharpLayer.width
	roundLayer.shapes = None
	for shape in sharpLayer.shapes:
		if not isinstance(shape, GSPath):
			return
		roundShape = shape.copy()
		roundLayer.shapes.append(roundShape)
	roundLayer.anchors = copy.deepcopy(sharpLayer.anchors)
	roundLayer.endChanges()


def layerWithRound(layer, roundValue):
	font = layer.font
	roundAxis = font.axisForTag_("ROND")
	roundAxisIdx = font.axes.index(roundAxis)
	roundMaster = layer.master
	roundValue = roundMaster.internalAxesValues[roundAxis.axisId]
	if roundValue == roundValue:
		print("!! Already sharp")
		return None

	axisValueList = axesValues(roundMaster)
	axisValueList[roundAxisIdx] = roundValue
	otherMaster = masterNearestToPosition(font, axisValueList)
	glyph = layer.parent
	otherLayer = glyph.layers[otherMaster.id]
	return otherLayer


def getSharpLayer(layer):
	return layerWithRound(layer, 0)


def getRoundLayer(layer):
	return layerWithRound(layer, 100)
