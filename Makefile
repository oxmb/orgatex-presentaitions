PANDOC    ?= pandoc
PYTHON    ?= python3
TEMPLATE  := orgatex-template.potx
REFERENCE := orgatex-reference.potx
SOURCES   := $(wildcard presentations/*.md)
DECKS     := $(patsubst presentations/%.md,output/%.pptx,$(SOURCES))
PDFS      := $(patsubst presentations/%.md,output/%.pdf,$(SOURCES))
MOCKUPS_HTML := $(wildcard assets/mockups/*.html)
MOCKUPS_PNG  := $(patsubst %.html,%.png,$(MOCKUPS_HTML))
DEPLOY_DIR := $(HOME)/OneDrive/Präsentationen

.PHONY: all pdf reference check mockups clean deploy
all: $(DECKS)
pdf: $(PDFS)

reference: $(REFERENCE)

$(REFERENCE): $(TEMPLATE) scripts/build-reference.py
	$(PYTHON) scripts/build-reference.py $(TEMPLATE) $(REFERENCE)

mockups: $(MOCKUPS_PNG)

assets/mockups/%.png: assets/mockups/%.html assets/mockups/mockup.css scripts/build-mockups.py
	$(PYTHON) scripts/build-mockups.py $<

output/layout-demo.pptx: presentations/layout-demo.md $(REFERENCE) pandoc/defaults.yaml scripts/build-layout-demo.py | output
	$(PYTHON) scripts/build-layout-demo.py

output/%.pptx: presentations/%.md $(REFERENCE) pandoc/defaults.yaml | output
	$(PANDOC) --defaults pandoc/defaults.yaml $< -o $@

BEAMER_DEPS := pandoc/defaults-beamer.yaml pandoc/beamerthemeOrgatex.sty \
               assets/logo-wide.pdf assets/logo-mark.pdf

output/%.pdf: presentations/%.md $(BEAMER_DEPS) | output
	TEXINPUTS=pandoc//:$(TEXINPUTS) $(PANDOC) --defaults pandoc/defaults-beamer.yaml $< -o $@

output/hermes-vertrieb.pptx output/hermes-vertrieb.pdf: $(MOCKUPS_PNG) assets/mockups/architektur.svg

output/fw-split-vertrieb.pptx output/fw-split-vertrieb.pdf: assets/mockups/ota-dashboard.png assets/mockups/feature-flags.png

assets/mockups/ota-dashboard.png: assets/mockups/ota-dashboard.html assets/mockups/tb-mockup.css scripts/build-mockups.py
	$(PYTHON) scripts/build-mockups.py $<

assets/mockups/feature-flags.png: assets/mockups/feature-flags.html assets/mockups/tb-mockup.css scripts/build-mockups.py
	$(PYTHON) scripts/build-mockups.py $<

output:
	mkdir -p output

check: $(REFERENCE)
	$(PYTHON) scripts/check-reference.py $(REFERENCE) presentations/smoke-test.md

deploy: $(DECKS)
	cp $(DECKS) $(DEPLOY_DIR)/

clean:
	rm -rf output $(REFERENCE)
