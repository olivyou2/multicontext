# Multicontext
여러 Host 에서 Python 코드를 원격으로 실행하게 해주는 Framework

### How to use it
~~~~python
from multicontext import MulticontextHost, serverlessFunction

host = MulticontextHost()
host.AddHost("Server Host Here", Server Port Here)

@serverlessFunction
def testFunction(host, context): # 여기서, host 는 사용되지 않지만 내부적인 작동을 위해 함수선언에 추가되어야 합니다.
  keys = list(context.keys())
  
  return {"ok": 1, "keys": keys}
  
response = testFunction(host, {"a": "1", "b": 2});
print(response)
# Expected :
# {ok: 1, keys: ["a", "b"]}
~~~~

### How to run Host