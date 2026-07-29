import os
import requests
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("KICK_CLIENT_ID")
CLIENT_SECRET = os.getenv("KICK_CLIENT_SECRET")
CHANNEL = "jaxi"

def get_access_token():
    url = "https://id.kick.com/oauth/token"
    data = {"grant_type": "client_credentials", "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,}
    try:
        response = requests.post(url, data=data, timeout=10)
    except requests.RequestException:
        print("Couldn't reach Kick's auth server.")
        return None
    if response.status_code != 200:
        print("Failed to get token. Status:", response.status_code)
        return None
    token_data = response.json()
    return token_data["access_token"]

def check_channel(token, channel):
    url = "https://api.kick.com/public/v1/channels"
    headers = {"Authorization": "Bearer " + token,}
    params = {"slug": channel,}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
    except requests.RequestException:
        print("Couldn't reach Kick's API.")
        return
    if response.status_code != 200:
        print("Failed to read channel. Status:", response.status_code)
        return
    data = response.json()
    channels = data["data"]
    if not channels:
        print("Channel not found:", channel)
        return
    info = channels[0]
    stream = info.get("stream")
    if stream is None:
        print(channel, "is offline")
        return
    live_status = info["stream"]["is_live"]
    if live_status:
        print(channel, "is live")
    else:
        print(channel, "is offline")

if __name__ == "__main__":
    token = get_access_token()
    if token:
        check_channel(token, CHANNEL)