# MenuTitle: Filter Kerning Regressions

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

from pprint import pprint
from GlyphsApp import Glyphs, LTR
from newGlyphs import newGlyphs

def oldKeyNewKey(keyNew, fontOld, fontNew):
	plainKey = keyNew
	if keyNew[0] != '@':
		glyphNew = fontNew.glyphForId_(keyNew)
		assert glyphNew
		plainKey = glyphNew.name
		glyphOld = fontOld.glyphs[glyphNew.name]
		if glyphOld:
			keyOld = glyphOld.id
		else:
			keyOld = None
	else:
		keyOld = keyNew
		# plainKey = plainKey.replace("MMK_L_", "")
		# plainKey = plainKey.replace("MMK_R_", "")
	return keyOld, plainKey

def removeNewKerningPairs(fontOld, fontNew, masterId, kernKeys):
	#print("++", masterId)
	newPairs = list()
	masterKerningOld = fontOld.kerning[masterId]
	masterKerningNew = fontNew.kerning[masterId]
	if masterKerningOld is None or masterKerningNew is None:
		# this master has linked metrics. We don’t need to check it
		return newPairs
	
	mappedId = fontOld.masterIDforMetrics_(masterId)
	if mappedId != masterId:
		print("!!!!", "the master", fontOld.masters[masterId].name, "has metrics mapping but also has its own kerning (%s)" % masterId)
		return newPairs

	for leftKeyNew, rightKerningNew in masterKerningNew.items():
		leftKeyOld, leftPlainKey = oldKeyNewKey(leftKeyNew, fontOld, fontNew)
		if leftPlainKey in kerningKeys:
			continue
		rightKerningOld = masterKerningOld.get(leftKeyOld, {})
		for rightKeyNew, kerningNew in rightKerningNew.items():
			rightKeyOld, rightPlainKey = oldKeyNewKey(rightKeyNew, fontOld, fontNew)
			if rightPlainKey in kerningKeys:
				continue
			kerningOld = rightKerningOld.get(rightKeyOld, None)
			if not kerningOld:
				newPairs.append((leftPlainKey, rightPlainKey))
				# fontNew.removeKerningForPair(masterId, leftKeyNew, rightKeyNew)
				fontNew.removeKerningForFontMasterID_leftKey_rightKey_direction_(masterId, leftKeyNew, rightKeyNew, LTR);
	return newPairs

def findNewKerningPairs(fontOld, fontNew, masterId):
	#print("++", masterId)
	newPairs = list()
	masterKerningOld = fontOld.kerning[masterId]
	masterKerningNew = fontNew.kerning[masterId]
	if masterKerningOld is None or masterKerningNew is None:
		# this master has linked metrics. We don’t need to check it
		return newPairs
	
	mappedId = fontOld.masterIDforMetrics_(masterId)
	if mappedId != masterId:
		print("!!!!", "the master", fontOld.masters[masterId].name, "has metrics mapping but also has its own kerning (%s)" % masterId)
		return newPairs

	for leftKeyNew, rightKerningNew in masterKerningNew.items():
		leftKeyOld, leftPlainKey = oldKeyNewKey(leftKeyNew, fontOld, fontNew)
		rightKerningOld = masterKerningOld.get(leftKeyOld, {})
		for rightKeyNew, kerningNew in rightKerningNew.items():
			rightKeyOld, rightPlainKey = oldKeyNewKey(rightKeyNew, fontOld, fontNew)
			kerningOld = rightKerningOld.get(rightKeyOld, None)
			if not kerningOld:
				newPairs.append((leftPlainKey, rightPlainKey))
	return newPairs

def buildKerningGroups(font, glyphNames):
	groups = set()
	for glyphName in glyphNames:
		glyph = font.glyphs[glyphName]
		if not glyph:
			print("!!!! didn’t found glyph", glyphName)
			continue
		group = glyph.leftKerningGroupId()
		if group:
			groups.add(group)
		group = glyph.rightKerningGroupId()
		if group:
			groups.add(group)
	return groups

def filterKerning(pairs, kerningKeys):
	unrelatedPairs = list()
	for pair in pairs:
		leftKey = pair[0]
		rightKey = pair[1]
		if leftKey in kerningKeys:
			continue
		if rightKey in kerningKeys:
			continue
		unrelatedPairs.append(pair)
	return unrelatedPairs

fontOld = None
fontNew = None


for font in Glyphs.fonts:
	if not font.familyName.startswith("Google Sans Flex"):
		continue
	if font.versionMinor == 2:
		fontOld = font
	elif font.versionMinor == 3:
		fontNew = font

if not fontOld or not fontNew:
	Message("Please open two GSF files and set version minor to '002' in one and '003' in the other")
else:
	kerningKeys = buildKerningGroups(fontNew, newGlyphs)
	#print("__kerningKeys", kerningKeys)
	kerningKeys.update(newGlyphs)

	pairs = set()
	removedPairs = set()
	for idx in range(len(fontNew.masters)):
		masterOld = fontOld.masters[idx]
		masterNew = fontNew.masters[idx]
		assert masterOld.name == masterNew.name
		assert masterOld.id == masterNew.id

		newPairs = findNewKerningPairs(fontOld, fontNew, masterOld.id)
		pairs.update(newPairs)
		
		newPairs = removeNewKerningPairs(fontOld, fontNew, masterOld.id, kerningKeys)
		removedPairs.update(newPairs)

	print("__newPairs", len(pairs))
	#pprint(pairs)
	
	unrelatedPairs = filterKerning(pairs, kerningKeys)

	print("__unrelatedPairs:", len(unrelatedPairs))
	#pprint(unrelatedPairs)

	print("__removedPairs:", len(removedPairs))