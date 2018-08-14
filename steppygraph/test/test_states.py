import json
from steppygraph.states import Choice, ChoiceCase, Comparison, ComparisonType, State, Task, StateType, to_serializable, \
    Pass
from steppygraph.states import Resource, ResourceType

def test_state_to_str():
    assert str(StateType.CHOICE) == "Choice"


def test_comparison_type_to_str():
    assert str(ComparisonType.BOOLEAN_EQ) == "BooleanEquals"


def test_task_to_json():
    assert json.dumps(Task(name="sdfdsf", resource=Resource(type=ResourceType.LAMBDA, name="trigger")),
                      default=to_serializable) == \
           """{"Type": "Task", "End": false, "Comment": "", "Resource": "arn:aws:lambda:::function:trigger", "TimeoutSeconds": 600}"""


def test_choice_case_to_json():
    assert json.dumps(ChoiceCase("$.foo.field",
                                 comparison=Comparison(ComparisonType.BOOLEAN_EQ, value=True),
                                 next=Pass(name="thisistheend")),
                      default=to_serializable) == \
           """{"Variable": "$.foo.field", "Next": "thisistheend", "BooleanEquals": true}"""


def test_choice_to_json():
    t = Task(
        name="endstate",
        resource=Resource(name="foo-trigger", type=ResourceType.LAMBDA)
    )
    choices = [ChoiceCase(variable="Foovar",
                          comparison=Comparison(comparison_type=ComparisonType.BOOLEAN_EQ, value=True),
                          next=t)
               ]
    c = Choice(name="Foochoice", choices=choices, default=t)

    assert json.dumps(c,
                      default=to_serializable) == \
           """{"Type": "Choice", "End": false, "Comment": "", "Choices": [{"Variable": "Foovar", "Next": "endstate", "BooleanEquals": true}], "Default": "endstate"}"""
