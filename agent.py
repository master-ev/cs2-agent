import os
import anthropic
from datetime import datetime
from dotenv import load_dotenv
from steam import get_steam_news, clean_bbcode
from hltv import get_hltv_news
from reddit import get_reddit_posts
from kick import get_access_token, check_channel_status
from pandascore import get_favorite_matches, format_start_time

load_dotenv()
client = anthropic.Anthropic()
MODEL = "claude-haiku-4-5-20251001"

TOOLS = [
    {
        "name": "get_cs2_updates",
        "description": (
            "Get the latest official Counter-Strike 2 updates and announcements "
            "posted by Valve on Steam. Use for game updates, patch notes, or "
            "what Valve changed recently."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_scene_news",
        "description": (
            "Get the latest competitive Counter-Strike news from HLTV: roster "
            "changes, transfers, match results, tournament announcements, player "
            "interviews. Use for anything about the professional scene."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_community_posts",
        "description": (
            "Get popular posts from CS2 subreddits — what players are discussing, "
            "complaining about, or reacting to right now. Use for community "
            "sentiment, not official news."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "subreddit": {
                    "type": "string",
                    "description": "Which subreddit to read: GlobalOffensive or cs2",
                }
            },
            "required": ["subreddit"],
        },
    },
    {
        "name": "check_stream",
        "description": (
            "Check whether a specific Kick streamer is live right now. "
            "Use when the user asks if someone is streaming."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "channel": {
                    "type": "string",
                    "description": "The Kick channel name, for example 'jaxi'",
                }
            },
            "required": ["channel"],
        },
    },
    {
        "name": "get_upcoming_matches",
        "description": (
            "Get upcoming professional CS2 matches for the user's favorite teams, "
            "with tournament names and start times in local time. Use when asked "
            "about schedules, who plays when, or upcoming tournaments."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
]

SYSTEM_PROMPT = (
    "CRITICAL RULE: You must write ALL of your responses in English only. "
    "The user may write in Romanian or any other language — you still answer in English. "
    "Never reply in Romanian.\n\n"
    "You are a CS2 esports assistant with access to several live sources. "
    "Use the tools to answer questions about the CS2 scene. "
    "If a question needs several sources, call several tools. "
    "Be concise and factual."
)

def format_news(news):
    parts = []
    for item in news:
        date = datetime.fromtimestamp(item["date"]).strftime("%d %B %Y")
        content = clean_bbcode(item["contents"])[:500]
        parts.append(item["title"] + " (" + date + ")\n" + content)
    return "\n\n".join(parts)

def format_hltv(news):
    parts = []
    for item in news:
        parts.append(item.title + " (" + item.published + ")\n" + item.description)
    return "\n\n".join(parts)

def format_posts(posts):
    parts = []
    for post in posts:
        parts.append(post.title + "\n" + post.link)
    return "\n".join(parts)

def format_matches(matches):
    parts = []
    for match in matches[:10]:
        line = match["name"] + " - " + match["league"]["name"]
        line = line + " - " + format_start_time(match["begin_at"])
        parts.append(line)
    return "\n".join(parts)

def run_tool(name, tool_input):
    if name == "get_cs2_updates":
        return format_news(get_steam_news())
    if name == "get_scene_news":
        return format_hltv(get_hltv_news())
    if name == "get_community_posts":
        subreddit = tool_input["subreddit"]
        return format_posts(get_reddit_posts(subreddit))
    if name == "check_stream":
        channel = tool_input["channel"]
        token = get_access_token()
        if token is None:
            return "Couldn't authenticate with Kick."
        return check_channel_status(token, channel)
    if name == "get_upcoming_matches":
        return format_matches(get_favorite_matches())
    return "Unknown tool: " + name
    
def ask(question):
    messages = [{"role": "user", "content": question}]
    while True:
        response = client.messages.create(model=MODEL, max_tokens=1500, system=SYSTEM_PROMPT, tools=TOOLS, messages=messages,)
        # reply-ul modelului
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            for block in response.content:
                if block.type == "text":
                    print(block.text)
            return
        results = []
        for block in response.content:
            if block.type == "tool_use":
                print("[tool: " + block.name + "]")
                output = run_tool(block.name, block.input)
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": output,})
        messages.append({"role": "user", "content": results})

if __name__ == "__main__":
    ask("Se mai stie ceva de iM?")