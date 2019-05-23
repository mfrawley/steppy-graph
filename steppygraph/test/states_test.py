import json

from steppygraph.machine import Branch, Parallel
from steppygraph.states import Choice, ChoiceCase, Comparison, ComparisonType, Task, StateType, to_serializable, \
    Pass, Catcher, ErrorType, State, BatchJob, EcsTask
from steppygraph.states import Resource, ResourceType
from steppygraph.test.testutils import read_json_test_case, write_json_test_case


def test_state_to_str():
    assert str(StateType.CHOICE) == "Choice"


def test_comparison_type_to_str():
    assert str(ComparisonType.BOOLEAN_EQ) == "BooleanEquals"


def test_resource_to_json():
    res = Resource(name="foo-trigger", type=ResourceType.LAMBDA,
                   aws_ac=1234, region="eu-west-1")
    assert json.dumps(res,
                      default=to_serializable) == '"arn:aws:lambda:eu-west-1:1234:function:foo-trigger"'


def test_lambda_task_to_json():
    assert json.dumps(Task(name="sdfdsf", resource=Resource(type=ResourceType.LAMBDA, name="trigger")),
                      default=to_serializable) == \
        """{"Type": "Task", "Resource": "arn:aws:lambda:::function:trigger", "TimeoutSeconds": 600}"""


def test_batch_task_to_json():
    assert json.dumps(BatchJob(name="foo", definition="fooDef", queue="fooQueue", parameters="$.batchJob"),
                      default=to_serializable) == \
        """{"Type": "Task", "Resource": "arn:aws:states:::batch:submitJob.sync", "TimeoutSeconds": 600, """ + \
        """"Parameters": {"JobDefinition": "fooDef", "JobName": "foo", "JobQueue": "fooQueue", "Parameters.$": "$.batchJob"}}"""


def test_ecs_task_to_json():
    assert json.dumps(EcsTask(name="foo", cluster="cluster_arn", definition="task_definition", launch_type="FARGATE"),
                      default=to_serializable) == \
        """{"Type": "Task", "Resource": "arn:aws:states:::ecs:runTask.sync", "TimeoutSeconds": 600, """ + \
        """"Parameters": {"Cluster": "cluster_arn", "LaunchType": "FARGATE", "TaskDefinition": "task_definition", "NetworkConfiguration": {}, "Overrides": {}}}"""


def test_choice_case_to_json():
    assert json.dumps(ChoiceCase("$.foo.field",
                                 comparison=Comparison(
                                     ComparisonType.BOOLEAN_EQ, value=True),
                                 next=Pass(name="thisistheend")),
                      default=to_serializable) == \
        """{"Variable": "$.foo.field", "Next": "thisistheend", "BooleanEquals": true}"""


def test_choice_to_json():
    t = Task(
        name="endstate",
        resource=Resource(name="foo-trigger", type=ResourceType.LAMBDA)
    )
    choices = [ChoiceCase(variable="Foovar",
                          comparison=Comparison(
                              comparison_type=ComparisonType.BOOLEAN_EQ, value=True),
                          next=t)
               ]
    c = Choice(name="Foochoice", choices=choices, default=t)

    assert json.dumps(c,
                      default=to_serializable) == \
        """{"Type": "Choice", "Choices": [{"Variable": "Foovar", "Next": "endstate", "BooleanEquals": true}], "Default": "endstate"}"""


def test_parallel():
    t = Task(
        name="endstate",
        resource=Resource(name="foo-trigger", type=ResourceType.LAMBDA)
    )
    branch_a = Branch("branchA")
    branch_a.next(t)
    branch_b = Branch("branchB")
    branch_b.next(t)
    p = Parallel("ABTest", branches=[branch_a, branch_b])
    p.build()
    assert len(p.Branches) == 2
    read_json_test_case("parallel_simple_state") == p.to_json()


def test_catcher_to_json():
    c = Catcher(error_equals=[ErrorType.TASK_FAILED], next=Task("foo", resource=Resource("fooAct",
                                                                                         type=ResourceType.ACTIVITY)))
    assert json.dumps(c, default=to_serializable) == read_json_test_case(
        "catcher_to_json")


def test_setting_timeout_works():
    t = Task("foo", timeout_seconds=7, resource=Resource(
        "fooRes", type=ResourceType.LAMBDA))
    assert t.TimeoutSeconds == 7


def test_setting_catcher_on_task_works():
    t2 = Task("foob",
              resource=Resource("sfs", type=ResourceType.LAMBDA))

    t = Task(
        name="catachable",
        resource=Resource(name="foo-trigger", type=ResourceType.LAMBDA),
        catch=[Catcher(error_equals=[ErrorType.TASK_FAILED], next=t2)]
    )
    assert read_json_test_case("catcher_in_the_task") == json.dumps(
        t, default=to_serializable)
