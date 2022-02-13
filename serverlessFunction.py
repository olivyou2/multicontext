import json
import inspect
from math import floor
from random import random
from socket import AF_INET, SOCK_STREAM, socket
from time import time
from typing import Callable
import multicontextHost

def serverlessFunction(func:Callable):
    def wrapper(host:multicontextHost, context=None, set=None):
        stt = time()

        rand_host, rand_port = host.GetRandomHost()

        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((rand_host, rand_port))

        source = "\n".join(inspect.getsource(func).split("\n")[1:])

        executeSet = list()

        func_name = func.__name__

        if (context != None):
            executeSet.append({
                "arg": context
            })
        else:
            for item in set:
                executeSet.append({
                    "arg": item
                })

        send_context = {
            "type": "execute",
            "source": source,
            "name": func_name,
            "executes": executeSet
        }

        client_socket.send((json.dumps(send_context)+"\r\n").encode())
        
        buff = ""
        func_res = None

        while True:
            recv_buff = client_socket.recv(1024)
            recv = recv_buff.decode("utf-8")

            buff += recv
            index = buff.find("\r\n")

            if (index == -1):
                continue
            else:
                result = json.loads(buff[:index])
                func_res = result
                break

        client_socket.close()
        edd = time()

        duration_ms = (edd-stt)*1000
        print(f"Duration : {duration_ms}")

        return func_res

    return wrapper
