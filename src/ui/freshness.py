# Guards against stale modules after a hot update
# Streamlit Community Cloud pulls new code without restarting Python, so already imported
# src modules can stay old while page scripts are new, which raises ImportError
# app.py calls drop_stale_modules() before importing anything else from src, and
# remember_loaded_modules() after each run, so modules first imported by a page get a baseline too

import os
import sys

_SEEN = {}
# True until the first check in this process, see drop_stale_modules
_FIRST_CHECK = [True]


def _mtime(module):
    path = getattr(module, "__file__", None)
    if not path:
        return None
    try:
        return os.stat(path).st_mtime_ns
    except OSError:
        return None


def _changed_since_compiled(module):
    # The cached .pyc header stores the source file time used when the module was loaded
    # A different time on disk now means the file changed after loading; unknown counts as unchanged
    cached = getattr(module, "__cached__", None)
    path = getattr(module, "__file__", None)
    if not cached or not path:
        return False
    try:
        with open(cached, "rb") as handle:
            header = handle.read(16)
        source_time = int(os.stat(path).st_mtime) & 0xFFFFFFFF
    except OSError:
        return False
    if len(header) < 16 or int.from_bytes(header[4:8], "little") != 0:
        return False
    return int.from_bytes(header[8:12], "little") != source_time


def remember_loaded_modules(prefix="src."):
    # Records the file time of every loaded module not seen yet, keeping earlier baselines
    for name, module in list(sys.modules.items()):
        if name.startswith(prefix) and name != __name__:
            mtime = _mtime(module)
            if mtime is not None:
                _SEEN.setdefault(name, mtime)


def drop_stale_modules(prefix="src."):
    # Returns True when a source file changed since it was first seen, after removing the changed
    # package's plain modules from sys.modules so the next import reads the new files
    stale = False
    first = _FIRST_CHECK[0]
    _FIRST_CHECK[0] = False
    for name, module in list(sys.modules.items()):
        if not name.startswith(prefix) or name == __name__:
            continue
        mtime = _mtime(module)
        if mtime is None:
            continue
        if first and getattr(module, "__path__", None) is None and _changed_since_compiled(module):
            # First check in this process, before any baseline exists: a module whose file changed
            # after it was loaded is stale, for example when the hot update brought in this guard
            stale = True
        elif _SEEN.setdefault(name, mtime) != mtime:
            stale = True
    if stale:
        for name in [n for n in sys.modules if n.startswith(prefix) and n != __name__]:
            # Packages stay loaded, their submodules are imported again on demand
            if getattr(sys.modules[name], "__path__", None) is None:
                del sys.modules[name]
        for name in [n for n in _SEEN if n.startswith(prefix)]:
            del _SEEN[name]
    return stale
