import requests

url = "https://api.sarvam.ai/translate"

payload = {
    "input": "an apple a day keeps the doctor away",
    "source_language_code": "en-IN",
    "target_language_code": "hi-IN",
    "speaker_gender": "Male",
    "mode": "formal",
    "model": "mayura:v1",
    "enable_preprocessing": True
}
headers = {"Content-Type": "application/json",
           "API-Subscription-Key": "223f1de5-2860-4900-b3bb-e733ad9653a8"}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)