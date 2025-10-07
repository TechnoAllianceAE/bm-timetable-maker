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
echo -e "${GREEN}[1/3] Starting Timetable Engine (Python FastAPI)...${NC}"
if check_port 8000; then
    echo -e "${YELLOW}Port 8000 already in use${NC}"
    kill_port 8000
fi

cd timetable-engine
python3 main_v25.py > ../logs/timetable-engine.log 2>&1 &
TIMETABLE_PID=$!
echo "  → Timetable Engine started on port 8000 (PID: $TIMETABLE_PID)"
echo "  → Logs: logs/timetable-engine.log"
cd ..

sleep 2

# 2. Start Backend (NestJS - Port 5000)
echo ""
echo -e "${GREEN}[2/3] Starting Backend (NestJS)...${NC}"
if check_port 5000; then
    echo -e "${YELLOW}Port 5000 already in use${NC}"
    kill_port 5000
fi

cd backend
npm run start:dev > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "  → Backend started on port 5000 (PID: $BACKEND_PID)"
echo "  → Logs: logs/backend.log"
cd ..

sleep 3

# 3. Start Frontend (Next.js - Port 3000)
echo ""
echo -e "${GREEN}[3/3] Starting Frontend (Next.js)...${NC}"
if check_port 3000; then
    echo -e "${YELLOW}Port 3000 already in use${NC}"
    kill_port 3000
fi

cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "  → Frontend started on port 3000 (PID: $FRONTEND_PID)"
echo "  → Logs: logs/frontend.log"
cd ..

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
