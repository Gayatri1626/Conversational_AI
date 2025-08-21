# emotion/emotion_client.py

import requests

def get_emotion_summary():
    response = requests.get("http://localhost:5000/emotion_summary?window_sec=5")
    response.raise_for_status()  # This will raise an HTTPError for bad responses
    return response.json()

if __name__ == "__main__":
    summary = get_emotion_summary()
    print(summary)
