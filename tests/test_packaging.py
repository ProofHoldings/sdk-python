"""Packaging drift guard: every top-level third-party import in the SDK
must be covered by a declared (non-optional) dependency in pyproject.toml.
"""

import re
import sys
import tomllib
from pathlib import Path

SDK_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = SDK_ROOT / "src" / "proof_sdk"

# Modules provided by [project.optional-dependencies] extras and imported lazily.
OPTIONAL_EXTRA_MODULES = {"jwt"}

FROM_RE = re.compile(r"^from\s+([A-Za-z_][A-Za-z0-9_]*)", re.MULTILINE)
IMPORT_RE = re.compile(r"^import\s+([^\n#]+)", re.MULTILINE)


def top_level_imported_modules(text: str) -> set[str]:
    modules = set(FROM_RE.findall(text))
    for clause in IMPORT_RE.findall(text):
        for part in clause.split(","):
            name = part.strip().split(" ")[0].split(".")[0]
            if name:
                modules.add(name)
    return modules


def declared_dependency_modules() -> set[str]:
    with open(SDK_ROOT / "pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)
    modules = set()
    for spec in pyproject["project"]["dependencies"]:
        name = re.split(r"[<>=!~\[; ]", spec, maxsplit=1)[0]
        modules.add(name.lower().replace("-", "_"))
    return modules


def imported_third_party_modules() -> set[str]:
    modules = set()
    for path in SRC_ROOT.rglob("*.py"):
        for module in top_level_imported_modules(path.read_text(encoding="utf-8")):
            if module in sys.stdlib_module_names:
                continue
            if module in ("proof_sdk",) or module in OPTIONAL_EXTRA_MODULES:
                continue
            modules.add(module)
    return modules


def test_all_third_party_imports_are_declared_dependencies():
    missing = imported_third_party_modules() - declared_dependency_modules()
    assert not missing, (
        f"Modules imported by proof_sdk but missing from [project] dependencies: {sorted(missing)}"
    )
