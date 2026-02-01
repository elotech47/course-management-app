# Quick Start Guide

## For First-Time Setup

### 1. Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit the file with your settings
nano .env  # or vim, or any text editor
```

**Important: Change these values in `.env`:**
- `SECRET_KEY` - Generate a secure random key
- `POSTGRES_PASSWORD` - Set a strong password
- `BACKEND_PORT` - Change if 8000 is in use
- `FRONTEND_PORT` - Change if 3000 is in use
- `VITE_API_URL` - Set to your server IP/domain

### 2. Choose Your Deployment Method

## Option A: Script Deployment (Recommended for direct server deployment)

```bash
# Deploy
./deploy.sh

# Check status
./deploy-status.sh

# View logs
tail -f logs/backend.log logs/frontend.log

# Stop
./deploy-stop.sh
```

## Option B: Docker Deployment (Recommended for containerized deployment)

```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d --build

# Run migrations (first time only)
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop
docker-compose -f docker-compose.prod.yml down
```

---

## Access Your Application

Once deployed, access at:
- **Frontend**: `http://your-server-ip:3000` (or your configured port)
- **Backend API**: `http://your-server-ip:8000` (or your configured port)
- **API Docs**: `http://your-server-ip:8000/docs`

---

## Common Commands

### Script Deployment
```bash
./deploy.sh          # Deploy/restart application
./deploy-stop.sh     # Stop application  
./deploy-status.sh   # Check status
tail -f logs/*.log   # View logs
```

### Docker Deployment
```bash
# Start
docker-compose -f docker-compose.prod.yml up -d

# Stop
docker-compose -f docker-compose.prod.yml down

# Restart
docker-compose -f docker-compose.prod.yml restart

# Logs
docker-compose -f docker-compose.prod.yml logs -f [service_name]

# Update code and redeploy
git pull
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## Troubleshooting

### Port Already in Use?
Edit `.env` and change `BACKEND_PORT` or `FRONTEND_PORT`:
```bash
BACKEND_PORT=8080
FRONTEND_PORT=3001
```

### Can't Connect to Database?
1. Make sure PostgreSQL is running
2. Check `DATABASE_URL` in `.env`
3. Verify database credentials

### Need Help?
See the full [DEPLOYMENT.md](DEPLOYMENT.md) guide for:
- Detailed setup instructions
- Nginx reverse proxy configuration
- SSL/HTTPS setup
- System service configuration
- Performance tuning
- Backup procedures

---

## Next Steps

1. **Register your first user** at the frontend URL
2. **Create a course** and add students
3. **Set up sessions** and assign roles
4. **Start grading** using the digital rubrics
5. **Generate reports** and export data

For production deployment, consider:
- Setting up Nginx reverse proxy
- Configuring SSL certificates
- Setting up automated backups
- Configuring monitoring

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.
