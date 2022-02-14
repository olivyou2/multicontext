FROM python:3.10.2-slim
RUN ["pip3", "install", "boto3"]
ENTRYPOINT "bash"
