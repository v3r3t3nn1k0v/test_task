import requests

url = 'http://127.0.0.1:8000/hero/'
body = {
    "name": "batman",
    "filters" : [
        {
            "filter_type": "exact", 
            'property' : 'power', 
            'value' : 63
        }
    ]
}
response = requests.get(url=url, json=body)
print(response.text)