import os
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("PANDASCORE_TOKEN")
MATCH_COUNT = 10

def get_upcoming_matches():
    url = "https://api.pandascore.co/csgo/matches/upcoming"
    headers = {"Authorization": "Bearer " + TOKEN,}
    params = {"per_page": MATCH_COUNT,}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
    except requests.RequestException:
        print("Couldn't reach PandaScore.")
        return []
    if response.status_code != 200:
        print("Failed to fetch matches. Status:", response.status_code)
        return []
    return response.json()

def print_matches(matches):
    print("Upcoming CS2 matches\n")
    for match in matches:
        name = match["name"]
        begin = match["begin_at"]
        league = match["league"]["name"]
        print(name)
        print("League:", league)
        print("Starts:", begin)
        print()

if __name__ == "__main__":
    matches = get_upcoming_matches()
    print_matches(matches)