# HubSpot CRM - Docker Setup

This document provides instructions for running the HubSpot CRM application using Docker containers.

## Prerequisites

- Docker and Docker Compose installed
- HubSpot API token

## Quick Start

### 1. Set Environment Variables

Create a `.env` file in the project root with your HubSpot API token:

```bash
HUBSPOT_API_TOKEN=your_hubspot_api_token_here
```

### 2. Production Setup

Build and run the production containers:

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f
```

### 3. Development Setup

For development with hot-reload and additional tools:

```bash
# Build and start development containers
docker-compose -f docker-compose.dev.yml up --build

# Run in background
docker-compose -f docker-compose.dev.yml up -d --build
```

## Services

### Production Services (`docker-compose.yml`)

- **web**: Flask application (port 5000)
- **postgres**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)

### Development Services (`docker-compose.dev.yml`)

- **web**: Flask application with hot-reload (port 5000)
- **postgres**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)
- **pgadmin**: Database management interface (port 8080)

## Access Points

- **Flask API**: http://localhost:5000
- **Swagger Documentation**: http://localhost:5000/swagger
- **pgAdmin** (dev only): http://localhost:8080
  - Email: admin@hubspot.com
  - Password: admin123

## Database Connection

The application automatically connects to the PostgreSQL database with these credentials:

- Host: `postgres` (container name)
- Database: `hubspot_db`
- Username: `hubspot_user`
- Password: `hubspot_password`

## Useful Commands

### Container Management

```bash
# Start services
docker-compose up

# Stop services
docker-compose down

# Rebuild containers
docker-compose up --build

# View running containers
docker-compose ps

# View logs
docker-compose logs -f web
docker-compose logs -f postgres

# Execute commands in running container
docker-compose exec web python manage.py shell
docker-compose exec postgres psql -U hubspot_user -d hubspot_db
```

### Development Commands

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up

# Run tests
docker-compose exec web python -m pytest

# Database migrations
docker-compose exec web flask db migrate -m "Description"
docker-compose exec web flask db upgrade
```

### Data Management

```bash
# Backup database
docker-compose exec postgres pg_dump -U hubspot_user hubspot_db > backup.sql

# Restore database
docker-compose exec -T postgres psql -U hubspot_user hubspot_db < backup.sql

# Remove all data (volumes)
docker-compose down -v
```

## Environment Variables

### Required

- `HUBSPOT_API_TOKEN`: Your HubSpot API token

### Optional (with defaults)

- `SECRET_KEY`: Flask secret key (auto-generated if not set)
- `FLASK_DEBUG`: Enable debug mode (False in production)
- `DEFAULT_PAGE_SIZE`: Default pagination size (10)
- `MAX_PAGE_SIZE`: Maximum pagination size (100)

## Troubleshooting

### Common Issues

1. **Port already in use**

   ```bash
   # Check what's using the port
   netstat -tulpn | grep :5000

   # Stop conflicting services or change ports in docker-compose.yml
   ```

2. **Database connection issues**

   ```bash
   # Check if postgres is running
   docker-compose ps postgres

   # Check postgres logs
   docker-compose logs postgres
   ```

3. **Permission issues**

   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

4. **Container won't start**

   ```bash
   # Check container logs
   docker-compose logs web

   # Rebuild without cache
   docker-compose build --no-cache
   ```

### Health Checks

The containers include health checks. Check status with:

```bash
docker-compose ps
```

### Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove containers, networks, and volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all
```

## Production Deployment

For production deployment:

1. Use the production docker-compose.yml
2. Set `FLASK_ENV=production`
3. Use strong passwords and secrets
4. Configure proper logging
5. Set up monitoring and backups
6. Use a reverse proxy (nginx) in front of the Flask app

## Security Notes

- Change default passwords in production
- Use environment variables for sensitive data
- Regularly update base images
- Monitor container logs for security issues
- Use secrets management for production deployments
