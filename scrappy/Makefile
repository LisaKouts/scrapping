VENV_PYTHON := venv\Scripts\python

.PHONY: help
help:
	@echo "Usage:"
	@echo "  make run       Run the main Python script"

.PHONY: run
run:
	@$(VENV_PYTHON) scrappy.py

setup: requirements.txt
	pip install -r requirements.txt

clean:
    rm -rf __pycache__