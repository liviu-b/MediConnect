# MediConnect

A modern healthcare appointment scheduling platform built with React and FastAPI.

## 🏥 Overview

MediConnect is a comprehensive medical appointment management system that connects patients with healthcare providers. The platform supports multiple medical centers, doctors, and staff members with role-based access control and multi-location management.

## ✨ Features

### For Patients
- 🗓️ **Easy Appointment Booking** - Schedule appointments with doctors 24/7
- 📱 **Patient Dashboard** - View upcoming appointments and medical history
- 📋 **Medical Records** - Access prescriptions and medical documents
- 🔍 **Search Medical Centers** - Find healthcare facilities by location and specialty
- 🌍 **Multi-language Support** - Available in English and Romanian

### For Medical Centers
- 🏢 **Multi-Location Management** - Manage multiple clinic locations
- 👨‍⚕️ **Doctor Management** - Add and manage medical staff
- 📊 **Dashboard & Analytics** - Monitor appointments and performance
- ⏰ **Operating Hours** - Configure clinic and doctor availability
- 💼 **Service Management** - Define medical services and pricing
- 🔐 **Role-Based Access Control** - Granular permissions for staff

### For Doctors & Staff
- 📅 **Personal Schedule** - Manage availability and appointments
- 👥 **Patient Management** - View patient history and records
- 💊 **Prescriptions** - Create and manage prescriptions
- 📝 **Medical Documents** - Generate recommendations and medical letters
- 🔔 **Notifications** - Stay updated on appointments

### For Super Admins
- 🏛️ **Organization Management** - Oversee multiple organizations
- 📍 **Location Management** - Manage all medical center locations
- 🔑 **Access Requests** - Approve/reject access requests to organizations
- 👥 **User Management** - Manage all users across the platform

## 🛠️ Technology Stack

### Frontend
- **React 19** - UI framework
- **React Router DOM** - Client-side routing and navigation
- **Tailwind CSS** - Utility-first CSS framework for styling
- **Radix UI** - Accessible component primitives
- **Lucide React** - Icon library
- **i18next** - Internationalization and multi-language support
- **Axios** - HTTP client for API requests
- **date-fns** - Modern date utility library
- **FullCalendar** - Calendar and scheduling component
- **React Hook Form** - Form validation and management
- **Zod** - TypeScript-first schema validation
- **Sonner** - Toast notifications
- **CRACO** - Create React App Configuration Override

### Backend
- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL document database
- **Motor** - Async MongoDB driver for Python
- **Pydantic** - Data validation using Python type annotations
- **PyJWT** - JSON Web Token implementation
- **Python-Jose** - JavaScript Object Signing and Encryption
- **Passlib** - Password hashing library
- **Bcrypt** - Password hashing algorithm
- **Uvicorn** - ASGI server
- **Python-dotenv** - Environment variable management
- **Resend** - Email service integration

## 📋 Prerequisites

- **Node.js** (v16 or higher)
- **Python** (v3.9 or higher)
- **PostgreSQL** (v13 or higher)
- **Git**

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd MediConnect
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/mediconnect
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Initialize Database

```bash
# Run migrations
alembic upgrade head

# Initialize permissions (optional)
python init_permissions_db.py
```

#### Start Backend Server

```bash
# Development
uvicorn app.main:app --reload --port 8000

# Or using the provided script
python server.py
```

The backend API will be available at `http://localhost:8000`

### 3. Frontend Setup

#### Install Node Dependencies

```bash
cd frontend
npm install
```

#### Configure Environment Variables

Create a `.env` file in the `frontend` directory:

```env
REACT_APP_BACKEND_URL=http://localhost:8000
```

#### Start Frontend Development Server

