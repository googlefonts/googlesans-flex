fontmake -m GSF-4style.designspace.xml -o variable --output-path variable_ttf/GSF-4style.designspace-VF.ttf;
fontmake -m GSF-4style.designspace.xml -o variable --output-path variable_ttf/GSF-4style.designspace-VF-no-optimize-gvar.ttf --no-optimize-gvar;

fontmake -m GSF-5style.designspace.xml -o variable --output-path variable_ttf/GSF-5style.designspace-VF.ttf;
fontmake -m GSF-5style.designspace.xml -o variable --output-path variable_ttf/GSF-5style.designspace-VF-no-optimize-gvar.ttf --no-optimize-gvar;

fontmake -m GSF-5style-ROND0000001.designspace.xml -o variable --output-path variable_ttf/GSF-5style-ROND0000001.designspace-VF-no-optimize-gvar.ttf --no-optimize-gvar;

fontmake -m GSF-5style-ROND0_00006103515.designspace.xml -o variable --output-path variable_ttf/GSF-5style-ROND0_00006103515.designspace-VF-no-optimize-gvar.ttf --no-optimize-gvar;

fontmake -m GSF-3style-ROND0_00006103515.designspace.xml -o variable --output-path variable_ttf/GSF-3style-ROND0_00006103515.designspace-VF-no-optimize-gvar.ttf --no-optimize-gvar;

fontmake -m GSF-5style-ROND001-centered.designspace.xml -o variable --output-path variable_ttf/GSF-3style-ROND001-centered.designspace-VF-no-optimize-gvar.ttf --no-optimize-gvar;

gftools builder --debug --no-clean-up GSF-5style-ROND001-centered.config.yaml;

fontmake -m GSF-3style-ROND0_006103515625.designspace.xml -o variable --output-path variable_ttf/GSF-3style-ROND0_006103515625.designspace-VF-no-optimize-gvar.ttf --no-optimize-gvar;


