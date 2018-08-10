import json

from machine import StateMachine
from states import Task


def test_hello_machine():
    s = StateMachine()
    s.next(Task(resource="some", name="Kermit", comment='Foo'))
    s.build()
    assert len(s.get_states()) == 1
    assert s.StartAt == s.get_states()[0].name(), str(s.get_states()[0])


def test_next_set_for_two_state_machine():
    s = StateMachine()
    s.next(Task(resource="some", name="Kermit", comment='Foo'))
    s.next(Task(resource="some", name="Miss Piggy", comment='Foo'))
    s.build()
    assert len(s.get_states()) == 2
    assert s.StartAt == "Kermit"
    assert s.get_states()[0].Next == s.get_states()[1].name(), s.printable()
    assert s.get_states()[-1].Next == None
    # assert s.get_states()[0].Next == s.get_states()[1].name()
