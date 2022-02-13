import json
import boto3
from math import floor
from random import random
from socket import AF_INET, SOCK_STREAM, socket

class ECRHost:
    def __init__(self):
        self.ecsClient = boto3.client("ecs")
        self.ec2Client = boto3.client("ec2")
        self.ec2Resource = boto3.resource('ec2')

        self.CheckAndCreateSecurityGroup()
        self.registerTaskDefinition()

    def GetSubnets(self):
        arr = []

        for subnet in self.ec2Client.describe_subnets()["Subnets"]:
            arr.append(subnet["SubnetId"])

        return arr

    def GetSecurityGroups(self):
        groups = self.ec2Client.describe_security_groups()
        return groups

    def CheckAndCreateSecurityGroup(self):
        groups = self.GetSecurityGroups()["SecurityGroups"]

        groupId = ""
        exists = False
        for group in groups:
            if (group["GroupName"] == "multicontext-group"):
                groupId = group["GroupId"]
                exists = True
                break
        
        if not exists:
            resp = self.ec2Client.create_security_group(
                Description="Security Group for MultiContext",
                GroupName="multicontext-group"
            )

            groupId = resp["GroupId"]
            securityGroup = self.ec2Resource.SecurityGroup(groupId)
            resp = securityGroup.authorize_ingress(
                IpPermissions=[
                    {
                        "FromPort": 8888,
                        "IpProtocol": "tcp",
                        "IpRanges": [
                            {
                                "CidrIp": "0.0.0.0/0"
                            }
                        ],
                        "Ipv6Ranges": [],
                        "PrefixListIds": [],
                        "ToPort": 8888,
                        "UserIdGroupPairs": []
                    }
                ],
            )

            return groupId
        else:
            return groupId
            
    def createCluster(self):
        self.ecsClient.create_cluster(
            clusterName='multicontext-cluster'
        )

    def listTask(self):
        response = self.ecsClient.list_tasks(cluster="multicontext-cluster")
        return response["taskArns"]
    
    def describeTask(self):
        taskIds = self.listTask()

        response = self.ecsClient.describe_tasks(cluster="multicontext-cluster", tasks=taskIds)
        return response

    def getAvailableEnis(self):
        enis = list()

        describes = self.describeTask()
        for describe in describes["tasks"]:
            attach = describe["attachments"]
            containers = describe["containers"]
            if (containers[0]["lastStatus"] == "RUNNING"):
                enis.append(attach[0]["details"][1]["value"])

        return enis

    def getHostCount(self):
        describes = self.describeTask()
        running = 0
        pending = 0

        for describe in describes["task"]:
            containers = describe["containers"]
            if (containers[0]["lastStatus"] == "RUNNING"):
                running += 1
            else:
                pending += 1
        
        return running, pending

    def getPublicIp(self, eni):
        ni = self.ec2Resource.NetworkInterface(eni)
        attributes = ni.association_attribute
        return attributes["PublicIp"]
            
    def getClutserIps(self):
        enis = self.getAvailableEnis()
        publicip = list()

        for eni in enis:
            publicip.append(self.getPublicIp(eni))

        return publicip

    def registerTaskDefinition(self):
        response = self.ecsClient.register_task_definition(
            executionRoleArn= "arn:aws:iam::587005168077:role/ecsTaskExecutionRole",
            containerDefinitions= [
                {
                "logConfiguration": {
                    "logDriver": "awslogs",
                    "options": {
                    "awslogs-group": "/ecs/multicontext-python",
                    "awslogs-region": "ap-northeast-2",
                    "awslogs-stream-prefix": "ecs"
                    }
                },
                "portMappings": [
                    {
                    "hostPort": 8888,
                    "protocol": "tcp",
                    "containerPort": 8888
                    }
                ],
                "cpu": 0,
                "environment": [],
                "mountPoints": [],
                "volumesFrom": [],
                "image": "toolscomfact/multicontext-python:latest",
                "name": "multicontext-python"
                }
            ],
            placementConstraints= [],
            memory= "2048",
            taskRoleArn= "arn:aws:iam::587005168077:role/ecsTaskExecutionRole",
            family= "multicontext-python",
            requiresCompatibilities= [
                "FARGATE"
            ],
            networkMode= "awsvpc",
            runtimePlatform= {
                "operatingSystemFamily": "LINUX",
            },
            cpu= "1024",
        )
        return response

    def runTask(self, count):
        response=self.ecsClient.run_task(
            capacityProviderStrategy=[
                {
                    "capacityProvider": "FARGATE_SPOT",
                    "weight": 1,
                    "base": 1
                }
            ],
            platformVersion='LATEST',
            count=count,
            cluster="multicontext-cluster",
            taskDefinition="multicontext-python",
            networkConfiguration={
                "awsvpcConfiguration":{
                    "subnets":self.GetSubnets(),
                    'securityGroups': [
                        self.CheckAndCreateSecurityGroup()
                    ],
                    'assignPublicIp': 'ENABLED',
                }
            }           
        )
        return response

    def getMulticontextHost(self):
        host = multicontextHost()
        for ip in self.getClutserIps():
            host.AddHost(ip, 8888)

        return host
        
class multicontextHost:    
    def __init__(self) -> None:
        self.hosts = list()

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

    