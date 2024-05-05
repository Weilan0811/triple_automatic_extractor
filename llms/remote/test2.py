import json
import requests

prompt = "你的名字是llama, 一个人工智能助理. 说说你对中国的看法."

data = {
    "prompt": prompt,
    "n_predict": 128
}
headers = {'Content-Type': 'application/json'}

result = requests.post(
    url="http://192.168.17.128:8080/completion",
    data=json.dumps(data),
    headers=headers
)

print(result.text)
