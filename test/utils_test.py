from utils import filter_internal_keys

d = {
    "_foo": True,
    "foo": 1
}


def test_filter_keys():
    o = filter_internal_keys(d)
    assert o['foo'] == True
    assert '_foo' not in o.keys()
