import json
from typing import List

from states import State, JSON_INDENT


class StateMachine:
    def __init__(self) -> None:
        self.StartAt: str = None
        self._states: List[State] = []

    def to_json(self) -> str:
        return json.dumps(self,
                          sort_keys=True,
                          indent=JSON_INDENT,
                          cls=StateMachineEncoder)

    def next(self, state: State) -> object:
        """
        This method
        """

        self._states.append(state)
        if len(self._states) > 0:
            self._states[-1].Next = state.name()
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
            d[s.name()] = s.to_json()
        self.States = d
        del self._states
        return self


class StateMachineEncoder(json.JSONEncoder):
    def default(self, obj):
        print(type(obj))
        try:
            return super(StateMachineEncoder, self).default(obj)
        except Exception as e:
            print(e)
            print(obj.__dict__)
