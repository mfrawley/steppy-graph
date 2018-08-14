import json
from typing import List

from steppygraph.states import State, JSON_INDENT, Task, StateEncoder, ResourceType, Resource, Wait, Pass
from steppygraph.utils import filter_props

class DuplicateStateError(Exception):
    pass

class StateMachine:
    def __init__(self, region:str='', account:str='') -> None:
        self.TimeoutSeconds = 600
        self.States: List[State] = None
        self.StartAt: str = None
        self._states: List[State] = []
        self._region = region
        self._account = account

    def to_json(self) -> str:
        return json.dumps(self,
                          sort_keys=True,
                          # skip_keys=True,
                          indent=JSON_INDENT,
                          cls=StateMachineEncoder)

    def next(self, state: State) -> object:
        """
        This method
        """
        for s in self._states:
            if s.name() == state.name():
                err_message = f"Duplicate State: Name '{s.name()}' already used in graph."
                raise DuplicateStateError(err_message)

        if len(self._states) > 0:
            self._states[-1].Next = state.name()
        self._states.append(state)
        return self

    def build(self) -> object:
        d = {}
        states_len = len(self._states)
        for i in range(0, states_len):
            s = self._states[i]
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


class StateMachineEncoder(json.JSONEncoder):
    def default(self, obj):
        print(type(obj))
        if isinstance(obj, StateMachine):
            for k, s in obj.States.items():
                obj.States[k] = StateEncoder().default(s)
            return filter_props(obj.__dict__)


        try:
            return super(StateMachineEncoder, self).default(obj)
        except Exception as e:
            print(e)
            print(obj.__dict__)


if __name__ == "__main__":
    s = StateMachine()
    res = Resource(name="foores", type=ResourceType.LAMBDA)
    s.next(Task(resource=res, name="Kermit", comment='Foo'))
    s.next(Wait(name="Waiting time", comment='Foo', seconds=2))
    s.next(Pass(name="Pass the buck"))
    s.next(Task(resource=res, name="Miss Piggy", comment='Foo'))
    s.build()
    
    print(s.to_json())
