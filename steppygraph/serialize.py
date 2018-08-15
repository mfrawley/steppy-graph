from functools import singledispatch

@singledispatch
def to_serializable(val):
    """Used by default."""
    return str(val)
