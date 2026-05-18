"""Read and bump the package version used for distribution."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_INIT = ROOT / "src" / "bling_jwt_auth" / "__init__.py"
VERSION_RE = re.compile(r'^__version__ = "(\d+)\.(\d+)\.(\d+)"$', re.MULTILINE)


def read_version() -> str:
    """Return the current package version from ``__init__.py``."""
    content = PACKAGE_INIT.read_text(encoding="utf-8")
    match = VERSION_RE.search(content)
    if match is None:
        msg = f"Could not find __version__ in {PACKAGE_INIT}"
        raise SystemExit(msg)
    return ".".join(match.groups())


def bump_version(part: str) -> str:
    """Increment one semantic-version component and write it back."""
    major, minor, patch = (int(value) for value in read_version().split("."))
    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    else:
        msg = f"Unsupported version part: {part}"
        raise SystemExit(msg)

    next_version = f"{major}.{minor}.{patch}"
    content = PACKAGE_INIT.read_text(encoding="utf-8")
    updated = VERSION_RE.sub(f'__version__ = "{next_version}"', content, count=1)
    PACKAGE_INIT.write_text(updated, encoding="utf-8")
    return next_version


def dist_glob() -> str:
    """Return the dist glob matching artifacts for the current version."""
    return f"dist/bling_jwt_auth-{read_version()}*"


def main() -> None:
    """Run the version helper CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("get", help="print the current package version")
    subparsers.add_parser("dist-glob", help="print the current dist artifact glob")
    bump_parser = subparsers.add_parser("bump", help="increment the package version")
    bump_parser.add_argument("part", choices=["major", "minor", "patch"])

    args = parser.parse_args()
    if args.command == "get":
        sys.stdout.write(f"{read_version()}\n")
    elif args.command == "dist-glob":
        sys.stdout.write(f"{dist_glob()}\n")
    elif args.command == "bump":
        sys.stdout.write(f"{bump_version(args.part)}\n")


if __name__ == "__main__":
    main()
