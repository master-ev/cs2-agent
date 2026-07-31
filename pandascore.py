from state import filter_new
import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("PANDASCORE_TOKEN")
FETCH_COUNT = 50
DISPLAY_COUNT = 5
FAVOURITE_TEAMS = ["NAVI", "Vitality", "Spirit", "MOUZ", "FaZe", "G2", "The MongolZ"]
LOCAL_TZ = ZoneInfo("Europe/Bucharest")

def match_id(match):
    return match["id"]

def get_favorite_matches():
    all_matches = get_upcoming_matches()
    favorites = []
    for match in all_matches:
        if is_favorite_match(match):
            favorites.append(match)
    return favorites

def get_new_matches():
    favorites = get_favorite_matches()
    return filter_new(favorites, "matches", match_id)

def get_upcoming_matches():
    url = "https://api.pandascore.co/csgo/matches/upcoming"
    headers = {"Authorization": "Bearer " + TOKEN,}
    params = {"per_page": FETCH_COUNT,}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
    except requests.RequestException:
        print("Couldn't reach PandaScore.")
        return []
    if response.status_code != 200:
        print("Failed to fetch matches. Status:", response.status_code)
        return []
    return response.json()

def get_team_names(match):
    names = []
    for entry in match.get("opponents", []):
        opponent = entry.get("opponent")
        if opponent is None:
            continue
        name = opponent.get("name")
        if name:
            names.append(name)
    return names

def is_favorite_match(match):
    if not FAVOURITE_TEAMS:
        return True
    team_names = get_team_names(match)
    for team in team_names:
        if "academy" in team.lower() or "junior" in team.lower():
            continue
        for favorite in FAVOURITE_TEAMS:
            if favorite.lower() in team.lower():
                return True
    return False

def format_start_time(iso_string):
    cleaned = iso_string.replace("Z", "+00:00")
    utc_time = datetime.fromisoformat(cleaned)
    local_time = utc_time.astimezone(LOCAL_TZ)
    return local_time.strftime("%d %B, %H:%M")

def print_matches(matches):
    print("New matches for your teams\n")
    for match in matches[:DISPLAY_COUNT]:
        name = match["name"]
        league = match["league"]["name"]
        start = format_start_time(match["begin_at"])
        print(name)
        print("League:", league)
        print("Starts:", start)
        print()

if __name__ == "__main__":
    matches = get_new_matches()
    if matches:
        print_matches(matches)
    else:
        print ("No newly anounced matches for your teams.")