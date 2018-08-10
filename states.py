import json
from enum import Enum
from typing import List

from utils import filter_props

ERROR_MAX_ATTEMPTS_DEFAULT = 2

ERROR_BACKOFF_RATE_DEFAULT = 1.5

ERROR_INTERVAL_S_DEFAULT = 60


class ErrorStates(Enum):
    ALL = "States.ALL"
    TIMEOUT = "States.Timeout"


JSON_INDENT = 4
DEFAULT_TASK_TIMEOUT = 600


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
            return filter_props(obj.__dict__)
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
        self.ResultPath = None
        self.Retry: List[Retry] = None
        self.Catch = None
        self.TimeoutSeconds = DEFAULT_TASK_TIMEOUT
        # self.HeartbeatSeconds


# {
#         "ErrorEquals": [ "States.Timeout" ],
#         "IntervalSeconds": 3,
#         "MaxAttempts": 2,
#         "BackoffRate": 1.5
#     }
class Retry:
    def __init__(self, max_attempts=ERROR_MAX_ATTEMPTS_DEFAULT,
                 backoff_rate=ERROR_BACKOFF_RATE_DEFAULT,
                 interval_seconds=ERROR_INTERVAL_S_DEFAULT,
                 error_equals=[ErrorStates.ALL]) -> None:
        self.BackoffRate = backoff_rate
        self.MaxAttempts = max_attempts
        self.IntervalSeconds = interval_seconds
        self.ErrorEquals = error_equals


if __name__ == "__main__":
    t = Task(resource="some", name="Kermit", comment='Foo')
    print(t.to_json())