```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## 🐳 Docker Deployment

Docker provides a consistent, isolated environment for running MediConnect, making it easier to deploy and manage across different systems without worrying about dependencies or configuration conflicts.

### Why Use Docker?

- **Consistency** - Same environment across development, testing, and production
- **Isolation** - Each service runs in its own container without conflicts
- **Easy Setup** - No need to manually install Python, Node.js, PostgreSQL, etc.
- **Portability** - Run anywhere Docker is installed
- **Scalability** - Easy to scale services independently
- **Quick Cleanup** - Remove everything with a single command

### Prerequisites

- **Docker** - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** - Usually included with Docker Desktop

### Using Docker Compose (Recommended)

Docker Compose orchestrates multiple containers (frontend, backend, database) as a single application.

#### 🚀 Quick Start

```bash
# Start all services (frontend, backend, database)
docker-compose up -d
```

**What this does:**
- `-d` flag runs containers in detached mode (background)
- Builds images if they don't exist
- Creates and starts all services defined in docker-compose.yml
- Sets up networking between containers
- Creates volumes for persistent data

#### 📊 View Running Containers

```bash
# List all running containers
docker-compose ps

# Expected output:
# NAME                    STATUS              PORTS
# mediconnect-frontend    Up 2 minutes        0.0.0.0:3000->3000/tcp
# mediconnect-backend     Up 2 minutes        0.0.0.0:8000->8000/tcp
# mediconnect-db          Up 2 minutes        0.0.0.0:5432->5432/tcp
```

#### 📝 View Logs

```bash
# View logs from all services
docker-compose logs

# Follow logs in real-time (like tail -f)
docker-compose logs -f

# View logs for specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# View last 100 lines and follow
docker-compose logs -f --tail=100

# View logs with timestamps
docker-compose logs -t
```

**Why view logs:**
- Debug errors and issues
- Monitor application behavior
- Track API requests and responses
- See database queries

#### 🔄 Rebuild Containers

```bash
# Rebuild all services (after code changes)
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build backend
docker-compose up -d --build frontend

# Force rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

**When to rebuild:**
- After changing code
- After updating dependencies (package.json, requirements.txt)
- After modifying Dockerfile
- When containers behave unexpectedly

#### ⏸️ Stop Services

```bash
# Stop all services (containers remain)
docker-compose stop

# Stop specific service
docker-compose stop backend

# Start stopped services
docker-compose start
```

**Difference between stop and down:**
- `stop` - Stops containers but keeps them (quick restart)
- `down` - Stops and removes containers (clean slate)

#### 🗑️ Remove Services

```bash
# Stop and remove all containers
docker-compose down

# Remove containers and volumes (deletes database data!)
docker-compose down -v

# Remove containers, volumes, and images
docker-compose down -v --rmi all
```

**⚠️ Warning:** Using `-v` flag will delete all data in the database!

#### 🔄 Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
```

**When to restart:**
- After environment variable changes
- When service becomes unresponsive
- To apply configuration changes

#### 🔍 Execute Commands in Containers

```bash
# Open bash shell in backend container
docker-compose exec backend bash

# Open bash shell in frontend container
docker-compose exec frontend sh

# Run database migrations
docker-compose exec backend alembic upgrade head

# Create database backup
docker-compose exec db pg_dump -U postgres mediconnect > backup.sql

# Restore database backup
docker-compose exec -T db psql -U postgres mediconnect < backup.sql

# Run Python script in backend
docker-compose exec backend python init_permissions_db.py

# Install new npm package in frontend
docker-compose exec frontend npm install package-name
```

#### 📦 Manage Volumes

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect mediconnect_postgres_data

# Remove unused volumes
docker volume prune

# Remove specific volume (⚠️ deletes data!)
docker volume rm mediconnect_postgres_data
```

**Volumes store:**
- Database data (persistent across container restarts)
- Uploaded files
- Configuration files

### Individual Docker Builds

For more control, you can build and run containers individually.

#### Backend Container

```bash
# Navigate to backend directory
cd backend

# Build the image
docker build -t mediconnect-backend .

# Run the container
docker run -d \
  --name mediconnect-backend \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e SECRET_KEY=your-secret-key \
  mediconnect-backend

# View logs
docker logs mediconnect-backend

# Follow logs
docker logs -f mediconnect-backend

# Stop container
docker stop mediconnect-backend

# Remove container
docker rm mediconnect-backend
```

**Flags explained:**
- `-d` - Run in detached mode (background)
- `--name` - Give container a name
- `-p 8000:8000` - Map port 8000 from container to host
- `-e` - Set environment variable
- `-t` - Tag the image with a name

#### Frontend Container

