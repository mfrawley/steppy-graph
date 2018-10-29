# Steppy Graph - An alpha-quality DSL for Step Functions

Example Usage:
```
s = StateMachine()
    res = Resource(name="foores", type=ResourceType.LAMBDA)
    s.next(Task(resource=res, name="Kermit", comment='Foo'))
    s.next(Wait(name="Waiting time", comment='Foo', seconds=2))
    s.next(Pass(name="Pass the buck"))
    s.next(Task(resource=res, name="Miss Piggy", comment='Foo'))
    s.build()
    
    print(s.to_json())
```
should produce output similar to:
```
{
    "StartAt": "Kermit",
    "States": {
        "Kermit": {
            "Comment": "Foo",
            "End": false,
            "Next": "Waiting time",
            "Resource": "arn:aws:lambda:::function:foores",
            "TimeoutSeconds": 600,
            "Type": "Task"
        },
        "Miss Piggy": {
            "Comment": "Foo",
            "End": true,
            "Resource": "arn:aws:lambda:::function:foores",
            "TimeoutSeconds": 600,
            "Type": "Task"
        },
        "Pass the buck": {
            "Comment": "",
            "End": false,
            "Next": "Miss Piggy",
            "Type": "Pass"
        },
        "Waiting time": {
            "Comment": "Foo",
            "End": false,
            "Next": "Pass the buck",
            "Seconds": 2,
            "Type": "Wait"
        }
    },
    "TimeoutSeconds": 600
}
```

Note - states added via the next() method in StateMachine are always "autoconnected", that is they have a boolean
flag set which will automatically wire them up to the next state in the graph. Use add_state for states that you want to
add without any auto-connection of the Next attribute.

