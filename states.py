import json
from enum import Enum

JSON_INDENT = 4


class StateType(Enum):
    TASK = 'Task'


class StateEncoder(json.JSONEncoder):
    def default(self, obj):
        print("isinstance(obj, StateType)", obj, isinstance(obj, Task))
        if isinstance(obj, Task):
            del obj._name
            obj.Type = obj.Type.value
            if obj.Next is None:
                del obj.Next
            return obj.__dict__
        try:
            return super(StateEncoder, self).default(obj)
        except AttributeError as e:
            print(obj.__dict__)
            print(e)
        except TypeError as e:
            print(obj.__dict__)
            print(e)


class JsonSerializable:
    def to_json(self) -> str:
        return json.dumps(self,
                          sort_keys=True,
                          indent=JSON_INDENT,
                          cls=StateEncoder)


class State(JsonSerializable):
    def __init__(self,
                 type: StateType,
                 name: str,
                 comment: str = '') -> None:
        self.Type = type
        self.End = False
        self.Comment = comment
        self._name = name

    def name(self) -> str:
        return self._name


class Task(State):
    def __init__(self,
                 resource: str,
                 name: str,
                 comment: str = '',
                 ) -> None:
        State.__init__(self, type=StateType.TASK, name=name, comment=comment)
        self.Resource = resource
        self.Next = None


if __name__ == "__main__":
    t = Task(resource="some", name="Kermit", comment='Foo')
    print(t.to_json())
