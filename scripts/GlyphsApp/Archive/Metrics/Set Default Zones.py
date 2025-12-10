#MenuTitle: Set Default Zones

from GlyphsApp import GSMetricsTypeAscender, GSMetricsTypeCapHeight, GSMetricsTypexHeight, GSMetricsTypeDescender, GSMetricsTypeBaseline, distance
from Foundation import NSMaxY, NSMinY
from GeorgsFlex.Cleanup.ComputePositionsOfSmallNumbers import measure


def zoneForMaster(master):
	font = master.font
	metricAscender = master.valueForMetric_(font.objectInMetricsWithType_withName_(GSMetricsTypeAscender, None))
	metricCapHeight = master.valueForMetric_(font.objectInMetricsWithType_withName_(GSMetricsTypeCapHeight, None))
	metricxHeight = master.valueForMetric_(font.objectInMetricsWithType_withName_(GSMetricsTypexHeight, None))
	metricBaseline = master.valueForMetric_(font.objectInMetricsWithType_withName_(GSMetricsTypeBaseline, None))
	metricDescender = master.valueForMetric_(font.objectInMetricsWithType_withName_(GSMetricsTypeDescender, None))
	
	glyphCapHeight = font.glyphs["C"]
	glyphxHeight = font.glyphs["C"]
	glyphAscender = font.glyphs["f"]
	layerCapHeight = glyphCapHeight.layers[master.id]
	layerxHeight = glyphxHeight.layers[master.id]
	layerAscender = glyphAscender.layers[master.id]
	
	topOvershootUppercase = NSMaxY(layerCapHeight.bounds) - metricCapHeight.position
	bottomOvershootUppercase = 0 - NSMinY(layerCapHeight.bounds)
	if metricCapHeight.overshoot == 0:
		metricCapHeight.overshoot = max(topOvershootUppercase, bottomOvershootUppercase) + 1
	if metricBaseline.overshoot < metricCapHeight.overshoot:
		metricBaseline.overshoot = -metricCapHeight.overshoot
	
	topOvershootLowercase = NSMaxY(layerxHeight.bounds) - metricxHeight.position
	bottomOvershootLowercase = 0 - NSMinY(layerxHeight.bounds)
	if metricxHeight.overshoot == 0:
		metricxHeight.overshoot = max(topOvershootLowercase, bottomOvershootLowercase) + 1
	if metricDescender.overshoot == 0:
		metricDescender.overshoot = -metricxHeight.overshoot
	
	topOvershootAscender = NSMaxY(layerAscender.bounds) - metricAscender.position
	if metricAscender.overshoot == 0:
		metricAscender.overshoot = topOvershootAscender + 1


def setDnomMetrics(master):
	flatHeight = measure(master, ".denominator")
	roundHeight0 = measure(master, ".denominator", name="zero")
	roundHeight2 = measure(master, ".denominator", name="two")
	roundHeight3 = measure(master, ".denominator", name="three")
	roundHeight8 = measure(master, ".denominator", name="eight")
	roundHeight9 = measure(master, ".denominator", name="nine")

	roundHeight = roundHeight0
	roundHeight = max(roundHeight, roundHeight0)
	roundHeight = max(roundHeight, roundHeight2)
	roundHeight = max(roundHeight, roundHeight3)
	roundHeight = max(roundHeight, roundHeight8)
	roundHeight = max(roundHeight, roundHeight9)
	topMetric = master.metrics()[-2]
	baselineMetric = master.metrics()[-1]
	if topMetric.metric.type != 0 and baselineMetric.metric.type == 0:
		topMetric = baselineMetric
		baselineMetric = None
	elif topMetric.metric.type != 0 or baselineMetric.metric.type != 8:
		print("_bail")
		return
	topMetric.position = flatHeight
	topMetric.overshoot = roundHeight - flatHeight
	if baselineMetric is not None:
		baselineMetric.position = 0
		baselineMetric.overshoot = flatHeight - roundHeight


stemH = Font.stems[1]
stemV = Font.stems[0]

def stemsForMaster(master):
	font = master.font
	layerT = font.glyphs["T"].layers[master.id]
	layerL = font.glyphs["I"].layers[master.id]
	intersections = layerL.calculateIntersectionsStartPoint_endPoint_(NSMakePoint(-100, 400), NSMakePoint(10000, 400))
	print("__intersections", intersections, master)
	p1 = intersections[1].pointValue()
	p2 = intersections[2].pointValue()

	bounds = layerT.shapes[1].bounds
	print("__stem", round(distance(p1, p2)), bounds.size.height)
	
	master.stems[stemH.id] = bounds.size.height
	master.stems[stemV.id] = round(distance(p1, p2))

Font.disableUpdateInterface()
for master in Font.masters:
	#zoneForMaster(master)
	#stemsForMaster(master)
	setDnomMetrics(master)


Font.enableUpdateInterface()
