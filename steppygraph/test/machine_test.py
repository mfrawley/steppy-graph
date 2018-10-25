import json
from pathlib import PurePath

from steppygraph.machine import StateMachine
from steppygraph.states import Task, Resource, ResourceType, Wait, Pass
from steppygraph.test.testutils import read_json_test_case


def test_hello_machine():
    s = StateMachine()
    s.next(Task(resource=Resource("some", type=ResourceType.LAMBDA), name="Kermit", comment='Foo'))
    s.build()
    assert len(s.get_states()) == 1
    assert s.StartAt == s.get_states()[0].name(), str(s.get_states()[0])


def test_add_state_does_not_update_next_property():
    s = StateMachine()
    s.add_state(Task(resource=Resource("some", type=ResourceType.LAMBDA), name="Kermit", comment='Foo'))
    s.add_state(Task(resource=Resource("two", type=ResourceType.LAMBDA), name="Moia", comment='Foo'))
    s.build()
    assert s.get_states()[0]._next != s.get_states()[1].name(), s.printable()


def test_next_set_for_two_state_machine():
    s = StateMachine()
    res = Resource(name="foores", type=ResourceType.LAMBDA)
    s.next(Task(resource=res, name="Kermit", comment='Foo'))
    s.next(Task(resource=res, name="Miss Piggy", comment='Foo'))
    s.build()
    assert len(s.get_states()) == 2
    assert s.StartAt == "Kermit"
    assert s.get_states()[0]._next == s.get_states()[1].name(), s.printable()
    assert s.get_states()[-1]._next == None
    # only the last state should have an "End" key according to spec
    assert s.get_states()[0].End == None
    assert s.get_states()[-1].End == True


def test_pass_wait():
    s = StateMachine()
    s.next(Wait(name="Hold!"))
    s.next(Pass(name="Pass the buck"))
    s.next(Wait(name="Who you calling buck?", seconds=5))
    s.build()

    assert s.count_states() == 3
    assert s.last().Seconds == 5

    assert s.to_json() == read_json_test_case('pass_wait')


def test_machine_sets_region_and_ac():
    s = StateMachine(region='eu-west-1', account=1234)
    s.next(Task(name="Hold!", resource=Resource("Foo", type=ResourceType.LAMBDA)))
    s.build()
    assert s.get_states()[0].Resource.region == 'eu-west-1'
    assert s.get_states()[0].Resource.aws_ac == 1234
