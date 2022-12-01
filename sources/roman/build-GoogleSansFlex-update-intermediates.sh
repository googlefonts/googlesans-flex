
__DIR__="$(cd "$(dirname "${0}")"; echo "$(pwd)")"

source tools/gsflex-prod-env/bin/activate

echo "Generating UFO instances"

fontmake -m sources/GoogleSansFlex-intermediates.designspace -i -o ufo

python tools/updateIntermediates.py

deactivate

