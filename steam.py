from state import load_seen, save_seen, get_seen_ids, mark_as_seen
import requests
import re
from datetime import datetime
APP_ID = 730
NEWS_COUNT = 5

def clean_bbcode(text):
    without_tags = re.sub(r"\[.*?\]", "", text)
    without_slashes = without_tags.replace("\\", "")
    cleaned = " ".join(without_slashes.split())
    return cleaned

def get_steam_news():
    url = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"
    params = {
        "appid": APP_ID,
        "count": NEWS_COUNT,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.RequestException:
        print("Couldn't reach Steam.")
        return []
    data = response.json()
    if "appnews" not in data or "newsitems" not in data["appnews"]:
        print("Unexpected response from Steam")
        return[]
    news_items = data["appnews"]["newsitems"]
    return news_items

def get_new_steam_news():
    all_news = get_steam_news()
    seen = load_seen()
    already_seen = get_seen_ids(seen, "steam")
    new_items = []
    for item in all_news:
        item_id = item["gid"]
        if item_id in already_seen:
            continue
        new_items.append(item)
        mark_as_seen(seen, "steam", item_id)
    save_seen(seen)
    return new_items

def print_news(news_items):
    print("Latest CS2 news\n")
    for item in news_items:
        title = item["title"]
        timestamp = item["date"]
        raw_content = item["contents"]
        content = clean_bbcode(raw_content)
        preview = content[:300]
        readable = datetime.fromtimestamp(timestamp)
        formatted = readable.strftime("%d %B %Y, %H:%M")
        link = item["url"]
        print(title)
        print(formatted)
        print(preview)
        print(link)
        print()


if __name__ == "__main__":
    items = get_new_steam_news()
    if items:
        print_news(items)
    else:
        print("No new CS2 updates since last check.")