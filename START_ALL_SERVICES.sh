#!/bin/bash

echo "========================================"
echo "Starting All Services"
echo "========================================"
echo ""

echo "[1/3] Starting Python Timetable Engine (v2.5)..."
cd timetable-engine
gnome-terminal --tab --title="Python Engine" -- bash -c "python main_v25.py; exec bash" 2>/dev/null || \
xterm -T "Python Engine" -e "python main_v25.py; bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '"$(pwd)"' && python main_v25.py"' 2>/dev/null &
cd ..
sleep 3

echo "[2/3] Starting Backend (NestJS)..."
cd backend
gnome-terminal --tab --title="Backend API" -- bash -c "npm run start:dev; exec bash" 2>/dev/null || \
xterm -T "Backend API" -e "npm run start:dev; bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '"$(pwd)"' && npm run start:dev"' 2>/dev/null &
cd ..
sleep 5

echo "[3/3] Starting Frontend (Next.js)..."
cd frontend
gnome-terminal --tab --title="Frontend UI" -- bash -c "npm run dev; exec bash" 2>/dev/null || \
xterm -T "Frontend UI" -e "npm run dev; bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '"$(pwd)"' && npm run dev"' 2>/dev/null &
cd ..

echo ""
echo "========================================"
echo "All services starting!"
echo "========================================"
echo ""
echo "Python Engine:  http://localhost:8000/docs"
echo "Backend API:    http://localhost:5000/api/v1"
echo "Frontend UI:    http://localhost:3000"
echo ""
