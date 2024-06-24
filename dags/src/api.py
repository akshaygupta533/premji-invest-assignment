import os

import requests

DUMMY_API_URL = os.environ["DUMMY_API_URL"]


def send_alert(message):
    # Method to call mock api for sending alert with error message
    res = requests.post(f"{DUMMY_API_URL}/send-alert/", json={"text": message})
    if res.status_code == 200:
        return res.json()["message"]
    else:
        res.raise_for_status()
        return ""


def get_senti_score(message):
    # Method to call mock api for getting sentiment score for a text
    res = requests.post(f"{DUMMY_API_URL}/get-senti-score/", json={"text": message})
    if res.status_code == 200:
        return res.json()["result"]
    else:
        res.raise_for_status()
        return ""
