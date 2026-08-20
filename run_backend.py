#!/usr/bin/env python3
"""Daemonize the BLACKOUT backend server."""
import os
import sys
import signal

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

# Double fork to daemonize
if os.fork() > 0:
    sys.exit(0)

os.setsid()

if os.fork() > 0:
    sys.exit(0)

# Redirect stdout/stderr
sys.stdout = open("/tmp/blackout-backend.log", "w")
sys.stderr = sys.stdout

from backend.main import app
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
