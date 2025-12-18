# MediConnect Development Guide

## Live Reload Setup

Your MediConnect application is now configured for **live reload** during development. This means you can see your code changes in real-time without rebuilding the entire application.

### How It Works

#### Backend (FastAPI)
- **Auto-reload enabled**: The backend runs with `uvicorn --reload` flag
- **Volume mounted**: Your `./backend` directory is mounted into the container
- **Live changes**: Any changes to Python files will automatically restart the FastAPI server

#### Frontend (React)
- **Hot Module Replacement (HMR)**: React dev server automatically reloads on file changes
- **Volume mounted**: Your `./frontend` directory is mounted into the container
- **File watching**: Polling enabled for Docker compatibility (`CHOKIDAR_USEPOLLING=true`)

### Getting Started

#### First Time Setup
```bash
# Build and start the containers
docker-compose up -d --build
```

#### Daily Development Workflow
```bash
# Start containers (no rebuild needed)
docker-compose up -d

# View logs in real-time
docker-compose logs -f

# View backend logs only
docker-compose logs -f backend

# View frontend logs only
docker-compose logs -f frontend
```

#### Making Code Changes
1. Edit any file in `./backend` or `./frontend` on your host machine
2. Save the file
3. **Backend**: Watch the logs - you'll see "Reloading..." message
4. **Frontend**: Your browser will automatically refresh (HMR)
5. No need to restart containers or rebuild!

### When to Rebuild

You only need to rebuild (`--build` flag) when:
- **Backend**: You modify `requirements.txt` (new Python dependencies)
- **Frontend**: You modify `package.json` or `yarn.lock` (new npm packages)
- **Docker config**: You change Dockerfile or docker-compose.yml

```bash
# Rebuild only when dependencies change
docker-compose up -d --build
```

### Useful Commands

```bash
# Stop all containers
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v

# Restart a specific service
docker-compose restart backend
docker-compose restart frontend

# Execute commands inside containers
docker-compose exec backend python -m pytest
docker-compose exec frontend yarn test

# View container status
docker-compose ps

# Follow logs with timestamps
docker-compose logs -f --timestamps
```

### Troubleshooting

#### Changes not reflecting?

**Backend:**
```bash
# Check if uvicorn is running with --reload
docker-compose logs backend | grep reload

# Restart the backend service
docker-compose restart backend
```

**Frontend:**
```bash
# Check if file watching is working
docker-compose logs frontend | grep -i "compiled\|webpack"

# Restart the frontend service
docker-compose restart frontend

# If still not working, rebuild
docker-compose up -d --build frontend
```

#### Permission issues with volumes?
```bash
# Fix ownership (Linux/Mac)
sudo chown -R $USER:$USER ./backend ./frontend
```

#### Port already in use?
```bash
# Find and kill process using port 8000 or 3000
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### Performance Tips

- **File watching in Docker** can be slower than native. The polling is enabled for compatibility.
- **Large node_modules**: The `/app/node_modules` volume prevents syncing node_modules between host and container, improving performance.
- **Python cache**: The `__pycache__` volume prevents cache conflicts between host and container.

### Production Deployment

For production, you should:
1. Remove volume mounts (use COPY in Dockerfile instead)
2. Disable `--reload` flag in backend
3. Build optimized frontend (`yarn build`)
4. Use production-grade WSGI server (gunicorn)
5. Set `restart: always` policy

Consider creating a separate `docker-compose.prod.yml` for production configuration.

---

## Development Workflow Example

```bash
# Morning: Start your dev environment
docker-compose up -d

# Work on a feature
# Edit: backend/app/routers/appointments.py
# Save → Backend auto-reloads in ~1-2 seconds

# Edit: frontend/src/pages/Appointments.js  
# Save → Browser auto-refreshes immediately

# Add a new Python package
# Edit: backend/requirements.txt
docker-compose up -d --build backend

# Add a new npm package
# Edit: frontend/package.json
docker-compose up -d --build frontend

# End of day: Stop containers
docker-compose down
```

Happy coding! 🚀
