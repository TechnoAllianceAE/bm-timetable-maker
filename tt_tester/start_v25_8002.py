#!/usr/bin/env python3
"""Launcher for v2.5 engine on port 8002"""
import sys
import os
import io

# Fix encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
engine_dir = os.path.join(parent_dir, 'timetable-engine')
sys.path.insert(0, engine_dir)
os.chdir(engine_dir)

import uvicorn
from main_v25 import app

if __name__ == "__main__":
    print("Starting v2.5 engine on port 8002...")
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
