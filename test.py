from multicontextHost import ECRHost, multicontextHost
from serverlessFunction import serverlessFunction

host = ECRHost()

mcontext = host.getMulticontextHost()

@serverlessFunction
def WonhoFunction(host, context):
    a = context["a"]
    b = context["b"]
    c = a + b

    return {"c": c}

result = WonhoFunction(mcontext, set=
    [
        {"a":3, "b":4},
        {"a":3, "b":5},
        {"a":3, "b":6},
        {"a":3, "b":7},
    ]
)

print(result)

#
#response = WonhoFunction(multicontext, context={"a":"b"})

#newHost = multicontextHost()
#newHost.AddHost("127.0.0.1", 8888)

#WonhoFunction(newHost, context={"a":3})