PYTHON ?= python3

.PHONY: setup test cli-help index-paper benchmark-paper report-paper preflight release-bundle-lite release-bundle-full

setup:
	$(PYTHON) -m pip install --upgrade pip setuptools wheel
	$(PYTHON) -m pip install -e .

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -p 'test_*.py'

cli-help:
	PYTHONPATH=src $(PYTHON) -m switching_sde.cli.main --help

index-paper:
	@if [ -z "$$LEGACY_PENN_ROOT" ]; then echo "LEGACY_PENN_ROOT is required"; exit 1; fi
	PYTHONPATH=src $(PYTHON) -m switching_sde.cli.main artifacts index --legacy-root "$$LEGACY_PENN_ROOT"
	PYTHONPATH=src $(PYTHON) -m switching_sde.cli.main artifacts link --legacy-root "$$LEGACY_PENN_ROOT"

benchmark-paper:
	@if [ -z "$$LEGACY_PENN_ROOT" ]; then echo "LEGACY_PENN_ROOT is required"; exit 1; fi
	PYTHONPATH=src $(PYTHON) -m switching_sde.cli.main benchmark --suite paper_full --mode frozen --legacy-root "$$LEGACY_PENN_ROOT"

report-paper:
	@if [ -z "$$LEGACY_PENN_ROOT" ]; then echo "LEGACY_PENN_ROOT is required"; exit 1; fi
	PYTHONPATH=src $(PYTHON) -m switching_sde.cli.main report --suite paper_full --legacy-root "$$LEGACY_PENN_ROOT"

preflight:
	@if [ -z "$$LEGACY_PENN_ROOT" ]; then echo "LEGACY_PENN_ROOT is required"; exit 1; fi
	$(PYTHON) scripts/release_preflight.py --legacy-root "$$LEGACY_PENN_ROOT"

release-bundle-lite:
	$(PYTHON) scripts/build_release_bundle.py --mode lite --output dist/switching_sde_release_lite.tar.gz

release-bundle-full:
	$(PYTHON) scripts/build_release_bundle.py --mode full --output dist/switching_sde_release_full.tar.gz
