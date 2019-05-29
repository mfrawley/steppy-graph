import json
from typing import List, Optional, Dict, Any

from enum import Enum

from steppygraph.serialize import to_serializable
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
    PARALLEL = 'Parallel'
    SUCCEED = 'Succeed'
    FAIL = 'Fail'

    def __str__(self):
        return self.value


class ResourceType(Enum):
    LAMBDA = 'lambda'
    ACTIVITY = 'activity'
    BATCH = 'batch'
    ECS = 'ecs'

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


class Resource:
    def __init__(self,
                 name: str,
                 type: ResourceType,
                 region: str = '',
                 aws_ac: str = '') -> None:
        self.resource_type = type
        self.name = name
        self.region = region
        self.aws_ac = aws_ac

    def __str__(self) -> str:
        if self.resource_type == ResourceType.LAMBDA:
            return f"arn:aws:lambda:{self.region}:{self.aws_ac}:function:{self.name}"
        elif self.resource_type == ResourceType.BATCH:
            return f"arn:aws:states:{self.region}:{self.aws_ac}:batch:submitJob.sync"
        elif self.resource_type == ResourceType.ECS:
            return f"arn:aws:states:{self.region}:{self.aws_ac}:ecs:runTask.sync"
        else:
            return f"arn:aws:states:{self.region}:{self.aws_ac}:activity:{self.name}"


@to_serializable.register(Resource)
def resource_to_json(val) -> str:
    """Used if *val* is an instance of Resource."""
    return str(val)


class State:
    def __init__(self,
                 name: str,
                 type: StateType,
                 comment: str = None) -> None:
        self.Type = type.value
        self.End: Optional[bool] = None
        self.Comment = comment
        self._name = name
        self.InputPath = None
        self.OutputPath = None
        self._next: Optional[str] = None
        self._autoconnect = False

    def name(self) -> str:
        return self._name

    def build(self):
        if self._next:
            self.Next = self._next
        return self

    def to_json(self):
        return json.dumps(self,
                          default=to_serializable,
                          sort_keys=True,
                          indent=JSON_INDENT)

    def set_next(self, next: str):
        """
        Note - Next property can only be set once, after that it is readonly
        :param next: name of the subsequent state
        """
        if not type(next) == str:
            raise ValueError("Next should be a string")

        if self._next is None:
            self._next = next

    def get_next(self) -> Optional[str]:
        return self._next


@to_serializable.register(State)
def state_to_json(val: State) -> dict:
    # val.Type = val.Type.value
    return filter_props(val.build().__dict__)


class Catcher:
    def __init__(self, error_equals: List[ErrorType], next: State) -> None:
        self.ErrorEquals = error_equals
        self._next = next

    def build(self):
        self.Next = self._next.name()
        return self


@to_serializable.register(Catcher)
def catcher_to_json(val: Catcher) -> dict:
    return filter_props(val.build().__dict__)


class Retrier:
    def __init__(self,
                 max_attempts=ERROR_MAX_ATTEMPTS_DEFAULT,
                 backoff_rate=ERROR_BACKOFF_RATE_DEFAULT,
                 interval_seconds=ERROR_INTERVAL_S_DEFAULT,
                 error_equals: List[ErrorType] = [ErrorType.ALL]) -> None:
        self.BackoffRate = backoff_rate
        self.MaxAttempts = max_attempts
        self.IntervalSeconds = interval_seconds
        self.ErrorEquals = error_equals


@to_serializable.register(Retrier)
def retrier_to_json(val: Retrier) -> dict:
    d = val.__dict__
    return d


class Task(State):
    def __init__(self,
                 name: str,
                 resource: Resource = None,
                 comment: str = None,
                 retry: List[Retrier] = None,
                 catch: List[Catcher] = None,
                 timeout_seconds: int = DEFAULT_TASK_TIMEOUT
                 ) -> None:
        State.__init__(self, type=StateType.TASK, name=name, comment=comment)
        if not isinstance(resource, Resource):
            raise ValueError(
                "resource must be an instance of the type Resource")
        self.Resource = resource
        self.ResultPath = None
        self.Retry = retry
        self.Catch = catch
        self.TimeoutSeconds = timeout_seconds
        self.HeartbeatSeconds = None


