#!/bin/bash

# Status Check Script for macOS/Linux
# Checks status of Backend (NestJS), Frontend (Next.js), and Timetable Engine (Python)

echo "=================================="
echo "Service Status Check"
echo "=================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if port is in use and get PID
check_service() {
    local service_name=$1
    local port=$2
    local url=$3

    local pid=$(lsof -ti:$port 2>/dev/null)

    if [ ! -z "$pid" ]; then
        # Get process info
        local process_info=$(ps -p $pid -o comm= 2>/dev/null)
        echo -e "${GREEN}✓ $service_name${NC}"
        echo -e "  Status: ${GREEN}RUNNING${NC}"
        echo "  Port: $port"
        echo "  PID: $pid"
        echo "  Process: $process_info"
        echo "  URL: $url"
        return 0
    else
        echo -e "${RED}✗ $service_name${NC}"
        echo -e "  Status: ${RED}STOPPED${NC}"
        echo "  Port: $port"
        echo "  URL: $url"
        return 1
    fi
}

# Track how many services are running
RUNNING_COUNT=0
TOTAL_COUNT=3

# 1. Check Timetable Engine (Python - Port 8000)
echo -e "${BLUE}[1/3] Timetable Engine (Python FastAPI)${NC}"
if check_service "Timetable Engine" 8000 "http://localhost:8000"; then
    ((RUNNING_COUNT++))
fi
echo ""

# 2. Check Backend (NestJS - Port 5000)
echo -e "${BLUE}[2/3] Backend (NestJS)${NC}"
if check_service "Backend API" 5000 "http://localhost:5000"; then
    ((RUNNING_COUNT++))
fi
echo ""

# 3. Check Frontend (Next.js - Port 3000)
echo -e "${BLUE}[3/3] Frontend (Next.js)${NC}"
if check_service "Frontend" 3000 "http://localhost:3000"; then
    ((RUNNING_COUNT++))
fi
echo ""

# Summary
echo "=================================="
if [ $RUNNING_COUNT -eq $TOTAL_COUNT ]; then
    echo -e "${GREEN}All Services Running ($RUNNING_COUNT/$TOTAL_COUNT)${NC}"
elif [ $RUNNING_COUNT -eq 0 ]; then
    echo -e "${RED}All Services Stopped ($RUNNING_COUNT/$TOTAL_COUNT)${NC}"
else
    echo -e "${YELLOW}Partial Services Running ($RUNNING_COUNT/$TOTAL_COUNT)${NC}"
fi
echo "=================================="
echo ""

# Show saved PIDs if file exists
if [ -f .service_pids ]; then
    echo "Saved PIDs in .service_pids:"
    cat -n .service_pids
    echo ""
fi

# Show available commands
echo "Available commands:"
echo "  ./START_ALL_SERVICES.sh  - Start all services"
echo "  ./STOP_ALL_SERVICES.sh   - Stop all services"
echo "  ./STATUS_ALL_SERVICES.sh - Check service status"
echo ""

# Show logs info if services are running
if [ $RUNNING_COUNT -gt 0 ]; then
    echo "View logs with:"
    if lsof -ti:8000 >/dev/null 2>&1; then
        echo "  tail -f logs/timetable-engine.log"
    fi
    if lsof -ti:5000 >/dev/null 2>&1; then
        echo "  tail -f logs/backend.log"
    fi
    if lsof -ti:3000 >/dev/null 2>&1; then
        echo "  tail -f logs/frontend.log"
    fi
    echo ""
fi
