from time import time
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

dataset = []
for i in range(10000):
    dataset.append({"a":10, "b":30})

test(serverContext, set=dataset)