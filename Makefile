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
	@echo "  make test:   Tests the fonts with fontbakery"
	@echo "  make proof:  Creates HTML proof documents in the proof/ directory"
	@echo "  make images: Creates PNG specimen images in the documentation/ directory"
	@echo

build: build.stamp

venv: venv/touchfile

build.stamp: venv sources/config.yaml $(SOURCES)
	rm -rf fonts/
	. venv/bin/activate \
		&& gftools builder sources/config.yaml
# Font-v cannot deal with worktrees, which we use for imports. See
# https://github.com/source-foundry/font-v/issues/169. Just skip it.
	if [ -z "${SKIP_FONTV}" ]; then venv/bin/font-v write --sha1 fonts/variable/*.ttf; fi
	venv/bin/python scripts/prune_font_binary.py fonts/variable/*.ttf
# TODO: Re-enable when additional designspaces are restored.
#venv/bin/python scripts/set-overlap-bits.py sources/regular/glyphs-with-overlap.txt sources/regular/GoogleSansFlex.designspace fonts/variable/GoogleSansFlex[ROND,opsz,wdth,wght].ttf
#venv/bin/python scripts/set-overlap-bits.py sources/italic/glyphs-with-overlap.txt sources/italic/GoogleSansFlex-Italic.designspace fonts/variable/GoogleSansFlex-Italic[ROND,opsz,wdth,wght].ttf
#venv/bin/python scripts/set-overlap-bits.py sources/regular/glyphs-with-overlap.txt sources/GoogleSansFlex.designspace fonts/variable/GoogleSansFlex[GRAD,ROND,opsz,slnt,wdth,wght].ttf
# Remove intermediary file leftover by gftools
# https://github.com/googlefonts/gftools/issues/764
	rm -vf fonts/variable/*.ttf.stat.yaml
	touch build.stamp

venv/touchfile: requirements.txt
	test -d venv || python3 -m venv venv
	. venv/bin/activate \
		&& pip install -U setuptools wheel pip \
		&& pip install --no-deps -r requirements.txt
	touch venv/touchfile

test: build.stamp
	@scripts/fontbakery.sh

run-collidoscope: build.stamp
# Install latest version of fontbakery on every run, isolated from build dependencies
	test -d venv_bakery || python3 -m venv venv_bakery
	venv_bakery/bin/pip install -U setuptools wheel pip
	venv_bakery/bin/pip install -U fontbakery[googlefonts] fonttools[interpolatable]

# Run collidoscope tests
	mkdir -p out/fontbakery
	-venv_bakery/bin/fontbakery check-shaping -l WARN --auto-jobs --succinct --html out/fontbakery/fontbakery-collidoscope-report.html \
		--configuration qa/fontbakery.config \
		-c collides \
		 fonts/variable/GoogleSansFlex[GRAD,ROND,opsz,slnt,wdth,wght].ttf

images: venv build.stamp $(DRAWBOT_OUTPUT)
	git add documentation/*.png && git commit -m "Rebuild images" documentation/*.png

%.png: %.py build.stamp
	python3 $< --output $@

clean:
	rm -rf venv
	find . -name "*.pyc" | xargs rm delete

update-project-template:
	npx update-template https://github.com/googlefonts/googlefonts-project-template/

update-glyphset-expectations:
	. venv/bin/activate && python scripts/gs-update-glyphset-qa-files.py

update-shaping-expectations:
	. venv/bin/activate && bash -c "cd qa && bash update_all_shaping.sh"

update:
	pip install -U pip-tools
	pip-compile --resolver=backtracking -U requirements.in

font-size: build
	venv/bin/pip install -U font-size
	find fonts -name '*.ttf' -type f | xargs venv/bin/font-size

progress-chart: venv
	. venv/bin/activate && python scripts/gs-progress-burndown.py

bump-to-tag: venv
	. venv/bin/activate && python3 scripts/bump-to-tag.py

glyph-hunt: venv
	. venv/bin/activate && python scripts/glyph-hunt.py --glyph-list .github/actions/import/glyph-list.txt --ds sources/regular/GoogleSansFlex.designspace
