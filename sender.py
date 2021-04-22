import requests


response = requests.post(
    'http://127.0.0.1:5000/send',
    json={'name': 'test', 'text': 'Test text'}
)
print(response.status_code)
print(response.headers)
print(response.text)

# response2 = requests.get(
#     'http://127.0.0.1:5000/status'
# )
# print(response2.status_code)
# print(response2.headers)
# print(response2.text)
# print(response.json())
