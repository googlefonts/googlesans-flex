ds-vf := "fonts-ds/variable/GoogleSansFlex[GRAD,ROND,opsz,slnt,wdth,wght].ttf"
gp-vf := "fonts-gp/variable/GoogleSansFlex[GRAD,ROND,opsz,slnt,wdth,wght].ttf"
fontc := ".venv/bin/fontc"
# fontc := "~/Tools/fontc/target/release/fontc"

export SOURCE_DATE_EPOCH := "1781694006"

ds:
    @rm -rf fonts-ds fonts
    uv run --python .venv gftools builder --experimental-fontc {{fontc}} sources/config.yaml
    mv fonts fonts-ds

gp:
    @rm -rf fonts-gp fonts
    uv run --python .venv gftools builder --experimental-fontc {{fontc}} sources/config-gp.yaml
    mv fonts fonts-gp

diffenate:
    diffenator3 --html --masters {{ds-vf}} {{gp-vf}}

ttx:
    @mkdir -p out/ttx-{ds,gp}
    @rm -rf out/ttx-{ds,gp}/*
    -ttx-diff --outdir out \
        --fontmake_font {{ds-vf}} \
        --fontc_font {{gp-vf}}
    @rm out/default/*.ttf out/default/{fontc,fontmake}.ttx
    @for f in out/default/fontc*; do mv -- "$f" "out/ttx-gp/GSF${f##*/fontc}"; done
    @for f in out/default/fontmake*; do mv -- "$f" "out/ttx-ds/GSF${f##*/fontmake}"; done
    @rm -rf out/default

qa:
    @mkdir -p out
    -fontspector --loglevel warn --succinct --full-lists \
        --profile qa/googlesans-profile.toml --configuration qa/googlesans-config.toml \
        --plugin qa/check-charset.py,qa/check-fea.py,qa/check-googlesans.py \
        --html out/fontspector-designspace-report.html \
        {{ds-vf}}
    -fontspector --loglevel warn --succinct --full-lists \
        --profile qa/googlesans-profile.toml --configuration qa/googlesans-config.toml \
        --plugin qa/check-charset.py,qa/check-fea.py,qa/check-googlesans.py \
        --html out/fontspector-glyphspackage-report.html \
        {{gp-vf}}
    -xdg-open out/fontspector-designspace-report.html
    -xdg-open out/fontspector-glyphspackage-report.html
