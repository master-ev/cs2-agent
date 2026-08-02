# CS2 Agent

An agent that follows the CS2 scene for me so I don't have to check five tabs myself. You ask it something, it figures out which sources it needs.

```
> is jaxi live?
No, jaxi is offline right now.

> when do my teams play?
BLAST Bounty Grand Final: Spirit vs MOUZ — 02 August, 13:30
ESL Challenger League: MOUZ.N vs WBT — 02 August, 16:00
```

It pulls from Steam (official updates), HLTV (scene news), Reddit, PandaScore (match schedules, filtered to my teams) and Kick (is someone streaming).

Built with Claude and tool calling - the model gets a description of each source and picks which ones the question actually needs. It also remembers what it's already shown me, so "what's new?" means new since last time, not the same five updates every day. 

There's a `briefing.py` that wraps this into a daily summary and posts it to Discord. A cron job runs it every morning at 9.

## Running it

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # add your own keys
python agent.py
```

You need API keys for Anthropic, PandaScore and Kick, plus a Discord webhook for the briefing.

## Notes

My favourite bug wasn't in the code. When Reddit rate-limited me, the tool returned an empty list, and an empty list looks exactly like "nothing happened" — so the agent would tell me all was quiet while it couldn't see anything at all.