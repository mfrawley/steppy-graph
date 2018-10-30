import json
from typing import List, Dict, TypeVar, Any, Optional, Tuple

from steppygraph.states import State, JSON_INDENT, Task, ResourceType, Resource, Wait, Pass, StateType, Catcher
from steppygraph.utils import filter_props
from steppygraph.serialize import to_serializable

TERMINAL_STATES = (StateType.FAIL, StateType.SUCCEED)


class DuplicateStateError(Exception):
    pass


class StateMachine:
    def __init__(self,
                 region: str = '',
                 account: str = '',
                 name='') -> None:
        self.TimeoutSeconds = 600
        self.States: Dict[str, State] = {}
        self.StartAt: Optional[str] = None
        self._states: List[State] = []
        self._region = region
        self._account = account
        self._name = name
        self.End: Optional[bool] = None

    def to_json(self) -> str:
        return json.dumps(self,
                          sort_keys=True,
                          indent=JSON_INDENT,
                          default=to_serializable)  # type: ignore

    def idx(self, name: str) -> Optional[int]:
        """
        Returns index of the first state in the graph with a matching name
        :param name:
        :return: index
        """
        for i in range(0, len(self._states)):
            s = self._states[i]
            if name == s.name():
                return i
        return None

    def last_orphan(self) -> Optional[int]:
        """
        Returns index of the most recently added state which is neither a terminal state nor has a Next attribute set.
        :param name:
        :return: index
        """
        # traverse the list backwards
        for index in range(len(self._states) - 1, -1, -1):
            s = self._states[index]
            if s._autoconnect is True and s.Type not in TERMINAL_STATES and s._next is None:
                return index
        return None

    def next(self, state: State) -> object:
        """
        This method adds a State to the task graph via add_state but it also
        sets the Next property of the previously added state to point to it for convenience.
        """
        state._autoconnect = True

        if len(self._states) > 0:
            orphan_idx = self.last_orphan()
            if orphan_idx is not None:
                s = self._states[orphan_idx]
                if s._autoconnect:
                    s.set_next(state.name())

        return self.add_state(state)

    def add_state(self, state: State) -> object:
        """
        This method appends a State to the task graph but does NOT affect the Next property.
        Useful when adding states which are out of sequence.
        """
        for s in self._states:
            if s.name() == state.name():
                err_message = f"Duplicate State: Name '{s.name()}' already used in graph. {[ss.name() for ss in self._states]}"
                raise DuplicateStateError(err_message)

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

    def build(self) -> Any:
        d = {}
        states_len = len(self._states)
        for i in range(0, states_len):
            s = self._states[i]

            if i == 0:
                self.StartAt = s.name()

            if i == states_len - 1:
                if s.Type not in [ts.value for ts in TERMINAL_STATES]:
                    s.End = True
            d[s.name()] = s.build()
        self.States = d
        return self

    def get_states(self) -> List[State]:
        return self._states

    def count_states(self) -> int:
        return len(self._states)

    def printable(self) -> str:
        return ' '.join([str(s.__dict__) for k, s in self.build().States.items()])

    def last(self) -> State:
        return self._states[-1]

    def name(self) -> str:
        return self._name


@to_serializable.register(StateMachine)
def machine_to_json(obj) -> Dict[str, Any]:
    for k, s in obj.States.items():
        obj.States[k] = s
    return filter_props(obj.__dict__)


class Branch(StateMachine):
    def __init__(self,
                 region: str = '',
                 account: str = '',
                 name='') -> None:
        StateMachine.__init__(self, region=region, account=account, name=name)
        del self.TimeoutSeconds


class Parallel(State):
    def __init__(self,
                 name: str,
                 branches: List[Branch],
                 comment: str = None,
                 catch: List[Catcher] = None
                 ) -> None:
        State.__init__(self, type=StateType.PARALLEL, name=name, comment=comment)
        self._catch = catch
        self.Branches = branches

    def build(self) -> object:
        if self._catch:
            self.Catch = self._catch

        for b in self.Branches:
            b.build()
        return self

# @to_serializable.register(Parallel)
# def parallel_to_json(obj) -> str:
#     for k, s in obj.States.items():
#         obj.States[k] = s
#     return filter_props(obj.__dict__)
