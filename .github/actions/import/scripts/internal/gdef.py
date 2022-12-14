# Copyright 2021 Google Sans Authors
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
"""Update the GDEF definition in the feature file.

We want our own because Glyphs has the habit of propagating anchors on
_everything_, even symbols that happen to contain components of latin
glyphs with anchors.
"""

# pyright: basic

from typing import Dict, Optional

import glyphsLib.builder.constants
import glyphsLib.glyphdata
import ufoLib2

KNOWN_BASES = {
    "k_ssa-deva",
    "j_nya-deva",
    "k_ss-deva",
    "k_ss-deva.alt2",
    "k_ss-deva.alt3",
    "k_ss-deva.alt4",
    "k_ss-deva.alt5",
    "k_ss-deva.alt6",
    "k_ss-deva.alt7",
    "j_ny-deva",
    "j_ny-deva.alt2",
    "j_ny-deva.alt3",
    "j_ny-deva.alt4",
    "j_ny-deva.alt5",
    "j_ny-deva.alt6",
    "j_ny-deva.alt7",
    "j_ny-deva.alt8",
    "ng_ya-deva",
    "ch_ya-deva",
    "tt_tta-deva",
    "tt_ttha-deva",
    "tt_ya-deva",
    "tth_ttha-deva",
    "tth_ya-deva",
    "dd_dda-deva",
    "dd_ddha-deva",
    "dd_ya-deva",
    "ddh_ddha-deva",
    "ddh_ya-deva",
    "t_ta-deva",
    "t_ra-deva",
    "d_ga-deva",
    "d_gha-deva",
    "d_da-deva",
    "d_dha-deva",
    "d_dh_ya-deva",
    "d_ba-deva",
    "d_bha-deva",
    "d_ma-deva",
    "d_ya-deva",
    "d_ra-deva",
    "d_va-deva",
    "p_ta-deva",
    "sh_ra-deva",
    "ss_tta-deva",
    "ss_ttha-deva",
    "h_nna-deva",
    "h_na-deva",
    "h_ma-deva",
    "h_ya-deva",
    "h_ra-deva",
    "h_la-deva",
    "h_va-deva",
    "h_ra_uMatra-deva",
    "h_ra_uuMatra-deva",
    "ba-khmer",
    "ba-khmer.post",
    "ba-khmer.post2",
    "ba_aaSign-khmer",
    "ba_aaSign-khmer.post2_",
    "ba_aaSign-khmer.post_",
    "ba_auSign-khmer",
    "ba_auSign-khmer.post2_",
    "ba_auSign-khmer.post_",
    "beikoet-khmer",
    "beiroc-khmer",
    "buonkoet-khmer",
    "buonroc-khmer",
    "ca-khmer",
    "ca_aaSign-khmer",
    "ca_auSign-khmer",
    "cha-khmer",
    "cha_aaSign-khmer",
    "cha_auSign-khmer",
    "cho-khmer",
    "cho-khmer.post",
    "cho-khmer.post2",
    "cho_aaSign-khmer",
    "cho_aaSign-khmer.post2_",
    "cho_aaSign-khmer.post_",
    "cho_auSign-khmer",
    "cho_auSign-khmer.post2_",
    "cho_auSign-khmer.post_",
    "co-khmer",
    "co_aaSign-khmer",
    "co_auSign-khmer",
    "da-khmer",
    "da_aaSign-khmer",
    "da_auSign-khmer",
    "dapBeikoet-khmer",
    "dapBeiroc-khmer",
    "dapBuonkoet-khmer",
    "dapBuonroc-khmer",
    "dapMuoykoet-khmer",
    "dapMuoyroc-khmer",
    "dapPiikoet-khmer",
    "dapPiiroc-khmer",
    "dapPramkoet-khmer",
    "dapPramroc-khmer",
    "dapkoet-khmer",
    "daproc-khmer",
    "do-khmer",
    "do_aaSign-khmer",
    "do_auSign-khmer",
    "dottedCircle",
    "ha-khmer",
    "ha_aaSign-khmer",
    "ha_auSign-khmer",
    "ka-khmer",
    "ka_aaSign-khmer",
    "ka_auSign-khmer",
    "kha-khmer",
    "kha_aaSign-khmer",
    "kha_auSign-khmer",
    "kho-khmer",
    "kho-khmer.post",
    "kho-khmer.post2",
    "kho_aaSign-khmer",
    "kho_aaSign-khmer.post2_",
    "kho_aaSign-khmer.post_",
    "kho_auSign-khmer",
    "kho_auSign-khmer.post2_",
    "kho_auSign-khmer.post_",
    "ko-khmer",
    "ko_aaSign-khmer",
    "ko_auSign-khmer",
    "la-khmer",
    "la_aaSign-khmer",
    "la_auSign-khmer",
    "lo-khmer",
    "lo_aaSign-khmer",
    "lo_auSign-khmer",
    "mo-khmer",
    "mo_aaSign-khmer",
    "mo_auSign-khmer",
    "muoykoet-khmer",
    "muoyroc-khmer",
    "ngo-khmer",
    "ngo_aaSign-khmer",
    "ngo_auSign-khmer",
    "nno-khmer",
    "nno_aaSign-khmer",
    "nno_auSign-khmer",
    "no-khmer",
    "no_aaSign-khmer",
    "no_auSign-khmer",
    "nyo-khmer",
    "nyo-khmer.less",
    "nyo_aaSign-khmer",
    "nyo_aaSign-khmer.less",
    "nyo_auSign-khmer",
    "nyo_auSign-khmer.less",
    "pathamasat-khmer",
    "pha-khmer",
    "pha_aaSign-khmer",
    "pha_auSign-khmer",
    "pho-khmer",
    "pho_aaSign-khmer",
    "pho_auSign-khmer",
    "piikoet-khmer",
    "piiroc-khmer",
    "po-khmer",
    "po_aaSign-khmer",
    "po_auSign-khmer",
    "pramBeikoet-khmer",
    "pramBeiroc-khmer",
    "pramBuonkoet-khmer",
    "pramBuonroc-khmer",
    "pramMuoykoet-khmer",
    "pramMuoyroc-khmer",
    "pramPiikoet-khmer",
    "pramPiiroc-khmer",
    "pramkoet-khmer",
    "pramroc-khmer",
    "qa-khmer",
    "qa_aaSign-khmer",
    "qa_auSign-khmer",
    "ro-khmer",
    "ro_aaSign-khmer",
    "ro_auSign-khmer",
    "sa-khmer",
    "sa-khmer.post",
    "sa_aaSign-khmer",
    "sa_aaSign-khmer.post_",
    "sa_auSign-khmer",
    "sa_auSign-khmer.post_",
    "sha-khmer",
    "sha_aaSign-khmer",
    "sha_auSign-khmer",
    "sso-khmer",
    "sso-khmer.post",
    "sso_aaSign-khmer",
    "sso_aaSign-khmer.post_",
    "sso_auSign-khmer",
    "sso_auSign-khmer.post_",
    "ta-khmer",
    "ta_aaSign-khmer",
    "ta_auSign-khmer",
    "tha-khmer",
    "tha_aaSign-khmer",
    "tha_auSign-khmer",
    "tho-khmer",
    "tho_aaSign-khmer",
    "tho_auSign-khmer",
    "to-khmer",
    "to_aaSign-khmer",
    "to_auSign-khmer",
    "ttha-khmer",
    "ttha_aaSign-khmer",
    "ttha_auSign-khmer",
    "ttho-khmer",
    "ttho-khmer.post",
    "ttho-khmer.post2",
    "ttho_aaSign-khmer",
    "ttho_aaSign-khmer.post2_",
    "ttho_aaSign-khmer.post_",
    "ttho_auSign-khmer",
    "ttho_auSign-khmer.post2_",
    "ttho_auSign-khmer.post_",
    "tuteyasat-khmer",
    "vo-khmer",
    "vo_aaSign-khmer",
    "vo_auSign-khmer",
    "yo-khmer",
    "yo-khmer.post",
    "yo-khmer.post2",
    "yo_aaSign-khmer",
    "yo_aaSign-khmer.post2_",
    "yo_aaSign-khmer.post_",
    "yo_auSign-khmer",
    "yo_auSign-khmer.post2_",
    "yo_auSign-khmer.post_",
}


