# Variables
VENV_DIR = venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip

# Check if virtual environment exists, if not, create it
$(VENV_DIR)/bin/activate:
	python3.12 -m venv $(VENV_DIR)

# Install main and dev dependencies
install: $(VENV_DIR)/bin/activate
	$(PIP) install -r requirements-dev.txt

# Run the download script with specified lower, upper bounds, and target folder
run: $(VENV_DIR)/bin/activate
	$(PYTHON) src/download_episodes.py $(lower) $(upper) $(folder)

# Lint the code
lint: $(VENV_DIR)/bin/activate
	$(VENV_DIR)/bin/flake8 src

# Format code with Black and sort imports with isort
format: $(VENV_DIR)/bin/activate
	$(VENV_DIR)/bin/black src
	$(VENV_DIR)/bin/isort src

# Run tests
test: $(VENV_DIR)/bin/activate
	$(VENV_DIR)/bin/pytest tests
