import json
import inspect
from math import floor
from random import random
from socket import AF_INET, SOCK_STREAM, socket
from time import time
from typing import Callable

class MulticontextHost:
    def __init__(self) -> None:
        self.hosts = list()
        self.sex = ""

    def GetRandomHost(self):
        if (len(self.hosts) == 0):
            return None
        else:
            index = floor(random() * (len(self.hosts) - 1))

            return self.hosts[index]

    def AddHost(self, host, port):
        self.hosts.append((host, port))

    def TerminateHost(self):
        for host in self.hosts:
            host_ip, host_port = host
            host_socket = socket(AF_INET, SOCK_STREAM)
            host_socket.connect((host_ip, host_port))
            host_socket.send((json.dumps({"type": "terminate"})+"\r\n").encode())
            host_socket.close()

def serverlessFunction(func:Callable):
    def wrapper(host:MulticontextHost, context):
        stt = time()

        rand_host, rand_port = host.GetRandomHost()

        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((rand_host, rand_port))

        source = "\n".join(inspect.getsource(func).split("\n")[1:])

        func_name = func.__name__
        send_context = {
            "type": "execute",
            "source": source,
            "name": func_name,
            "arg": context
        }

        client_socket.send((json.dumps(send_context)+"\r\n").encode())
        
        buff = ""
        func_res = None

        while True:
            recv_buff = client_socket.recv(1024)
            recv = recv_buff.decode("utf-8")

            buff += recv
            index = recv.find("\r\n")

            if (index == -1):
                continue
            else:
                result = json.loads(recv[:index])
                func_res = result
                break

        client_socket.close()
        edd = time()

        duration_ms = (edd-stt)*1000

        return func_res

    return wrapper