def update_opentype_categories(ufo: ufoLib2.Font) -> Dict[str, str]:
    """Returns a `public.openTypeCategories` dictionary.

    Building it requires anchor propagation or user care to work as
    expected, as Glyphs.app also looks at anchors for classification:

    * base: any glyph that has an attaching anchor (such as "top"; "_top" does
      not count) and is neither classified as Ligature nor Mark using the
      definitions below;
    * ligature: if subCategory is "Ligature" and the glyph has at least one
      attaching anchor;
    * mark: if category is "Mark" and subCategory is either "Nonspacing" or
      "Spacing Combining";
    * composite: never assigned by Glyphs.app.

    See:

    * https://github.com/googlefonts/glyphsLib/issues/85
    * https://github.com/googlefonts/glyphsLib/pull/100#issuecomment-275430289
    """

    # Drop glyphs that don't exist in font anymore.
    existing: Dict[str, str] = ufo.lib.get("public.openTypeCategories", {})
    categories: Dict[str, str] = {k: v for k, v in existing.items() if k in ufo}

    category_key = glyphsLib.builder.constants.GLYPHLIB_PREFIX + "category"
    subcategory_key = glyphsLib.builder.constants.GLYPHLIB_PREFIX + "subCategory"

    for glyph in ufo:
        assert glyph.name is not None
        has_attaching_anchor = False
        for anchor in glyph.anchors:
            name = anchor.name
            if not name:
                continue
            if not name.startswith("_"):
                has_attaching_anchor = True

        # First check glyph.lib for category/subCategory overrides. Otherwise,
        # use global values from GlyphData.
        glyphinfo = glyphsLib.glyphdata.get_glyph(glyph.name)
        category: Optional[str] = glyph.lib.get(category_key, glyphinfo.category)
        subcategory: Optional[str] = glyph.lib.get(
            subcategory_key, glyphinfo.subCategory
        )

        if glyph.name in KNOWN_BASES:
            categories[glyph.name] = "base"
        elif subcategory == "Ligature" and has_attaching_anchor:
            categories[glyph.name] = "ligature"
        elif category == "Mark" and (
            subcategory == "Nonspacing" or subcategory == "Spacing Combining"
        ):
            categories[glyph.name] = "mark"
        elif category == "Letter" and has_attaching_anchor:
            categories[glyph.name] = "base"

    return categories
