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
    news = get_hltv_news()
    print_news(news)