class ContainerOverrides:
    def __init__(self,
                 command: Optional[str] = None,
                 environment: Optional[str] = None,
                 instance_type: Optional[str] = None,
                 memory: Optional[int] = None,
                 resource_requirements: Optional[list] = None,
                 vcpus: Optional[int] = None
                 ) -> None:
        if command:
            self.Command = command

        if environment:
            self.Environment = environment

        if instance_type:
            self.InstanceType = instance_type

        if memory:
            self.Memory = memory

        if resource_requirements:
            self.ResourceRequirements = resource_requirements

        if vcpus:
            self.Vcpus = vcpus


@to_serializable.register(ContainerOverrides)
def containeroverrides_to_json(val: ContainerOverrides) -> dict:
    return filter_props(val.__dict__)


class BatchJob(Task):
    def __init__(self,
                 name: str,
                 definition: str,
                 queue: str,
                 parameters: str = None,
                 comment: str = None,
                 retry: List[Retrier] = None,
                 catch: List[Catcher] = None,
                 timeout_seconds: int = DEFAULT_TASK_TIMEOUT,
                 container_overrides: Optional[ContainerOverrides] = None
                 ) -> None:
        Task.__init__(self,
                      name=name,
                      resource=Resource(name=name, type=ResourceType.BATCH),
                      comment=comment,
                      retry=retry,
                      catch=catch,
                      timeout_seconds=timeout_seconds)
        self.Parameters: Dict[str, Any] = {
            "JobDefinition": definition,
            "JobName": name,
            "JobQueue": queue
        }

        if container_overrides:
            self.Parameters["ContainerOverrides"] = container_overrides

        if parameters is not None:
            self.Parameters["Parameters.$"] = parameters


@to_serializable.register(BatchJob)
def batchjob_to_json(val: BatchJob) -> dict:
    return filter_props(val.__dict__)


class EcsTask(Task):
    def __init__(self,
                 name: str,
                 cluster: str,
                 definition: str,
                 launch_type: str,
                 network_configuration: dict = {},
                 overrides: dict = {},
                 comment: str = None,
                 retry: List[Retrier] = None,
                 catch: List[Catcher] = None,
                 timeout_seconds: int = DEFAULT_TASK_TIMEOUT
                 ) -> None:
        Task.__init__(self,
                      name=name,
                      resource=Resource(name=name, type=ResourceType.ECS),
                      comment=comment,
                      retry=retry,
                      catch=catch,
                      timeout_seconds=timeout_seconds)
        self.Parameters = {
            "Cluster": cluster,
            "LaunchType": launch_type,
            "TaskDefinition": definition,
            "NetworkConfiguration": network_configuration,
            "Overrides": overrides
        }


class Pass(State):
    def __init__(self,
                 name: str,
                 result: dict = None,
                 result_path: str = None,
                 comment: str = None
                 ) -> None:
        State.__init__(self, type=StateType.PASS, name=name, comment=comment)
        self.ResultPath = result_path
        self.Result = result


class Wait(State):
    def __init__(self,
                 name: str,
                 seconds: int = DEFAULT_TASK_TIMEOUT,
                 comment: str = None
                 ) -> None:
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
def choicecase_to_json(val: ChoiceCase) -> dict:
    d = val.__dict__
    d[val._comparison.type()] = val._comparison.value()
    return filter_props(d)


class Choice(State):
    def __init__(self,
                 name: str,
                 choices: List[ChoiceCase],
                 default: State,
                 comment: str = None
                 ) -> None:
        State.__init__(self, type=StateType.CHOICE, name=name, comment=comment)
        self.Choices = choices
        self.Default = default.name()


class Succeed(State):
    def __init__(self, name: str) -> None:
        State.__init__(self, type=StateType.SUCCEED, name=name)


@to_serializable.register(Succeed)
def succeed_to_json(val: Succeed) -> dict:
    return filter_props(val.__dict__)


class Fail(State):
    def __init__(self, name: str, cause: str = "", error: str = "") -> None:
        State.__init__(self, type=StateType.FAIL, name=name)
        self.Cause = cause
        self.Error = error


@to_serializable.register(Fail)
def fail_to_json(val: Fail) -> dict:
    return filter_props(val.__dict__)
