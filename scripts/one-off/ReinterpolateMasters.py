#MenuTitle: ReinterpolateMasters

from GlyphsApp import GSInstance
shiftFromWght = 400
shiftFromOpsz = 18
shiftTo = 360

Font.disableUpdateInterface()
layers = Glyphs.font.currentTab.selectedLayers
masters2Shift = []
instance2Shift = []
weightIdx = -1
wghtAxis = Font.axisForTag_("wght")
opszAxis = Font.axisForTag_("opsz")

def instanceAsMaster(instance):
	font = instance.font
	instanceFont, _ = font.generateInstance_error_(instance, None)
	assert instanceFont is not None

	instanceMaster = instanceFont.masters[0]
	insertedMaster = font.addFontAsNewMaster_(instanceMaster)
	insertedMaster.internalAxesValues = instance.internalAxesValues
	return insertedMaster

for master in Font.masters:
	if master.internalAxesValues[wghtAxis.axisId] == shiftFromWght and master.internalAxesValues[opszAxis.axisId] == 144:
		masters2Shift.append(master)
		instance = GSInstance()
		instance.name = master.name
		instance.font = Font
		instance.internalAxesValues = master.internalAxesValues
		instance.internalAxesValues[wghtAxis.axisId] = shiftTo
		instance.internalAxesValues[opszAxis.axisId] = shiftFromOpsz
		instance.instanceInterpolations  # trigger update
		instance.manualInterpolation = True
		instance2Shift.append(instance)

newMasters = []
for instance in instance2Shift:
	newMaster = instanceAsMaster(instance)
	newMaster.name += "_new"
	newMasters.append(newMaster)
	newMaster.internalAxesValues[wghtAxis.axisId] = shiftFromWght
	newMaster.internalAxesValues[opszAxis.axisId] = 144

for idx, newMaster in enumerate(newMasters):
	oldMasters = masters2Shift[idx]
	oldMasterIdx = Font.masters.index(oldMasters)
	print(oldMasterIdx)
	Font.fontMasters().removeObject_(newMaster)
	Font.fontMasters().insertObject_atIndex_(newMaster, oldMasterIdx)
	Font.removeFontMaster_(oldMasters)

	for glyph in Font.glyphs:
		layer = glyph.layers[newMaster.id]
		layer.roundCoordinatesToGridFast_(1)
		layer.width = round(layer.width)

Font.enableUpdateInterface()