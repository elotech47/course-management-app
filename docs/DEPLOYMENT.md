# Course Management App - Deployment Guide

## Overview

This application can be deployed using two methods:
1. **Script-based deployment** - Direct deployment on the server
2. **Docker Compose** - Containerized deployment

Both methods support **configurable ports** to avoid conflicts with other services.

---

## Prerequisites

### For Script-Based Deployment
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- nginx or Apache (optional, for reverse proxy)

### For Docker Deployment
- Docker 20.10+
- Docker Compose 2.0+

---

## Configuration

### 1. Create Environment File

Copy the example environment file and customize it:

```bash
cp env.example .env
```

### 2. Edit `.env` File

**Important settings to configure:**

```bash
# Database Configuration
DATABASE_URL=postgresql://course_admin:YOUR_PASSWORD@localhost:5432/course_management
POSTGRES_USER=course_admin
POSTGRES_PASSWORD=YOUR_SECURE_PASSWORD
POSTGRES_DB=course_management
POSTGRES_PORT=5432  # Change if 5432 is in use

# Backend Configuration
BACKEND_PORT=8000   # Change if 8000 is in use
SECRET_KEY=generate-a-secure-random-key-at-least-32-characters-long
ENVIRONMENT=production

# Frontend Configuration
FRONTEND_PORT=3000  # Change if 3000 is in use
VITE_API_URL=http://your-server-ip:8000  # or your domain

# Email Configuration (optional)
SENDGRID_API_KEY=your_sendgrid_api_key
FROM_EMAIL=noreply@yourdomain.com
```

### 3. Generate a Secure Secret Key

```bash
# Using Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Or using OpenSSL
openssl rand -base64 32
```

---

## Method 1: Script-Based Deployment

### Initial Setup

1. **Clone the repository** (if not already done):
```bash
git clone <your-repo-url>
cd course-management-app
```

2. **Configure environment**:
```bash
cp env.example .env
nano .env  # Edit with your settings
```

3. **Setup PostgreSQL**:
```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create user and database
CREATE USER course_admin WITH PASSWORD 'your_password';
CREATE DATABASE course_management OWNER course_admin;
GRANT ALL PRIVILEGES ON DATABASE course_management TO course_admin;
\q
```

4. **Make scripts executable**:
```bash
chmod +x deploy.sh deploy-stop.sh deploy-status.sh
```

### Deploy the Application

```bash
./deploy.sh
```

This script will:
- ✓ Check port availability
- ✓ Verify PostgreSQL connection
- ✓ Set up Python virtual environment
- ✓ Install backend dependencies
- ✓ Run database migrations
- ✓ Start backend server (with 4 workers)
- ✓ Build frontend for production
- ✓ Start frontend server

### Manage the Application

**Check status:**
```bash
./deploy-status.sh
```

**Stop the application:**
```bash
./deploy-stop.sh
```

**View logs:**
```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log
```

**Restart the application:**
```bash
./deploy-stop.sh
./deploy.sh
```

### Setting Up as System Service (Optional but Recommended)

Create systemd service files for automatic startup:

**Backend service** (`/etc/systemd/system/course-management-backend.service`):
```ini
[Unit]
Description=Course Management Backend
After=network.target postgresql.service

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/course-management-app/backend
Environment="PATH=/path/to/course-management-app/backend/venv/bin"
EnvironmentFile=/path/to/course-management-app/.env
ExecStart=/path/to/course-management-app/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${BACKEND_PORT} --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Frontend service** (`/etc/systemd/system/course-management-frontend.service`):
```ini
[Unit]
Description=Course Management Frontend
After=network.target course-management-backend.service

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/course-management-app/frontend/dist
EnvironmentFile=/path/to/course-management-app/.env
ExecStart=/usr/local/bin/serve -s . -l ${FRONTEND_PORT}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start services:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable course-management-backend
sudo systemctl enable course-management-frontend
sudo systemctl start course-management-backend
sudo systemctl start course-management-frontend

# Check status
sudo systemctl status course-management-backend
sudo systemctl status course-management-frontend
```

---

## Method 2: Docker Compose Deployment

### Deploy with Docker Compose

1. **Configure environment**:
```bash
cp env.example .env
nano .env  # Edit with your settings
```

2. **Build and start containers**:
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

3. **Run database migrations** (first time only):
```bash
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### Manage Docker Deployment

**View logs:**
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

**Stop containers:**
```bash
docker-compose -f docker-compose.prod.yml down
```

**Restart containers:**
```bash
docker-compose -f docker-compose.prod.yml restart
```

**Update and redeploy:**
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build
```

**View container status:**
```bash
docker-compose -f docker-compose.prod.yml ps
```

**Access container shell:**
```bash
# Backend
docker-compose -f docker-compose.prod.yml exec backend bash

