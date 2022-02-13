from multicontextHost import multicontextHost
from serverlessFunction import serverlessFunction

serverContext = multicontextHost()
serverContext.AddHost("127.0.0.1", 8888)

@serverlessFunction
def test(server, context:dict):
    a = context["a"]
    b = context["b"]
    c = a + b

    return {"ok": 1, "c" : c}

response = test(serverContext, {"a":10, "b":20})
print(response)