# Full-Stack Todo App with Docker

This project demonstrates a complete Docker setup with:

- **Backend**: FastAPI with PostgreSQL database
- **Frontend**: React with Vite
- **Orchestration**: Docker Compose

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│   Frontend  │────▶│  Backend    │────▶│  PostgreSQL  │
│  (React)    │     │  (FastAPI)  │     │  (Database)  │
└─────────────┘     └─────────────┘     └──────────────┘
    :3000               :8000               :5432
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- macOS, Linux, or Windows (with Docker Desktop)

### Build and Run

1. **Clone or navigate to the project directory**:

   ```bash
   cd docker-lesson
   ```

2. **Copy environment variables** (optional - defaults are provided):

   ```bash
   cp .env.example .env
   ```

3. **Build and start all services**:

   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API Docs: http://localhost:8000/docs
   - Backend Health: http://localhost:8000/health

### Services

#### Frontend (React + Vite)

- Port: 3000
- Accessible at http://localhost:3000
- Hot-reloading enabled in development mode

#### Backend (FastAPI)

- Port: 8000
- API Endpoints:
  - `GET /` - API status
  - `GET /health` - Health check
  - `GET /todos` - List all todos
  - `GET /todos/{id}` - Get specific todo
  - `POST /todos` - Create new todo
  - `PUT /todos/{id}` - Update todo
  - `DELETE /todos/{id}` - Delete todo
- Swagger UI: http://localhost:8000/docs

#### Database (PostgreSQL)

- Port: 5432
- Default credentials (from .env):
  - Username: postgres
  - Password: password
  - Database: todos_db

## Docker Compose Features

- **Service Dependencies**: Backend waits for PostgreSQL to be healthy
- **Health Checks**: All services have health checks configured
- **Volume Mounts**:
  - PostgreSQL data persists in named volume `postgres_data`
  - Backend code mounted for hot-reload
- **Environment Variables**: Configurable via `.env` file
- **Networking**: Custom bridge network for inter-service communication
- **CORS**: Backend configured to accept requests from frontend

## Docker Concepts Covered

1. **Building Images**: Multi-stage build for React frontend
2. **Container Dependencies**: Backend waits for PostgreSQL health
3. **Volume Management**:
   - Named volumes for data persistence
   - Bind mounts for development
4. **Environment Configuration**: Database credentials via .env
5. **Container Networking**: Services communicate over custom network
6. **Health Checks**: Monitors service readiness
7. **Logging**: Services log to stdout (visible with `docker-compose logs`)

## Common Commands

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Build images without starting
docker-compose build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View running services
docker-compose ps

# Execute command in running container
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec postgres psql -U postgres
```

## Development Workflow

### Adding new dependencies to backend

1. Update `backend/requirements.txt`
2. Rebuild: `docker-compose up --build`

### Adding new dependencies to frontend

1. Update `frontend/package.json`
2. Rebuild: `docker-compose up --build`

### Accessing the database

```bash
docker-compose exec postgres psql -U postgres -d todos_db
```

### Viewing logs for specific service

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

## Production Considerations (Next Steps)

- Replace `allow_origins=["*"]` with specific domains
- Use secrets manager for sensitive variables
- Implement database migrations with Alembic
- Add nginx reverse proxy
- Implement CI/CD pipeline
- Use Kubernetes for orchestration at scale

## Troubleshooting

**Frontend can't connect to backend**

- Check if backend is running: `docker-compose ps`
- Verify network: `docker-compose exec frontend ping backend`
- Check logs: `docker-compose logs backend`

**Database connection errors**

- Verify PostgreSQL is healthy: `docker-compose ps`
- Check logs: `docker-compose logs postgres`
- Verify DB_PASSWORD in .env matches POSTGRES_PASSWORD

**Port conflicts**

- Change ports in `docker-compose.yml`
- Or stop other services using those ports

## Learning Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

## Built with GitHub Copilot

This project was built with the assistance of GitHub Copilot Agent, demonstrating the power of AI-assisted development for rapid prototyping and learning Docker containerization patterns.
