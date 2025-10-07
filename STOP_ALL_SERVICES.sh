#!/bin/bash

# Stop All Services Script for macOS/Linux
# Stops Backend (NestJS), Frontend (Next.js), and Timetable Engine (Python)

echo "=================================="
echo "Stopping All Services"
echo "=================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to kill process on port
kill_port() {
    local port=$1
    local service=$2
    local pids=$(lsof -ti:$port 2>/dev/null)

    if [ ! -z "$pids" ]; then
        echo -e "${YELLOW}Stopping $service on port $port...${NC}"
        for pid in $pids; do
            echo "  → Killing PID: $pid"
            kill -9 $pid 2>/dev/null
        done
        echo -e "${GREEN}  ✓ $service stopped${NC}"
    else
        echo "  → $service not running on port $port"
    fi
}

# Stop services using PID file if it exists
if [ -f .service_pids ]; then
    echo -e "${YELLOW}Stopping services using saved PIDs...${NC}"
    echo ""

    while IFS= read -r pid; do
        if ps -p $pid > /dev/null 2>&1; then
            echo "  → Killing PID: $pid"
            kill -9 $pid 2>/dev/null
        fi
    done < .service_pids

    rm -f .service_pids
    echo ""
fi

# Also kill by port to ensure cleanup
echo "Ensuring all services are stopped..."
echo ""

kill_port 8000 "Timetable Engine"
kill_port 5000 "Backend API"
kill_port 3000 "Frontend"

echo ""
echo "=================================="
echo -e "${GREEN}All Services Stopped${NC}"
echo "=================================="
echo ""

# Clean up any orphaned node processes (optional, commented out for safety)
# Uncomment if needed:
# echo "Cleaning up node processes..."
# pkill -9 -f "node.*npm" 2>/dev/null
# pkill -9 -f "next" 2>/dev/null
# pkill -9 -f "nest" 2>/dev/null
