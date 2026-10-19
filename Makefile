UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
	REALPATH := grealpath
else
	REALPATH := realpath
endif

BUILD := build
DIST := dist
MAKE := make
PYTHON := python
PYINSTALLER := pyinstaller
REQUIREMENTS := requirements.txt
VENV := .venv
VENVACTIVATE := $(VENV)/bin/activate
VENV_PIP := $(VENV)/bin/pip
VENV_PYTHON := $(VENV)/bin/python

setup:
	@$(MAKE) venv
	@$(MAKE) dependencies
	@$(MAKE) install
	@$(MAKE) link

venv:
	$(PYTHON) -m venv "$(VENV)"

dependencies:
	@$(VENV_PIP) install -r $(REQUIREMENTS)

install:
	source $(VENVACTIVATE) ; $(PYINSTALLER) --noconfirm porydex.py

link:
	ln -s $(shell $(REALPATH) dist/porydex/porydex) "$(VENV)/bin/porydex"

test:
	$(VENV_PYTHON) -m pytest tests

clean:
	rm -rf "$(VENV)"
	rm -rf "$(BUILD)"
	rm -rf "$(DIST)"
