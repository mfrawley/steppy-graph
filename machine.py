import json
from typing import List

from states import State, JSON_INDENT, Task, StateEncoder


class StateMachine:
    def __init__(self) -> None:
        self.States = None
        self.StartAt: str = None
        self._states: List[State] = []

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

    def printable(self) -> str:
        # return self.build().States
        return ' '.join([str(s.__dict__) for k, s in self.build().States.items()])


class StateMachineEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, StateMachine):
            del obj._states

            for k, s in obj.States.items():
                obj.States[k] = StateEncoder().default(s)
                # return obj

        try:
            return super(StateMachineEncoder, self).default(obj)
        except Exception as e:
            print(e)
            print(obj.__dict__)


if __name__ == "__main__":
    s = StateMachine()
    s.next(Task(resource="some", name="Kermit", comment='Foo'))
    s.build()
    print(s.to_json())
