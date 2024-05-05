import json

a = [{
    "111": 111,
    "222": 222
}]
print(json.dumps(a, ensure_ascii=False, indent=4))
