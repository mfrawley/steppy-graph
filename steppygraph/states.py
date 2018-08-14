import json
from enum import Enum
from typing import List
from functools import singledispatch

from steppygraph.utils import filter_props

ERROR_MAX_ATTEMPTS_DEFAULT = 2
ERROR_BACKOFF_RATE_DEFAULT = 1.5
ERROR_INTERVAL_S_DEFAULT = 60
JSON_INDENT = 4
DEFAULT_TASK_TIMEOUT = 600
DEFAULT_WAIT_PERIOD = 60


class ErrorType(Enum):
    ALL = "States.ALL"
    TIMEOUT = "States.Timeout"
    TASK_FAILED = "States.TaskFailed"
    PERMISSIONS = "States.Permissions"
    RESULT_PATH_MATCH_FAILURE = "States.ResultPathMatchFailure"
    BRANCH_FAILED = "States.BranchFailed"
    NO_CHOICE_MATCHED = "States.NoChoiceMatched"

    def __str__(self):
        return self.value

class StateType(Enum):
    TASK = 'Task'
    PASS = 'Pass'
    WAIT = 'Wait'
    CHOICE = 'Choice'

    def __str__(self):
        return self.value


class ResourceType(Enum):
    LAMBDA = 'lambda'
    ACTIVITY = 'activity'

    def __str__(self):
        return self.value


class ComparisonType(Enum):
    BOOLEAN_EQ = "BooleanEquals"
    NUMERIC_EQ = "NumericEquals"
    NUMERIC_LT = "NumericLessThan"
    NUMERIC_LT_EQ = "NumericLessThanEquals"
    NUMERIC_GT = "NumericGreaterThan"
    NUMERIC_GT_EQ = "NumericGreaterThanEquals"

    STRING_EQ = "StringEquals"
    STRING_LT = "StringLessThan"
    STRING_GT = "StringGreaterThan"
    STRING_LT_EQ = "StringLessThanEquals"
    STRING_GT_EQ = "StringGreaterThanEquals"

    TS_EQ = "TimestampEquals"
    TS_LT = "TimestampLessThan"
    TS_GT = "TimestampGreaterThan"
    TS_LT_EQ = "TimestampLessThanEquals"
    TS_GT_EQ = "TimestampGreaterThanEquals"

    def __str__(self):
        return self.value


class LogicalOperatorType(Enum):
    AND = "And"
    OR = "Or"
    NOT = "Not"

    def __str__(self):
        return self.value


@singledispatch
def to_serializable(val):
    """Used by default."""
    return str(val)


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


@to_serializable.register(Resource)
def resource_to_json(val) -> str:
    """Used if *val* is an instance of Resource."""
    return str(val)


class StateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, State):
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
                 name: str,
                 type: StateType,
                 comment: str = '') -> None:
        self.Type = type
        self.End = False
        self.Comment = comment
        self._name = name
        self.InputPath = None
        self.OutputPath = None
        self.Next = None

    def name(self) -> str:
        return self._name


@to_serializable.register(State)
def state_to_json(val: State) -> dict:
    val.Type = val.Type.value
    if val.Next is None:
        del val.Next
    return filter_props(val.__dict__)


@to_serializable.register(Resource)
def json_resource(val) -> str:
    """Used if *val* is an instance of Resource."""
    return str(val)


class Task(State):
    def __init__(self,
                 name: str,
                 resource: Resource,
                 comment: str = '',
                 ) -> None:
        State.__init__(self, type=StateType.TASK, name=name, comment=comment)
        self.Resource: str = str(resource)
        self.ResultPath = None
        self.Retry: List[Retrier] = None
        self.Catch = None
        self.TimeoutSeconds = DEFAULT_TASK_TIMEOUT
        self.HeartbeatSeconds = None


class Retrier:
    def __init__(self, max_attempts=ERROR_MAX_ATTEMPTS_DEFAULT,
                 backoff_rate=ERROR_BACKOFF_RATE_DEFAULT,
                 interval_seconds=ERROR_INTERVAL_S_DEFAULT,
                 error_equals:ErrorType=[ErrorType.ALL]) -> None:
        self.BackoffRate = backoff_rate
        self.MaxAttempts = max_attempts
        self.IntervalSeconds = interval_seconds
        self.ErrorEquals = error_equals


class Pass(State):
    def __init__(self,
                 name: str,
                 result: dict = None,
                 result_path: str = None,
                 comment: str = ''
                 ):
        State.__init__(self, type=StateType.PASS, name=name, comment=comment)
        self.ResultPath = result_path
        self.Result = result


class Wait(State):
    def __init__(self,
                 name: str,
                 seconds: int = DEFAULT_TASK_TIMEOUT,
                 comment: str = ''
                 ):
        State.__init__(self, type=StateType.WAIT, name=name, comment=comment)
        self.Seconds = seconds


class Comparison:
    def __init__(self, comparison_type: ComparisonType, value: object) -> None:
        self._comparison_type = comparison_type
        self._value = value

    def type(self) -> str:
        return self._comparison_type.value

    def value(self) -> object:
        return self._value


class ChoiceCase:
    def __init__(self,
                 variable: str,
                 comparison: Comparison,
                 next: State) -> None:
        self.Variable = variable
        self._comparison = comparison
        self.Next = next.name()


@to_serializable.register(ChoiceCase)
def state_to_json(val: ChoiceCase) -> dict:
    d = val.__dict__
    d[val._comparison.type()] = val._comparison.value()
    return filter_props(d)


class Choice(State):
    def __init__(self,
                 name: str,
                 choices: List[ChoiceCase],
                 default: State,
                 comment: str = ''
                 ) -> None:
        State.__init__(self, type=StateType.CHOICE, name=name, comment=comment)
        self.Choices = choices
        self.Default = default.name()


# @to_serializable.register(Choice)
# def state_to_json(val: Choice) -> dict:
#     d = val.__dict__
#     d[val._comparison.type()] = val._comparison.value()
#     return filter_props(d)


if __name__ == "__main__":
    t = Task(resource="some", name="Kermit", comment='Foo')
    print(t.to_json())
