PANDOC    ?= pandoc
PYTHON    ?= python3
TEMPLATE  := orgatex-template.potx
REFERENCE := orgatex-reference.potx
SOURCES   := $(wildcard presentations/*.md)
DECKS     := $(patsubst presentations/%.md,output/%.pptx,$(SOURCES))

.PHONY: all reference check clean
all: $(DECKS)

reference: $(REFERENCE)

$(REFERENCE): $(TEMPLATE) scripts/build-reference.py
	$(PYTHON) scripts/build-reference.py $(TEMPLATE) $(REFERENCE)

output/%.pptx: presentations/%.md $(REFERENCE) pandoc/defaults.yaml | output
	$(PANDOC) --defaults pandoc/defaults.yaml $< -o $@

output:
	mkdir -p output

check: $(REFERENCE)
	$(PYTHON) scripts/check-reference.py $(REFERENCE) presentations/smoke-test.md

clean:
	rm -rf output $(REFERENCE)