# Frontend
docker-compose -f docker-compose.prod.yml exec frontend sh
```

---

## Nginx Reverse Proxy (Recommended for Production)

### Configure Nginx

Create `/etc/nginx/sites-available/course-management`:

```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**Enable the site:**
```bash
sudo ln -s /etc/nginx/sites-available/course-management /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL with Let's Encrypt (HTTPS)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com
```

---

## Port Configuration Examples

### Scenario 1: Ports 8000 and 3000 are free
```bash
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

### Scenario 2: Different ports needed
```bash
BACKEND_PORT=8080
FRONTEND_PORT=3001
```
Update VITE_API_URL accordingly:
```bash
VITE_API_URL=http://your-server-ip:8080
```

### Scenario 3: Using Nginx reverse proxy
```bash
# App runs on custom ports
BACKEND_PORT=8080
FRONTEND_PORT=3001

# Nginx listens on 80/443 and proxies to these ports
# Update VITE_API_URL to use nginx proxy
VITE_API_URL=https://api.yourdomain.com
```

---

## Troubleshooting

### Port Already in Use

**Find process using port:**
```bash
# Linux/Mac
lsof -i :8000
sudo netstat -tulpn | grep :8000

# Kill process
kill -9 <PID>
```

### Database Connection Issues

**Check PostgreSQL status:**
```bash
sudo systemctl status postgresql

# Test connection
psql "$DATABASE_URL" -c "SELECT 1"
```

**Check database logs:**
```bash
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### Backend Not Starting

**Check logs:**
```bash
# Script deployment
tail -f logs/backend.log

# Docker deployment
docker-compose -f docker-compose.prod.yml logs backend
```

**Common issues:**
- Database not accessible
- Port already in use
- Missing environment variables
- Dependencies not installed

### Frontend Not Building

**Check Node.js version:**
```bash
node --version  # Should be 18+
```

**Clear cache and rebuild:**
```bash
cd frontend
rm -rf node_modules dist
npm install
npm run build
```

### Docker Issues

**View all logs:**
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

**Rebuild from scratch:**
```bash
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## Performance Tuning

### Backend Workers

Adjust the number of Uvicorn workers based on CPU cores:
```bash
# In deploy.sh or systemd service
uvicorn app.main:app --workers $(( $(nproc) * 2 ))
```

### Frontend Caching

The nginx configuration includes optimal caching headers for static assets.

### Database Connection Pool

Edit `backend/app/db/database.py` if needed:
```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=40
)
```

---

## Backup and Maintenance

### Database Backup

```bash
# Create backup
pg_dump "$DATABASE_URL" > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
psql "$DATABASE_URL" < backup_20260101_120000.sql
```

### Automated Daily Backups

Add to crontab (`crontab -e`):
```bash
0 2 * * * cd /path/to/course-management-app && pg_dump "$DATABASE_URL" > backups/backup_$(date +\%Y\%m\%d).sql
```

### Log Rotation

Create `/etc/logrotate.d/course-management`:
```
/path/to/course-management-app/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 your-username your-username
    sharedscripts
}
```

---

## Security Checklist

- [ ] Change default SECRET_KEY to a strong random value
- [ ] Use strong PostgreSQL password
- [ ] Set up firewall (ufw/iptables)
- [ ] Enable HTTPS with SSL certificate
- [ ] Keep system and dependencies updated
- [ ] Set up regular database backups
- [ ] Configure fail2ban for SSH protection
- [ ] Use environment-specific .env files (never commit to git)
- [ ] Enable database query logging in production
- [ ] Set up monitoring and alerting

---

## Monitoring

### Basic Health Checks

**Backend health:**
```bash
curl http://localhost:8000/docs
```

**Frontend health:**
```bash
curl http://localhost:3000
```

### Application Logs

```bash
# Script deployment
tail -f logs/backend.log logs/frontend.log

# Docker deployment
docker-compose -f docker-compose.prod.yml logs -f
```

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review application logs
3. Verify .env configuration
4. Check system resources (CPU, RAM, disk)

---

## Quick Reference

### Script Deployment Commands
```bash
./deploy.sh          # Deploy application
./deploy-stop.sh     # Stop application
./deploy-status.sh   # Check status
```

### Docker Commands
```bash
docker-compose -f docker-compose.prod.yml up -d --build    # Deploy
docker-compose -f docker-compose.prod.yml down             # Stop
docker-compose -f docker-compose.prod.yml logs -f          # View logs
docker-compose -f docker-compose.prod.yml ps               # Status
```

### Access URLs
- Frontend: `http://localhost:${FRONTEND_PORT}`
- Backend API: `http://localhost:${BACKEND_PORT}`
- API Documentation: `http://localhost:${BACKEND_PORT}/docs`
