from pathlib import PurePath


def write_json_test_case(name: str, s: object) -> None:
    with open(PurePath() / f'steppygraph/test/json/{name}.json', 'w+') as f:
        f.write(s.to_json())


def read_json_test_case(name: str) -> str:
    with open(PurePath() / f'steppygraph/test/json/{name}.json', 'r') as f:
        return f.read()
