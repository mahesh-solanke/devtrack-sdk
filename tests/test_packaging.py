import ast
import builtins
import importlib
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_PACKAGES = {"django", "fastapi", "starlette", "httpx"}


def _requirement_name(requirement: str) -> str:
    match = re.match(r"[A-Za-z0-9_.-]+", requirement)
    assert match, f"Invalid requirement: {requirement}"
    return match.group(0).lower().replace("_", "-")


def _requirement_names(requirements: list[str]) -> set[str]:
    return {_requirement_name(requirement) for requirement in requirements}


def test_pyproject_keeps_frameworks_optional():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())

    core_dependencies = _requirement_names(pyproject["project"]["dependencies"])
    optional_dependencies = pyproject["project"]["optional-dependencies"]
    classifiers = set(pyproject["project"]["classifiers"])

    assert FRAMEWORK_PACKAGES.isdisjoint(core_dependencies)
    assert optional_dependencies["django"] == ["django>=4.0.0"]
    assert optional_dependencies["fastapi"] == ["fastapi>=0.90"]
    assert {"fastapi", "django"}.issubset(
        _requirement_names(optional_dependencies["all"])
    )
    assert "Framework :: Django :: 4.2" in classifiers
    assert "Framework :: Django :: 5.2" in classifiers


def test_setup_py_keeps_frameworks_optional():
    setup_tree = ast.parse((ROOT / "setup.py").read_text())
    setup_call = next(
        node
        for node in ast.walk(setup_tree)
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "setup"
    )
    setup_kwargs = {keyword.arg: keyword.value for keyword in setup_call.keywords}

    install_requires = ast.literal_eval(setup_kwargs["install_requires"])
    extras_require = ast.literal_eval(setup_kwargs["extras_require"])
    classifiers = ast.literal_eval(setup_kwargs["classifiers"])

    assert FRAMEWORK_PACKAGES.isdisjoint(_requirement_names(install_requires))
    assert extras_require["django"] == ["django>=4.0.0"]
    assert extras_require["fastapi"] == ["fastapi>=0.90"]
    assert {"fastapi", "django"}.issubset(_requirement_names(extras_require["all"]))
    assert "Framework :: Django :: 4.2" in classifiers
    assert "Framework :: Django :: 5.2" in classifiers


def test_top_level_import_does_not_require_frameworks(monkeypatch):
    for module_name in list(sys.modules):
        if module_name == "devtrack_sdk" or module_name.startswith("devtrack_sdk."):
            del sys.modules[module_name]

    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        package_name = name.split(".", 1)[0]
        if package_name in {"django", "fastapi", "starlette"}:
            raise AssertionError(f"Unexpected framework import: {name}")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    package = importlib.import_module("devtrack_sdk")

    assert package.__version__
