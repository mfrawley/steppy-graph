
def filter_internal_keys(d: dict) -> dict:
    filtered = {}
    for key, value in d.items():
        if key[0] != '_':
            filtered[key] = value

    return filtered