FROM python:3.10.2-slim
RUN ["pip3", "install", "boto3"]
ENV AWS_ACCESS_KEY_ID=AKIAYRLB4BHGQV5XSNEU
ENV AWS_SECRET_ACCESS_KEY=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
ENV AWS_DEFAULT_REGION=ap-northeast-2
ENTRYPOINT "bash"