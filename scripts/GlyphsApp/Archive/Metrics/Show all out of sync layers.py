# MenuTitle: Show all out of sync layers

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

layers = []
for layer in Glyphs.font.selectedLayers[0].parent.layers:
	if layer.isMasterLayer and layer.metricsKeysOutOfSync():
		print(layer)
		layers.append(layer)

Glyphs.font.newTab(layers)
