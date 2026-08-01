#!/bin/bash
# run the daily briefing

cd "/home/evelin/My STUFF/cs2-agent"
source venv/bin/activate
python briefing.py >> briefing.log 2>&1