```bash
# Navigate to frontend directory
cd frontend

# Build the image
docker build -t mediconnect-frontend .

# Run the container
docker run -d \
  --name mediconnect-frontend \
  -p 3000:3000 \
  -e REACT_APP_BACKEND_URL=http://localhost:8000 \
  mediconnect-frontend

# View logs
docker logs mediconnect-frontend

# Stop and remove
docker stop mediconnect-frontend
docker rm mediconnect-frontend
```

#### Database Container

```bash
# Run PostgreSQL container
docker run -d \
  --name mediconnect-db \
  -p 5432:5432 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=mediconnect \
  -v mediconnect_postgres_data:/var/lib/postgresql/data \
  postgres:13

# Connect to database
docker exec -it mediconnect-db psql -U postgres -d mediconnect

# Backup database
docker exec mediconnect-db pg_dump -U postgres mediconnect > backup.sql

# Restore database
docker exec -i mediconnect-db psql -U postgres mediconnect < backup.sql
```

### 🔧 Useful Docker Commands

#### Container Management

```bash
# List all containers (running and stopped)
docker ps -a

# Remove all stopped containers
docker container prune

# Remove specific container
docker rm container-name

# Force remove running container
docker rm -f container-name

# View container resource usage
docker stats

# Inspect container details
docker inspect container-name
```

#### Image Management

```bash
# List all images
docker images

# Remove image
docker rmi image-name

# Remove unused images
docker image prune

# Remove all unused images
docker image prune -a

# View image history
docker history image-name

# Tag an image
docker tag old-name:tag new-name:tag
```

#### Network Management

```bash
# List networks
docker network ls

# Inspect network
docker network inspect mediconnect_default

# Create custom network
docker network create my-network

# Connect container to network
docker network connect my-network container-name
```

#### System Cleanup

```bash
# Remove all unused containers, networks, images
docker system prune

# Remove everything including volumes (⚠️ deletes all data!)
docker system prune -a --volumes

# View disk usage
docker system df
```

### 🐛 Troubleshooting

#### Container Won't Start

```bash
# Check logs for errors
docker-compose logs backend

# Check if port is already in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Remove and recreate container
docker-compose down
docker-compose up -d --build
```

#### Database Connection Issues

```bash
# Check if database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Connect to database manually
docker-compose exec db psql -U postgres -d mediconnect

# Reset database
docker-compose down -v
docker-compose up -d
```

#### Out of Disk Space

```bash
# Check disk usage
docker system df

# Clean up unused resources
docker system prune -a

# Remove old images
docker image prune -a
```

#### Container Keeps Restarting

```bash
# Check logs for crash reason
docker-compose logs --tail=50 backend

# Check container status
docker-compose ps

# Inspect container
docker inspect mediconnect-backend
```

### 📚 Docker Compose File Structure

The `docker-compose.yml` file defines all services:

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:13
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: mediconnect
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Backend API
  backend:
    build: ./backend
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/mediconnect
      SECRET_KEY: your-secret-key
    ports:
      - "8000:8000"

  # Frontend React App
  frontend:
    build: ./frontend
    depends_on:
      - backend
    environment:
      REACT_APP_BACKEND_URL: http://localhost:8000
    ports:
      - "3000:3000"

volumes:
  postgres_data:
```

### 🎯 Best Practices

1. **Use Docker Compose for Development** - Easier to manage multiple services
2. **Use .dockerignore** - Exclude unnecessary files from builds
3. **Use Multi-stage Builds** - Reduce image size
4. **Don't Store Secrets in Images** - Use environment variables
5. **Use Volumes for Data** - Persist data across container restarts
6. **Tag Your Images** - Use version tags for production
7. **Monitor Resource Usage** - Use `docker stats` to check performance
8. **Regular Cleanup** - Remove unused containers and images
9. **Use Health Checks** - Ensure services are running correctly
10. **Backup Volumes** - Regularly backup database volumes

### 🚀 Production Deployment

For production, consider:

```bash
# Build optimized images
docker-compose -f docker-compose.prod.yml build

# Run with production configuration
docker-compose -f docker-compose.prod.yml up -d

# Use environment-specific compose files
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale backend=3

