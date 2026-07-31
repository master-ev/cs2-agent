from state import filter_new
import feedparser
import time

SUBREDDITS = ["GlobalOffensive", "cs2"]
POST_COUNT = 5
USER_AGENT = "cs2-agent/1.0 by /u/EvelinTheDream"
MAX_RETRIES = 4

def reddit_id(post):
    return post.link

def get_reddit_posts(subreddit):
    feed_url = "https://www.reddit.com/r/" + subreddit + "/hot.rss"
    for attempt in range(MAX_RETRIES):
        feed = feedparser.parse(feed_url, request_headers={"User-Agent": USER_AGENT})
        status = feed.get("status")
        if status == 200 and feed.entries:
            real_posts = feed.entries[2:]
            return real_posts[:POST_COUNT]
        if status == 429:
            wait = 10 * (attempt + 1)
            print("Rate-limited on r/" + subreddit + ", waiting", wait, "seconds...")
            time.sleep(wait)
            continue

        print("Couldn't read r/" + subreddit + " (status:", status, ")")
        return []
    print("Gave up on r/" + subreddit + " after", MAX_RETRIES, "attempts.")
    return []

def get_new_reddit_posts(subreddit):
    posts = get_reddit_posts(subreddit)
    return filter_new(posts, "reddit", reddit_id)

def print_posts(subreddit, posts):
    print("Posts from r/" + subreddit + "\n")
    for post in posts:
        title = post.title
        link = post.link
        print(title)
        print(link)
        print()

if __name__ == "__main__":
    for sub in SUBREDDITS:
        posts = get_new_reddit_posts(sub)
        if posts:
            print_posts(sub, posts)
        else:
            print("No new posts in r/" + sub)
        print("---\n")
        time.sleep(3)
