# Stale-module guard: a changed source file is imported again, unchanged files and packages stay

import importlib
import os
import sys

import src.ui.freshness as freshness
from src.ui.freshness import drop_stale_modules, remember_loaded_modules


def make_package(tmp_path, monkeypatch, name):
    pkg = tmp_path / name
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "mod.py").write_text("def old():\n    return 1\n", encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setattr(freshness, "_FIRST_CHECK", [False])
    return pkg


def test_unchanged_modules_are_kept(tmp_path, monkeypatch):
    make_package(tmp_path, monkeypatch, "probe_same")
    importlib.import_module("probe_same.mod")
    assert drop_stale_modules("probe_same.") is False
    assert drop_stale_modules("probe_same.") is False
    assert "probe_same.mod" in sys.modules


def test_changed_module_is_reloaded_with_new_names(tmp_path, monkeypatch):
    pkg = make_package(tmp_path, monkeypatch, "probe_changed")
    mod = importlib.import_module("probe_changed.mod")
    assert drop_stale_modules("probe_changed.") is False
    # Simulate a git pull that adds a new function, as in the Community Cloud hot update
    (pkg / "mod.py").write_text("def old():\n    return 1\n\ndef new():\n    return 2\n", encoding="utf-8")
    stat = os.stat(mod.__file__)
    os.utime(mod.__file__, ns=(stat.st_atime_ns, stat.st_mtime_ns + 5_000_000_000))
    importlib.invalidate_caches()
    assert drop_stale_modules("probe_changed.") is True
    assert "probe_changed.mod" not in sys.modules
    from probe_changed.mod import new
    assert new() == 2
    assert drop_stale_modules("probe_changed.") is False


def test_module_imported_after_the_guard_still_gets_a_baseline(tmp_path, monkeypatch):
    # The real failure: the guard ran before the page imported the module, then the file changed
    pkg = make_package(tmp_path, monkeypatch, "probe_late")
    assert drop_stale_modules("probe_late.") is False
    mod = importlib.import_module("probe_late.mod")
    remember_loaded_modules("probe_late.")
    (pkg / "mod.py").write_text("def new():\n    return 3\n", encoding="utf-8")
    stat = os.stat(mod.__file__)
    os.utime(mod.__file__, ns=(stat.st_atime_ns, stat.st_mtime_ns + 5_000_000_000))
    importlib.invalidate_caches()
    assert drop_stale_modules("probe_late.") is True
    from probe_late.mod import new
    assert new() == 3


def bump(path, text):
    # Rewrite a source file and move its time forward, as a git pull would
    path.write_text(text, encoding="utf-8")
    stat = os.stat(path)
    os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns + 5_000_000_000))
    importlib.invalidate_caches()


def test_first_check_reloads_modules_changed_after_loading(tmp_path, monkeypatch):
    # The guard arrives with a hot update while old modules are already in memory
    pkg = make_package(tmp_path, monkeypatch, "probe_first")
    importlib.import_module("probe_first.mod")
    bump(pkg / "mod.py", "def new():\n    return 4\n")
    monkeypatch.setattr(freshness, "_FIRST_CHECK", [True])
    assert drop_stale_modules("probe_first.") is True
    assert "probe_first.mod" not in sys.modules and "probe_first" in sys.modules
    from probe_first.mod import new
    assert new() == 4


def test_first_check_keeps_unchanged_modules(tmp_path, monkeypatch):
    # A normal start, where modules were loaded before the guard but nothing changed
    make_package(tmp_path, monkeypatch, "probe_clean")
    importlib.import_module("probe_clean.mod")
    monkeypatch.setattr(freshness, "_FIRST_CHECK", [True])
    assert drop_stale_modules("probe_clean.") is False
    assert "probe_clean.mod" in sys.modules
