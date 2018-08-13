
def filter_props(d: dict) -> dict:
    filtered = {}
    for key, value in d.items():
        if key[0] != '_' and value is not None:
            filtered[key] = value

    return filtered