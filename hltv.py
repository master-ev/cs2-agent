from state import load_seen, save_seen, get_seen_ids, mark_as_seen
import feedparser
from time import strftime

FEED_URL = "https://www.hltv.org/rss/news"
NEWS_COUNT = 5

def get_hltv_news():
    feed = feedparser.parse(FEED_URL)
    if not feed.entries:
        print("Couldn't read the HLTV feed.")
        return []
    return feed.entries[:NEWS_COUNT]

def get_new_hltv_news():
    all_news = get_hltv_news()
    seen = load_seen()
    already_seen = get_seen_ids(seen, "hltv")
    new_items = []
    for item in all_news:
        item_id = item.link
        if item_id in already_seen:
            continue
        new_items.append(item)
        mark_as_seen(seen, "hltv", item_id)
    save_seen(seen)
    return new_items

def print_news(items):
    print("Latest HLTV news\n")
    for item in items:
        title = item.title
        description = item.description
        published = strftime("%d %B %Y, %H:%M", item.published_parsed)
        link = item.link
        print(title)
        print(published)
        print(description)
        print(link)
        print()

if __name__ == "__main__":
    news = get_new_hltv_news()
    if news:
        print_news(news)
    else:
        print("No new HLTV news since last check.")