import requests
from datetime import datetime
APP_ID = 730
NEWS_COUNT = 3

def get_steam_news():
    url = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"
    params = {
        "appid": APP_ID,
        "count": NEWS_COUNT,
    }
    response = requests.get(url, params=params)
    data = response.json()
    news_items = data["appnews"]["newsitems"]
    return news_items

def print_news(news_items):
    print("Latest CS2 news\n")
    for item in news_items:
        title = item["title"]
        timestamp = item["date"]
        readable = datetime.fromtimestamp(timestamp)
        formatted = readable.strftime("%d %B %Y, %H:%M")
        link = item["url"]
        print(title)
        print(formatted)
        print(link)
        print()


if __name__ == "__main__":
    items = get_steam_news()
    print_news(items)
