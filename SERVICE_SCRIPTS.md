# Service Management Scripts

Scripts to start and stop all services (Backend, Frontend, Timetable Engine) in one command.

## 📁 Files

### For Windows:
- **`START_ALL_SERVICES.bat`** - Start all 3 services
- **`STOP_ALL_SERVICES.bat`** - Stop all 3 services
- **`STATUS_ALL_SERVICES.bat`** - Check status of all services ✨ NEW

### For macOS/Linux:
- **`START_ALL_SERVICES.sh`** - Start all 3 services
- **`STOP_ALL_SERVICES.sh`** - Stop all 3 services
- **`STATUS_ALL_SERVICES.sh`** - Check status of all services ✨ NEW

## 🚀 Usage

### Windows:

```cmd
# Start all services
START_ALL_SERVICES.bat

# Check service status
STATUS_ALL_SERVICES.bat

# Stop all services
STOP_ALL_SERVICES.bat
```

### macOS/Linux:

```bash
# Start all services
./START_ALL_SERVICES.sh

# Check service status
./STATUS_ALL_SERVICES.sh

# Stop all services
./STOP_ALL_SERVICES.sh
```

## 📋 What Gets Started

The scripts start 3 services in order:

1. **Timetable Engine (Python FastAPI)** - Port 8000
   - Handles timetable generation algorithms
   - API docs: http://localhost:8000/docs

2. **Backend API (NestJS)** - Port 5000
   - Main API server
   - Handles auth, CRUD operations
   - Communicates with Timetable Engine

3. **Frontend (Next.js)** - Port 3000
   - Web application UI
   - http://localhost:3000

## 📊 Service URLs

After starting:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Timetable Engine**: http://localhost:8000
- **Timetable Docs**: http://localhost:8000/docs

## 📝 Logs

### Windows:
Services run in separate console windows - logs visible in each window.

### macOS/Linux:
Logs are saved to:
- `logs/timetable-engine.log`
- `logs/backend.log`
- `logs/frontend.log`

View logs in real-time:
```bash
tail -f logs/timetable-engine.log
tail -f logs/backend.log
tail -f logs/frontend.log
```

## 🔧 Features

### START Scripts:
- ✅ Checks if ports are already in use
- ✅ Kills existing processes on ports (optional)
- ✅ Starts services in correct order
- ✅ Waits between starts for services to initialize
- ✅ Saves process IDs for later shutdown (macOS/Linux)
- ✅ Shows service URLs and log locations

### STOP Scripts:
- ✅ Gracefully stops all services
- ✅ Kills processes by port number
- ✅ Uses saved PIDs for cleanup (macOS/Linux)
- ✅ Ensures all processes are terminated

### STATUS Scripts: ✨ NEW
- ✅ Checks if each service is running on its designated port
- ✅ Shows PID (Process ID) for running services
- ✅ Shows process name for identification
- ✅ Color-coded output (Green = Running, Red = Stopped, Yellow = Partial)
- ✅ Displays service URLs for quick access
- ✅ Shows saved PIDs from .service_pids file
- ✅ Overall status summary (3/3, 2/3, etc.)
- ✅ No changes to running services - read-only status check

## ⚠️ Port Conflicts

If ports are already in use:

**Windows**: The BAT script will prompt you to kill existing processes

**macOS/Linux**: The script automatically kills processes on required ports

## 🐛 Troubleshooting

### Services won't start:

1. **Check if ports are free:**
   ```bash
   # macOS/Linux
   lsof -i :3000
   lsof -i :5000
   lsof -i :8000

   # Windows
   netstat -ano | findstr :3000
   netstat -ano | findstr :5000
   netstat -ano | findstr :8000
   ```

2. **Manually kill processes:**
   ```bash
   # macOS/Linux
   kill -9 $(lsof -ti:3000)
   kill -9 $(lsof -ti:5000)
   kill -9 $(lsof -ti:8000)

   # Windows
   taskkill /F /PID <PID>
   ```

3. **Check dependencies:**
   ```bash
   # Backend & Frontend
   cd backend && npm install
   cd frontend && npm install

   # Timetable Engine
   cd timetable-engine
   pip install -r requirements.txt
   ```

### Permission errors (macOS/Linux):

Make scripts executable:
```bash
chmod +x START_ALL_SERVICES.sh
chmod +x STOP_ALL_SERVICES.sh
```

## 🔄 Manual Start (if scripts fail)

### Start individually:

```bash
# 1. Timetable Engine
cd timetable-engine
python3 main_v25.py

# 2. Backend (in new terminal)
cd backend
npm run start:dev

# 3. Frontend (in new terminal)
cd frontend
npm run dev
```

## 📦 Development vs Production

These scripts are for **development** only. For production:

1. Use proper process managers:
   - **PM2** for Node.js services
   - **systemd** or **supervisor** for Python service

2. Use reverse proxy (nginx/Apache)

3. Set up proper logging and monitoring

4. Use environment-specific configs

## 💡 Tips

- **First time setup**: Run `npm install` in backend and frontend folders before starting
- **Python dependencies**: Run `pip install -r requirements.txt` in timetable-engine folder
- **Database setup**: Run migrations before starting backend
- **Check logs**: If services fail, check the log files for errors
- **Clean restart**: Always use STOP script before START to avoid port conflicts

## 🎯 Quick Commands Reference

```bash
# Start everything
./START_ALL_SERVICES.sh

# Check service status
./STATUS_ALL_SERVICES.sh

# Stop everything
./STOP_ALL_SERVICES.sh

# View all logs
tail -f logs/*.log

# Check running services manually
lsof -i :3000,5000,8000

# Force kill all node processes (careful!)
pkill -9 node
pkill -9 python3
```

## 📊 STATUS Script Output Example

```bash
$ ./STATUS_ALL_SERVICES.sh

==================================
Service Status Check
==================================

[1/3] Timetable Engine (Python FastAPI)
✓ Timetable Engine
  Status: RUNNING
  Port: 8000
  PID: 31303
  Process: python3
  URL: http://localhost:8000

[2/3] Backend (NestJS)
✓ Backend API
  Status: RUNNING
  Port: 5000
  PID: 31308
  Process: node
  URL: http://localhost:5000

[3/3] Frontend (Next.js)
✓ Frontend
  Status: RUNNING
  Port: 3000
  PID: 31331
  Process: node
  URL: http://localhost:3000

==================================
All Services Running (3/3)
==================================

Saved PIDs in .service_pids:
31303
31308
31331

Available commands:
  START_ALL_SERVICES.sh  - Start all services
  STOP_ALL_SERVICES.sh   - Stop all services
  STATUS_ALL_SERVICES.sh - Check service status

View logs in the logs/ directory:
  logs/timetable-engine.log
  logs/backend.log
  logs/frontend.log
```
