PANDOC    ?= pandoc
PYTHON    ?= python3
TEMPLATE  := orgatex-template.potx
REFERENCE := orgatex-reference.potx
SOURCES   := $(wildcard presentations/*.md)
DECKS     := $(patsubst presentations/%.md,output/%.pptx,$(SOURCES))
MOCKUPS_HTML := $(wildcard assets/mockups/*.html)
MOCKUPS_PNG  := $(patsubst %.html,%.png,$(MOCKUPS_HTML))

.PHONY: all reference check mockups clean
all: $(DECKS)

reference: $(REFERENCE)

$(REFERENCE): $(TEMPLATE) scripts/build-reference.py
	$(PYTHON) scripts/build-reference.py $(TEMPLATE) $(REFERENCE)

mockups: $(MOCKUPS_PNG)

assets/mockups/%.png: assets/mockups/%.html assets/mockups/mockup.css scripts/build-mockups.py
	$(PYTHON) scripts/build-mockups.py $<

output/%.pptx: presentations/%.md $(REFERENCE) pandoc/defaults.yaml | output
	$(PANDOC) --defaults pandoc/defaults.yaml $< -o $@

output/hermes-vertrieb.pptx: $(MOCKUPS_PNG)

output:
	mkdir -p output

check: $(REFERENCE)
	$(PYTHON) scripts/check-reference.py $(REFERENCE) presentations/smoke-test.md

clean:
	rm -rf output $(REFERENCE)
