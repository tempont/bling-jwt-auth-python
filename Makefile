.PHONY: check build version bump-patch bump-minor bump-major release-patch release-minor release-major

check:
	bash scripts/check.sh

build: check
	uv run --extra dev python -m build
	uv run --extra dev python -m twine check $$(python scripts/package_version.py dist-glob)

version:
	python scripts/package_version.py get

bump-patch:
	python scripts/package_version.py bump patch

bump-minor:
	python scripts/package_version.py bump minor

bump-major:
	python scripts/package_version.py bump major

release-patch: bump-patch build

release-minor: bump-minor build

release-major: bump-major build
