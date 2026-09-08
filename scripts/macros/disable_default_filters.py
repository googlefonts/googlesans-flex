# Copyright 2026 Google Sans Flex Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Disables default filters. Necessary when using fontc with Glyphs sources, as
there's no other means by which to control this currently
"""

default_master = next(
    master for master in Glyphs.font.masters if master.name == "Regular"
)
default_master.userData["com.github.googlei18n.ufo2ft.filters"] = ()
print("disabled default filters")
