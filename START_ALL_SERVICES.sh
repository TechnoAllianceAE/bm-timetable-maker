#!/bin/bash

# Start All Services Script for macOS/Linux
# Starts Backend (NestJS), Frontend (Next.js), and Timetable Engine (Python)

echo "=================================="
echo "Starting All Services"
echo "=================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}Killing existing process on port $port (PID: $pid)${NC}"
        kill -9 $pid 2>/dev/null
        sleep 1
    fi
}

# Create logs directory if it doesn't exist
mkdir -p logs

# 1. Start Timetable Engine (Python - Port 8000)
echo -e "${GREEN}[1/3] Checking Timetable Engine (Python FastAPI)...${NC}"
if check_port 8000; then
    echo -e "${GREEN}  ✓ Timetable Engine already running on port 8000${NC}"
    TIMETABLE_PID=$(lsof -ti:8000)
else
    echo "  → Starting Timetable Engine..."
    cd timetable-engine
    python3 main_v25.py > ../logs/timetable-engine.log 2>&1 &
    TIMETABLE_PID=$!
    cd ..
    sleep 2
    echo -e "${GREEN}  ✓ Timetable Engine started on port 8000 (PID: $TIMETABLE_PID)${NC}"
fi
echo "  → Logs: logs/timetable-engine.log"

# 2. Start Backend (NestJS - Port 5000)
echo ""
echo -e "${GREEN}[2/3] Checking Backend (NestJS)...${NC}"
if check_port 5000; then
    echo -e "${GREEN}  ✓ Backend already running on port 5000${NC}"
    BACKEND_PID=$(lsof -ti:5000)
else
    echo "  → Starting Backend..."
    cd backend
    npm run start:dev > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    sleep 3
    echo -e "${GREEN}  ✓ Backend started on port 5000 (PID: $BACKEND_PID)${NC}"
fi
echo "  → Logs: logs/backend.log"

# 3. Start Frontend (Next.js - Port 3000)
echo ""
echo -e "${GREEN}[3/3] Checking Frontend (Next.js)...${NC}"
if check_port 3000; then
    echo -e "${GREEN}  ✓ Frontend already running on port 3000${NC}"
    FRONTEND_PID=$(lsof -ti:3000)
else
    echo "  → Starting Frontend..."
    cd frontend
    npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    sleep 2
    echo -e "${GREEN}  ✓ Frontend started on port 3000 (PID: $FRONTEND_PID)${NC}"
fi
echo "  → Logs: logs/frontend.log"

# Save PIDs to file for later shutdown
echo "$TIMETABLE_PID" > .service_pids
echo "$BACKEND_PID" >> .service_pids
echo "$FRONTEND_PID" >> .service_pids

echo ""
echo "=================================="
echo -e "${GREEN}All Services Started Successfully!${NC}"
echo "=================================="
echo ""
echo "Service URLs:"
echo "  🐍 Timetable Engine: http://localhost:8000"
echo "  🐍 Timetable Docs:   http://localhost:8000/docs"
echo "  🔧 Backend API:      http://localhost:5000"
echo "  🌐 Frontend:         http://localhost:3000"
echo ""
echo "Service PIDs saved to .service_pids"
echo ""
echo "To view logs:"
echo "  tail -f logs/timetable-engine.log"
echo "  tail -f logs/backend.log"
echo "  tail -f logs/frontend.log"
echo ""
echo "To stop all services:"
echo "  ./STOP_ALL_SERVICES.sh"
echo ""
