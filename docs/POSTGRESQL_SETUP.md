# PostgreSQL Setup Guide for macOS

## Current Issue
PostgreSQL is installed but the server is not running.

## Solution: Start PostgreSQL

### Option 1: Using Homebrew Services (Recommended)

```bash
# Start PostgreSQL (runs in background, auto-starts on boot)
brew services start postgresql@17

# Or if you have a different version:
brew services start postgresql
```

### Option 2: Start Manually (temporary)

```bash
# Find your PostgreSQL data directory
# Usually: /opt/homebrew/var/postgresql@17 or /opt/homebrew/var/postgres

# Start server manually
postgres -D /opt/homebrew/var/postgresql@17
```

### Option 3: Use Postgres.app (Alternative)

Download from: https://postgresapp.com/
- Easier GUI management
- Starts automatically

## After Starting PostgreSQL

### 1. Create Database and User

```bash
# Connect to PostgreSQL (will use your Mac username)
psql postgres

# In psql prompt, run these commands:
CREATE DATABASE course_management;
CREATE USER course_admin WITH PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE course_management TO course_admin;

# Exit
\q
```

### 2. Update Backend Configuration

Edit `backend/.env`:

```bash
DATABASE_URL=postgresql://course_admin:67U2fXTtAa4P@localhost:5432/course_management
```

Or use your Mac username (no password needed):

```bash
DATABASE_URL=postgresql://elotech@localhost:5432/course_management
```

### 3. Initialize Database Tables

```bash
cd backend
source venv/bin/activate  # If not already activated
python -c "from app.db import models; from app.db.database import engine; models.Base.metadata.create_all(bind=engine)"
```

## Quick Commands Reference

```bash
# Check if PostgreSQL is running
pg_isready

# List all databases
psql -l

# Connect to a specific database
psql course_management

# Stop PostgreSQL
brew services stop postgresql

# Restart PostgreSQL
brew services restart postgresql

# Check PostgreSQL status
brew services list | grep postgresql
```

## Troubleshooting

### "role postgres does not exist"
This means PostgreSQL was installed without creating the default `postgres` superuser.
Solution: Use your Mac username instead, or create the postgres role:

```bash
createuser -s postgres
```

### "database elotech does not exist"
When you run `psql` without arguments, it tries to connect to a database named after your username.
Solution: Create it or specify a database:

```bash
createdb elotech
# OR
psql postgres  # Connect to the default postgres database
```

### Permission Issues
If you get permission errors:

```bash
# Make sure you own the PostgreSQL data directory
sudo chown -R $(whoami) /opt/homebrew/var/postgresql@17
```

## Quick Setup Script

Run this after starting PostgreSQL:

```bash
#!/bin/bash

# Create database
createdb course_management

# Create tables
cd backend
source venv/bin/activate
python -c "from app.db import models; from app.db.database import engine; models.Base.metadata.create_all(bind=engine)"

echo "Database setup complete!"
echo "Update your backend/.env with:"
echo "DATABASE_URL=postgresql://$(whoami)@localhost:5432/course_management"
```

## Next Steps

1. Start PostgreSQL: `brew services start postgresql`
2. Wait 5 seconds for it to start
3. Run: `psql postgres` (should work now)
4. Create database and tables (see above)
5. Start your backend: `cd backend && uvicorn app.main:app --reload`
