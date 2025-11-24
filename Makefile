export UV_PYTHON=$(shell cat .github/workflows/python-version.txt)
UV_RUN=uv run --with-requirements requirements.txt

SOURCES=$(shell python3 scripts/read-config.py --sources )
FAMILY=$(shell python3 scripts/read-config.py --family )
DRAWBOT_SCRIPTS=$(shell ls documentation/*.py)
DRAWBOT_OUTPUT=$(shell ls documentation/*.py | sed 's/\.py/.png/g')

help:
	@echo "###"
	@echo "# Build targets for $(FAMILY)"
	@echo "###"
	@echo
	@echo "  make build:  Builds the fonts and places them in the fonts/ directory"
	@echo "  make release:  Builds the fonts above, along with Android and Workspace-specific variants"
	@echo "  make test:   Tests the fonts with fontbakery"
	@echo "  make images: Creates PNG specimen images in the documentation/ directory"
	@echo

build: build.stamp

build.stamp: requirements.txt sources/config.yaml $(SOURCES)
	rm -rf fonts/
	$(UV_RUN) gftools builder --experimental-fontc $(shell uv run --with-requirements requirements.txt which fontc) sources/config.yaml
# Font-v cannot deal with worktrees, which we use for imports. See
# https://github.com/source-foundry/font-v/issues/169. Just skip it.
	if [ -z "${SKIP_FONTV}" ]; then $(UV_RUN) font-v write --sha1 fonts/variable/*.ttf; fi
	$(UV_RUN) scripts/prune_font_binary.py fonts/variable/*.ttf
	$(UV_RUN) scripts/set-overlap-bits.py sources/glyphs-with-overlap.txt sources/GoogleSansFlex.designspace fonts/variable/GoogleSansFlex[GRAD,ROND,opsz,slnt,wdth,wght].ttf
	touch build.stamp

test: build.stamp
	@scripts/fontbakery.sh

android: build.stamp
	mkdir -p fonts/android
	-@rm fonts/android/*.ttf
	$(UV_RUN) scripts/set_ymin_ymax.py \
		--ymin -605 --ymax 2007 \
		fonts/variable/GoogleSansFlex[GRAD,ROND,opsz,slnt,wdth,wght].ttf \
		--output fonts/android/GoogleSansFlex[GRAD,ROND,opsz,slnt,wdth,wght].ttf
	$(UV_RUN) scripts/prune_hvar.py \
		fonts/android/GoogleSansFlex[GRAD,ROND,opsz,slnt,wdth,wght].ttf

workspace: build.stamp
	-@rm fonts/workspace/*.ttf
	-@rm fonts/tv/*.ttf
	$(UV_RUN) scripts/cut_instances.py \
		fonts/variable/GoogleSansFlex[GRAD,ROND,opsz,slnt,wdth,wght].ttf \
		fonts/workspace
	mkdir -p fonts/tv
	mv fonts/workspace/GoogleSansFlexTV[wght].ttf fonts/tv
	$(UV_RUN) pyftsubset fonts/tv/GoogleSansFlexTV[wght].ttf --output-file=fonts/tv/GoogleSansFlexTV[wght].ttf --unicodes="U+D-25CC,U+FB00-1D61E" --layout-features="tnum,numr,subs,sups,frac,ordn,dnom,zero,kern,locl,mark,mkmk,ccmp,liga" --name-IDs="*" --recalc-average-width --recalc-max-context --recalc-bounds --notdef-outline

release: android workspace

COLLIDOSCOPE_OPTS = fontbakery \
	check-googlefonts -l WARN --auto-jobs --succinct \
	--html out/fontbakery/fontbakery-collidoscope-report.html \
	--configuration qa/fontbakery.config \
	-c shaping/collides \
	fonts/variable/GoogleSansFlex[GRAD,ROND,opsz,slnt,wdth,wght].ttf

run-collidoscope: build.stamp
	mkdir -p out/fontbakery
	if [ -e requirements-fb.txt ]; then \
		uvx --with-requirements requirements-fb.txt $(COLLIDOSCOPE_OPTS); \
	else \
		uvx --with fontbakery[googlefonts] --with fonttools[interpolatable] $(COLLIDOSCOPE_OPTS); \
	fi

images: build.stamp $(DRAWBOT_OUTPUT)
	git add documentation/*.png && git commit -m "Rebuild images" documentation/*.png

%.png: %.py build.stamp
	$(UV_RUN) python $< --output $@

clean:
	rm -rf .venv
	find . -name "*.pyc" | xargs rm delete

update-project-template:
	npx update-template https://github.com/googlefonts/googlefonts-project-template/

update-glyphset-expectations:
	$(UV_RUN) scripts/gs-update-glyphset-qa-files.py

update-shaping-expectations:
	$(UV_RUN) bash -c "cd qa && bash update_all_shaping.sh"

update:
	uv pip compile --universal requirements.in > requirements.txt

font-size: build
	-@[ -n "${GITHUB_RUN_ID}" ] && echo "::group::TTF size report, by table"
	find fonts -name '*.ttf' -type f | xargs uvx font-size
	-@[ -n "${GITHUB_RUN_ID}" ] && echo "::endgroup::"
	-@[ -n "${GITHUB_RUN_ID}" ] && echo "::group::'gvar' size report, by glyph"
	uv run --with fonttools --with rich scripts/gvar_by_glyph.py fonts/variable/GoogleSansFlex[GRAD,ROND,opsz,slnt,wdth,wght].ttf
	-@[ -n "${GITHUB_RUN_ID}" ] && echo "::endgroup::"

progress-chart:
	$(UV_RUN) scripts/gs-progress-burndown.py

bump-to-tag:
	$(UV_RUN) scripts/bump-to-tag.py

glyph-hunt:
	$(UV_RUN) scripts/glyph-hunt.py --glyph-list .github/actions/import/glyph-list.txt --ds sources/regular/GoogleSansFlex.designspace

shaperglot: build
	mkdir -p out
# Report coverage of all languages
	uvx shaperglot report --group fonts/variable/GoogleSansFlex[GRAD,ROND,opsz,slnt,wdth,wght].ttf
	@echo "\nChecking against the target language list"
# Report coverage of target languages
	@xargs uvx shaperglot check fonts/variable/GoogleSansFlex[GRAD,ROND,opsz,slnt,wdth,wght].ttf < qa/target_langs.txt

autobase: build
	cargo binstall --no-confirm autobase-cli || cargo install --locked autobase-cli
	autobase --min-max --config sources/autobase.toml --words 1000000 fonts/variable/GoogleSansFlex[GRAD,ROND,opsz,slnt,wdth,wght].ttf

.PHONY: release autobase
