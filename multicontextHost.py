import json
import inspect
from math import floor
from random import random
from socket import AF_INET, SOCK_STREAM, socket
from time import time
from typing import Callable

class multicontextHost:
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
