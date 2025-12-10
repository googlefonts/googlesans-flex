# MenuTitle: Clean Unaccessible Kerning

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

from GlyphsApp import Glyphs

font = Glyphs.font

for master in font.masters:
	if not font.kerning.get(master.id):
		continue
	mappedId = font.masterIDforMetrics_(master.id)
	if mappedId != master.id:
		print("!! unneeded kerning in master", master.name)
		del font.kerning[master.id]