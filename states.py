import json
from enum import Enum

from utils import filter_internal_keys

JSON_INDENT = 4


class StateType(Enum):
    TASK = 'Task'


class ResourceType(Enum):
    LAMBDA = 'lambda'
    ACTIVITY = 'activity'


class Resource:
    def __init__(self,
                 name: str,
                 type: ResourceType,
                 region: str = '',
                 aws_ac: str = ''):
        self.resource_type = type
        self.name = name
        self.region = region
        self.aws_ac = aws_ac

    def __str__(self) -> str:
        if self.resource_type == ResourceType.LAMBDA:
            return f"arn:aws:lambda:{self.region}:{self.aws_ac}:function:{self.name}"
        else:
            return f"arn:aws:states:{self.region}:{self.aws_ac}:activity:{self.name}"


class StateEncoder(json.JSONEncoder):
    def default(self, obj):
        print("isinstance(obj, StateType)", obj, isinstance(obj, Task))
        if isinstance(obj, Task):
            obj.Type = obj.Type.value
            if obj.Next is None:
                del obj.Next
            return filter_internal_keys(obj.__dict__)
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
                 resource: Resource,
                 name: str,
                 comment: str = '',
                 ) -> None:
        State.__init__(self, type=StateType.TASK, name=name, comment=comment)
        self.Resource: str = str(resource)
        self.Next = None


if __name__ == "__main__":
    t = Task(resource="some", name="Kermit", comment='Foo')
    print(t.to_json())
