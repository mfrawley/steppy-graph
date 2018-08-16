import json
from typing import List, Dict

from steppygraph.states import State, JSON_INDENT, Task, ResourceType, Resource, Wait, Pass, StateType
from steppygraph.utils import filter_props
from steppygraph.serialize import to_serializable


class DuplicateStateError(Exception):
    pass


class StateMachine:
    def __init__(self,
                 region: str = '',
                 account: str = '',
                 name='') -> None:
        self.TimeoutSeconds = 600
        self.States: Dict[str, State] = {}
        self.StartAt: str = None
        self._states: List[State] = []
        self._region = region
        self._account = account
        self._name = name

    def to_json(self) -> str:
        return json.dumps(self,
                          sort_keys=True,
                          indent=JSON_INDENT,
                          default=to_serializable)

    def next(self, state: State) -> object:
        """
        This method appends a State to the task graph and does some magic to help init certain types
        of States.
        """
        for s in self._states:
            if s.name() == state.name():
                err_message = f"Duplicate State: Name '{s.name()}' already used in graph."
                raise DuplicateStateError(err_message)

        if len(self._states) > 0:
            self._states[-1]._next = state.name()

        self.set_resource_attrs(state)
        self._states.append(state)
        return self

    def set_resource_attrs(self, state):
        """
        If the State is a Task and has a resource set, set the metadata to auto-fill aws ac and region
        :param state:
        :return:
        """
        if isinstance(state, Task):
            if state.Resource:
                state.Resource.aws_ac = self._account
                state.Resource.region = self._region

    def build(self) -> object:
        d = {}
        states_len = len(self._states)
        for i in range(0, states_len):
            s = self._states[i]
            s.build()
            if i == 0:
                self.StartAt = s.name()

            if i == states_len - 1:
                s.End = True
            d[s.name()] = s
        self.States = d
        return self

    def get_states(self) -> List[State]:
        return self._states

    def count_states(self) -> int:
        return len(self._states)

    def printable(self) -> str:
        return ' '.join([str(s.__dict__) for k, s in self.build().States.items()])

    def name(self) -> str:
        return self._name


@to_serializable.register(StateMachine)
def machine_to_json(obj) -> str:
    for k, s in obj.States.items():
        obj.States[k] = s
    return filter_props(obj.__dict__)


class Branch(StateMachine):
    def __init__(self,
                 region: str = '',
                 account: str = '',
                 name=''):
        StateMachine.__init__(self, region=region, account=account, name=name)


class Parallel(State):
    def __init__(self,
                 name: str,
                 branches: List[Branch],
                 comment: str = None
                 ) -> None:
        State.__init__(self, type=StateType.PARALLEL, name=name, comment=comment)
        self.Branches = branches

    def build(self) -> object:
        for b in self.Branches:
            b.build()
        return self

# @to_serializable.register(Parallel)
# def parallel_to_json(obj) -> str:
#     for k, s in obj.States.items():
#         obj.States[k] = s
#     return filter_props(obj.__dict__)