# Update service without downtime
docker-compose up -d --no-deps --build backend
```

### 📖 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)

## 📁 Project Structure

```
MediConnect/
├── backend/
│   ├── app/
│   │   ├── middleware/       # Custom middleware
│   │   ├── routers/          # API endpoints
│   │   ├── schemas/          # Pydantic models
│   │   ├── services/         # Business logic
│   │   ├── config.py         # Configuration
│   │   ├── db.py            # Database setup
│   │   ├── main.py          # FastAPI app
│   │   └── security.py      # Authentication
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── contexts/        # React contexts
│   │   ├── hooks/           # Custom hooks
│   │   ├── i18n/           # Translations
│   │   ├── lib/            # Utilities
│   │   ├── pages/          # Page components
│   │   ├── App.js          # Main app component
│   │   └── index.js        # Entry point
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔐 Authentication & Authorization

### User Roles

- **SUPER_ADMIN** - Full system access, manages organizations
- **CLINIC_ADMIN** - Manages medical center and staff
- **LOCATION_ADMIN** - Manages specific location
- **DOCTOR** - Manages appointments and patient records
- **ASSISTANT** - Assists doctors with appointments
- **STAFF** - General staff access
- **USER** - Patient access

### Authentication Flow

1. User registers or logs in
2. Backend generates JWT token
3. Token stored in session/local storage
4. Token sent with each API request
5. Backend validates token and permissions

## 🌍 Internationalization

The application supports multiple languages:

- **English (en)** - Default
- **Romanian (ro)** - Full translation

### Adding New Languages

1. Create new locale file in `frontend/src/i18n/locales/`
2. Add translations following the existing structure
3. Import in `frontend/src/i18n/index.js`

## 📊 Database Schema

### Main Tables

- **users** - User accounts
- **organizations** - Medical organizations
- **locations** - Medical center locations
- **doctors** - Doctor profiles
- **appointments** - Appointment bookings
- **medical_records** - Patient medical records
- **prescriptions** - Medication prescriptions
- **services** - Medical services offered
- **access_requests** - Organization access requests
- **permissions** - Role-based permissions

## 🔧 API Documentation

Once the backend is running, visit:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - User logout

#### Appointments
- `GET /api/appointments` - List appointments
- `POST /api/appointments` - Create appointment
- `PUT /api/appointments/{id}` - Update appointment
- `DELETE /api/appointments/{id}` - Cancel appointment

#### Medical Centers
- `GET /api/clinics` - List medical centers
- `POST /api/clinics` - Create medical center
- `GET /api/clinics/{id}` - Get medical center details

#### Doctors
- `GET /api/doctors` - List doctors
- `POST /api/doctors` - Add doctor
- `GET /api/doctors/{id}/availability` - Get doctor availability

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 🚀 Deployment

### Production Build

#### Frontend
```bash
cd frontend
npm run build
```

#### Backend
```bash
cd backend
# Set production environment variables
export DATABASE_URL=postgresql://...
export SECRET_KEY=...
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Environment Variables for Production

#### Backend
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key (use strong random string)
- `ALGORITHM` - JWT algorithm (HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time
- `CORS_ORIGINS` - Allowed CORS origins

#### Frontend
- `REACT_APP_BACKEND_URL` - Backend API URL

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Authors

- **ACL-Smart Software** - Initial work

## 🙏 Acknowledgments

- React team for the amazing framework
- FastAPI team for the excellent Python framework
- All contributors and users of MediConnect

## 📞 Support

For support, email support@mediconnect.com or open an issue in the repository.

## 🗺️ Roadmap

- [ ] Mobile app (React Native)
- [ ] Video consultations
- [ ] Payment integration
- [ ] Insurance verification
- [ ] Advanced analytics
- [ ] AI-powered appointment suggestions
- [ ] Multi-tenant architecture improvements
- [ ] Enhanced reporting features

## 📸 Screenshots

### Patient Dashboard
![Patient Dashboard](docs/screenshots/patient-dashboard.png)

### Appointment Booking
![Appointment Booking](docs/screenshots/appointment-booking.png)

### Medical Center Management
![Medical Center Management](docs/screenshots/clinic-management.png)

---

**Made with ❤️ by ACL-Smart Software**
