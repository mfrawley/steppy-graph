from steppygraph.utils import filter_props

d = {
    "_foo": True,
    "foo": 1
}


def test_filter_keys():
    o = filter_props(d)
    assert o['foo'] == True
    assert '_foo' not in o.keys()
