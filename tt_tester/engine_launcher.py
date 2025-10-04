#!/usr/bin/env python3
"""
Engine Launcher for A/B Testing
Launches timetable engines on different ports
"""

import sys
import os
from pathlib import Path

def launch_v20_engine(port=8020):
    """Launch main_v20.py with specified port"""
    # Add the timetable-engine directory to Python path
    engine_dir = Path(__file__).parent.parent / "timetable-engine"
    sys.path.insert(0, str(engine_dir))
    
    # Import and configure uvicorn
    import uvicorn
    
    # Change to engine directory
    os.chdir(engine_dir)
    
    # Import the v20 app
    from main_v20 import app
    
    # Start server
    print(f"Starting main_v20.py on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

def launch_v25_engine(port=8025):
    """Launch main_v25.py with specified port"""
    # Add the timetable-engine directory to Python path
    engine_dir = Path(__file__).parent.parent / "timetable-engine"
    sys.path.insert(0, str(engine_dir))
    
    # Import and configure uvicorn
    import uvicorn
    
    # Change to engine directory
    os.chdir(engine_dir)
    
    # Import the v25 app
    from main_v25 import app
    
    # Start server
    print(f"Starting main_v25.py on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python engine_launcher.py <version> <port>")
        print("Example: python engine_launcher.py v20 8020")
        sys.exit(1)
    
    version = sys.argv[1]
    port = int(sys.argv[2])
    
    if version == "v20":
        launch_v20_engine(port)
    elif version == "v25":
        launch_v25_engine(port)
    else:
        print(f"Unknown version: {version}")
        sys.exit(1)