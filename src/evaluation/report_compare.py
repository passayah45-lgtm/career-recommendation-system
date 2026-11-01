# Compares two experiment reports with a numeric tolerance
# Trained models can differ in the last rounded digit between machines (CPU-specific BLAS kernels),
# so CI compares ML reports within a small tolerance; local --check without a tolerance stays byte-exact


def report_differences(saved, fresh, tolerance, path="$"):
    # Returns a list of "path: saved != fresh" strings; numbers may differ by at most tolerance
    if isinstance(saved, bool) or isinstance(fresh, bool):
        return [] if saved == fresh else [f"{path}: {saved!r} != {fresh!r}"]
    if isinstance(saved, (int, float)) and isinstance(fresh, (int, float)):
        return [] if abs(saved - fresh) <= tolerance else [f"{path}: {saved!r} != {fresh!r}"]
    if isinstance(saved, dict) and isinstance(fresh, dict):
        if set(saved) != set(fresh):
            return [f"{path}: keys differ ({sorted(set(saved) ^ set(fresh))})"]
        out = []
        for key in saved:
            out += report_differences(saved[key], fresh[key], tolerance, f"{path}.{key}")
        return out
    if isinstance(saved, list) and isinstance(fresh, list):
        if len(saved) != len(fresh):
            return [f"{path}: length {len(saved)} != {len(fresh)}"]
        out = []
        for i, (a, b) in enumerate(zip(saved, fresh)):
            out += report_differences(a, b, tolerance, f"{path}[{i}]")
        return out
    return [] if saved == fresh else [f"{path}: {saved!r} != {fresh!r}"]
