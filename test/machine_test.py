from states import Task
from machine import StateMachine

def test_hello_machine():
    s = StateMachine()
    s.next(Task(resource="some", name="Kermit", comment='Foo'))
    assert len(s.States) == 1
