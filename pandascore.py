from state import filter_new
import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("PANDASCORE_TOKEN")
FETCH_COUNT = 100
DISPLAY_COUNT = 5
FAVOURITE_TEAMS = ["NAVI", "Vitality", "Spirit", "MOUZ", "FaZe", "G2", "The MongolZ"]
LOCAL_TZ = ZoneInfo("Europe/Bucharest")

def match_id(match):
    return match["id"]

def fetch_matches(endpoint):
    url = "https://api.pandascore.co/csgo/matches/" + endpoint
    headers = {"Authorization": "Bearer " + TOKEN}
    params = {"per_page": FETCH_COUNT}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
    except requests.RequestException:
        print("Couldn't reach PandaScore.")
        return []
    if response.status_code != 200:
        print("Failed to fetch matches. Status::", response.status_code)
        return []
    return response.json()

def get_upcoming_matches():
    return fetch_matches("upcoming")

def get_past_matches():
    return fetch_matches("past")

def get_running_matches():
    return fetch_matches("running")

def get_favorite_matches():
    favorites = []
    for match in get_upcoming_matches():
        if is_favorite_match(match):
            favorites.append(match)
    return favorites

def get_favorite_results():
    results = []
    for match in get_past_matches():
        if is_favorite_match(match):
            results.append(match)
    return results

def get_favorite_live():
    live = []
    for match in get_running_matches():
        if is_favorite_match(match):
            live.append(match)
    return live

def format_score(match):
    results = match.get("results", [])
    opponents = match.get("opponents", [])
    if len(results) < 2 or len(opponents) < 2:
        return "score unavailable"
    parts = []
    for result in results:
        team_id = result.get("team_id")
        score = result.get("score")
        name = "?"
        for entry in opponents:
            opponent = entry.get("opponent")
            if opponent and opponent.get("id") == team_id:
                name = opponent.get("name")
        parts.append(name + " " + str(score))
    return " - ".join(parts)

def get_new_matches():
    favorites = get_favorite_matches()
    return filter_new(favorites, "matches", match_id)

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

SECONDARY_TAGS = [
    "academy", "junior", "prodigy", "prospects", "rising",
    "up next", "nxt", "youngsters", ".a", ".n",
]

def is_favorite_match(match):
    if not FAVOURITE_TEAMS:
        return True
    team_names = get_team_names(match)
    for team in team_names:
        lowered = team.lower()
        if any(tag in lowered for tag in SECONDARY_TAGS):
            continue
        for favorite in FAVOURITE_TEAMS:
            if favorite.lower() in lowered:
                return True
    return False

def format_start_time(iso_string):
    cleaned = iso_string.replace("Z", "+00:00")
    utc_time = datetime.fromisoformat(cleaned)
    local_time = utc_time.astimezone(LOCAL_TZ)
    return local_time.strftime("%d %B, %H:%M")

def minutes_until(iso_string):
    cleaned = iso_string.replace("Z", "+00:00")
    start = datetime.fromisoformat(cleaned)
    now = datetime.now(tz=LOCAL_TZ)
    difference = start - now
    return difference.total_seconds() / 60

def get_matches_starting_soon(within_minutes=60):
    soon = []
    for match in get_favorite_matches():
        minutes = minutes_until(match["begin_at"])
        if 0 < minutes <= within_minutes:
            soon.append(match)
    return soon

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