from time import sleep
from multicontextHost import ECSHost
from multicontextHost import MulticontextHost
from serverlessFunction import serverlessFunction

host = ECSHost()
waitTime = 0

running, pending = host.GetHostCount()
if (running == 0):
    host.RunTask(1)

print(f"Container Status Running : {running}, Pending : {pending}")

while True:
    running, pending = host.GetHostCount()
    waitTime += 1
    if (running > 0):
        break

    print(f"Wait for Run instance ... Elapsed : {waitTime}s")
    sleep(1)

mcontext = host.GetMulticontextHost()

@serverlessFunction
def WonhoFunction(host, context):
    a = context["a"]
    b = context["b"]
    c = a + b

    return {"c": c}

WonhoFunction(mcontext, context={"a":3, "b":4})
    
dataset = []
for i in range(10000):
    dataset.append({"a":3, "b":4})

WonhoFunction(mcontext, set=dataset)
    #WonhoFunction(mcontext, context={"a":3, "b":4})

#mcontext.TerminateHost()

#
#response = WonhoFunction(multicontext, context={"a":"b"})

#newHost = multicontextHost()
#newHost.AddHost("127.0.0.1", 8888)

#WonhoFunction(newHost, context={"a":3})