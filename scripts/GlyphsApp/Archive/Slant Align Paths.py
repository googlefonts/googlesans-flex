#MenuTitle: Slant Align Paths

layers = Glyphs.font.currentTab.selectedLayers
for layer in layers:
    slantHeight = layer.associatedFontMaster().slantHeightForLayer_(layer)
    layer.slantX_origin_doCorrection_checkSelection_(-10, slantHeight, False, False)
    transformer = NSClassFromString("GlyphsPaletteTransform").new()
    transformer.alignSelection_layers_checkSelection_(1, [layer], False)
    layer.slantX_origin_doCorrection_checkSelection_(10, slantHeight, False, False)
