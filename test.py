import requests

url = "http://127.0.0.1:5000/train"
files = {'file': open("/Users/anandkaliappan/Desktop/photosme/testing.zip", 'rb')}
data = {"trigger_phrase": "reva3", "user_name": "Anand"}
response = requests.post(url, files=files, data=data)

print("Status Code:", response.status_code)
print("Response JSON:", response.json())
