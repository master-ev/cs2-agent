import os
import anthropic
from datetime import datetime
from dotenv import load_dotenv
from steam import get_steam_news, clean_bbcode

load_dotenv()
client = anthropic.Anthropic()
MODEL = "claude-haiku-4-5-20251001"

TOOLS = [
    {
        "name": "get_cs2_updates",
        "description": (
            "Get the latest official Counter-Strike 2 updates and announcements "
            "posted by Valve on Steam. Use this when the user asks about game "
            "updates, patch notes, or what Valve changed recently."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    }
]

SYSTEM_PROMPT = (
    "CRITICAL RULE: You must write ALL of your responses in English only. "
    "The user may write in Romanian or any other language — you still answer in English. "
    "Never reply in Romanian.\n\n"
    "You are a CS2 esports assistant. Be concise and factual."
)

def format_news(news):
    parts = []
    for item in news:
        title = item["title"]
        date = datetime.fromtimestamp(item["date"]).strftime("%d %B %Y")
        content = clean_bbcode(item["contents"])[:500]
        parts.append(title + " (" + date + ")\n" + content)
    return "\n\n".join(parts)

def run_tool(name, tool_input):
    if name == "get_cs2_updates":
        news = get_steam_news()
        return format_news(news)
    return "Unknown tool: " + name

def ask(question):
    messages = [{"role": "user", "content": question}]
    while True:
        response = client.messages.create(model=MODEL, max_tokens=1000, system=SYSTEM_PROMPT, tools=TOOLS, messages=messages,)
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
    ask("a modificat Valve ceva la bombă?")