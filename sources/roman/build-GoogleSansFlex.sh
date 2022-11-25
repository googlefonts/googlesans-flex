
source tools/gsflex-env/bin/activate

## MAKE VF

fontmake -m sources/roman/GoogleSansFlex.designspace -o variable --output-path fonts/GoogleSansFlex-Beta1.0[ROND,opsz,wdth,wght]-VF.ttf --no-production-names

#fontmake -m sources/GoogleSansFlex-Squiggle/GoogleSansFlex-Squiggle.designspace -o variable --output-path fonts/GoogleSansFlex-Squiggle[WHGT,wdth]-VF.ttf --no-production-names

deactivate