import requests

DUMMY_API_URL = "http://host.docker.internal:80"


def send_alert(message):
    res = requests.post(f"{DUMMY_API_URL}/send-alert/", json={"text": message})
    if res.status_code == 200:
        return res.json()["message"]
    else:
        res.raise_for_status()
        return ""


def get_senti_score(message):
    res = requests.post(f"{DUMMY_API_URL}/get-senti-score/", json={"text": message})
    if res.status_code == 200:
        return res.json()["result"]
    else:
        res.raise_for_status()
        return ""
