import json
from pathlib import PurePath

from steppygraph.serialize import to_serializable


def write_json_test_case(name: str, s: object) -> None:
    with open(PurePath() / f'steppygraph/test/json/{name}.json', 'w+') as f:
        if type(s) == str:
            f.write(s)
        else:
            f.write(json.dumps(s, default=to_serializable))


def read_json_test_case(name: str) -> str:
    with open(PurePath() / f'steppygraph/test/json/{name}.json', 'r') as f:
        return f.read()
