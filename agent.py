import os
import anthropic
from datetime import datetime
from dotenv import load_dotenv
from steam import get_steam_news, get_new_steam_news, clean_bbcode
from hltv import get_hltv_news, get_new_hltv_news
from reddit import get_reddit_posts
from kick import get_access_token, check_channel_status
from pandascore import get_favorite_matches, format_start_time

load_dotenv()
client = anthropic.Anthropic()
MODEL = "claude-haiku-4-5-20251001"
MAX_HISTORY = 20

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
    {
        "name": "get_new_since_last_check",
        "description": (
            "Get ONLY what is new since the last time the user checked — new Steam "
            "updates and new HLTV news they haven't seen yet. Use this for daily "
            "briefings or when the user asks 'what's new?' or 'anything I missed?'. "
            "Do not use this when the user asks about a specific topic — use the "
            "regular tools for that."
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
    "If a question needs several sources, call several tools.\n\n"
    "The match tool already filters to the user's favorite teams. Never ask them "
    "which teams they follow, and never suggest they set favorites up — that is "
    "already configured. If no matches come back, simply say none are scheduled.\n\n"
    "If a tool result starts with ERROR, tell the user that source could not be "
    "checked — never present it as 'nothing new'. Do not invent information that "
    "did not come from a tool.\n\n"
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
        news = get_steam_news()
        if not news:
            return "Error: Couldn't fetch Steam updates. The source may be unreachable."
        return format_news(news)
    if name == "get_scene_news":
        news = get_hltv_news()
        if not news:
            return "Error: Couln't fetch HLTV news. The source may be unreachable."
        return format_hltv(news)
    if name == "get_community_posts":
        subreddit = tool_input["subreddit"]
        posts = get_reddit_posts(subreddit)
        if not posts:
            return "Error: Couldn't fetch posts from r/" + subreddit + " (possibly rate-limited)."
        return format_posts(posts)
    if name == "check_stream":
        channel = tool_input["channel"]
        token = get_access_token()
        if token is None:
            return "Error: Couldn't authenticate with Kick."
        return check_channel_status(token, channel)
    if name == "get_upcoming_matches":
        matches = get_favorite_matches()
        if not matches:
            return "No upcoming matches found for the favorite teams."
        return format_matches(matches)
    if name == "get_new_since_last_check":
        new_updates = get_new_steam_news()
        new_news = get_new_hltv_news()
        parts = []
        if new_updates:
            parts.append("New Steam updates:\n" + format_news(new_updates))
        else:
            parts.append("No new Steam updates since last check.")
        if new_news:
            parts.append("New HLTV news:\n" + format_hltv(new_news))
        else:
            parts.append("No new HLTV news since last check.")
        return "\n\n".join(parts)
    return "Unknown tool: " + name
    
def ask(question, messages):
    messages.append({"role": "user", "content": question})
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
        handled_ids = []
        for block in response.content:
            if block.type == "tool_use":
                if block.id in handled_ids:
                    continue
                handled_ids.append(block.id)
                print("[tool: " + block.name + "]")
                output = run_tool(block.name, block.input)
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": output,})
        messages.append({"role": "user", "content": results})

def chat():
    print("CS2 agent ready. Type 'quit' to exit, 'reset' to clear history.\n")
    messages = []
    while True:
        question = input("> ")
        if question.lower() in ["quit", "exit", "q"]:
            break
        if question.lower() == "reset":
            messages = []
            print("History cleared.\n")
            continue
        if not question.strip():
            continue
        if len(messages) > MAX_HISTORY:
            messages = messages[-MAX_HISTORY:]
        ask(question, messages)
        print()

if __name__ == "__main__":
    chat()