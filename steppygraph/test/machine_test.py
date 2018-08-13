import json

from machine import StateMachine
from states import Task, Resource, ResourceType, Wait, Pass


def test_hello_machine():
    s = StateMachine()
    s.next(Task(resource="some", name="Kermit", comment='Foo'))
    s.build()
    assert len(s.get_states()) == 1
    assert s.StartAt == s.get_states()[0].name(), str(s.get_states()[0])


def test_next_set_for_two_state_machine():
    s = StateMachine()
    res = Resource(name="foores", type=ResourceType.LAMBDA)
    s.next(Task(resource=res, name="Kermit", comment='Foo'))
    s.next(Task(resource=res, name="Miss Piggy", comment='Foo'))
    s.build()
    assert len(s.get_states()) == 2
    assert s.StartAt == "Kermit"
    assert s.get_states()[0].Next == s.get_states()[1].name(), s.printable()
    assert s.get_states()[-1].Next == None


def test_pass_wait():
    s = StateMachine()
    s.next(Wait(name="Hold!"))
    s.next(Pass(name="Pass the buck"))
    s.next(Wait(name="Who you calling buck?", seconds=5))
    s.build()

    assert s.count_states() == 3
    assert s.get_states()[-1].Seconds == 5