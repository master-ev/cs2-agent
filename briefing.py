import os
import requests
from dotenv import load_dotenv
from agent import client, MODEL, TOOLS, run_tool

load_dotenv()
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
MAX_MESSAGE_LENGTH = 1900

BRIEFING_PROMPT = (
    "Write a short daily CS2 briefing. Check what is new since the last check, "
    "the upcoming matches for my teams, and whether jaxi is streaming. "
    "Keep it under 1500 characters. Use short sections. "
    "If nothing happened in a category, say so in one line instead of padding. "
    "If a source could not be checked, say that explicitly."
)

SYSTEM_PROMPT = (
    "You write concise daily briefings about the CS2 scene, in English. "
    "Never invent information that did not come from a tool. "
    "If a tool result starts with ERROR, report that the source was unavailable."
)

def generate_briefing():
    messages = [{"role": "user", "content": BRIEFING_PROMPT}]
    while True:
        response = client.messages.create(model=MODEL, max_tokens=1500, system=SYSTEM_PROMPT, tools=TOOLS, messages=messages,)
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            text_parts = []
            for block in response.content:
                if block.type == "text":
                    text_parts.append(block.text)
            return "\n".join(text_parts)
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

def send_to_discord(text):
    if not WEBHOOK_URL:
        print("No discord webhook.")
        return False
    if len(text) > MAX_MESSAGE_LENGTH:
        text = text[:MAX_MESSAGE_LENGTH] + "..."
    payload = {"content": text}
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
    except requests.RequestException:
        print("Couldn't reach Discord.")
        return False
    if response.status_code not in [200, 204]:
        print("Discord returned status", response.status_code)
        return False
    return True

if __name__ == "__main__":
    briefing = generate_briefing()
    print(briefing)
    print()
    if send_to_discord(briefing):
        print("Sent to Discord.")