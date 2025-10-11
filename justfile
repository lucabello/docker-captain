set shell := ["bash", "-c"]

[private]
default:
  just --list

# Lint the codebase using ruff
[group("dev")]
lint:
    ruff check

# Format the codebase using ruff
[group("dev")]
format:
    """Auto‑format code with black."""
    ruff format

# Build the project
[group("build")]
build:
    uv build

# Remove build artifacts, caches, and temporary files
[group("build")]
clean:
    # Remove __pycache__ directories
    find . -type d -name "__pycache__" -exec rm -r {} + || true
    # Remove .pytest_cache directory
    rm -rf .pytest_cache
    # Remove build/dist/egg-info directories
    rm -rf build dist *.egg-info
    # Remove coverage reports
    rm -f .coverage coverage.xml

# Release to PyPi
[group("release")]
release: clean build
    # uv publish?
