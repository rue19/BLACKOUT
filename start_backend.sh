#!/bin/bash
cd /home/shrinjali/Desktop/Blackout/backend
source ../.venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
