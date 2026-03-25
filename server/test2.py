import requests

resp = requests.post("http://127.0.0.1:11451/texify", json={ "path": "./tex-test.png" })

print(resp.json())

resp = requests.post("http://127.0.0.1:11451/ocr", json={ "path": "./test2.png" })

print(resp.json())
