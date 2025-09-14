#!/bin/bash

# Exit on any error
set -e

# Function to wait for PostgreSQL
wait_for_postgres() {
    echo "Waiting for PostgreSQL to be ready..."
    while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
        echo "PostgreSQL is not ready yet. Waiting..."
        sleep 2
    done
    echo "PostgreSQL is ready!"
}

# Function to create database if it doesn't exist
create_database() {
    echo "Checking if database '$DB_NAME' exists..."
    # Use PGPASSWORD to set password for psql commands
    export PGPASSWORD=$DB_PASSWORD
    
    if ! psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1; then
        echo "Database '$DB_NAME' does not exist. Creating..."
        psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE \"$DB_NAME\";"
        echo "Database '$DB_NAME' created successfully!"
    else
        echo "Database '$DB_NAME' already exists."
    fi
}

# Wait for PostgreSQL
wait_for_postgres

# Create database if it doesn't exist
create_database

# Verify database connection
echo "Verifying database connection..."
export PGPASSWORD=$DB_PASSWORD
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT version();" > /dev/null
echo "Database connection verified successfully!"

# Run database migrations using dbmate
echo "Running database migrations with dbmate..."
# URL encode the password to handle special characters
ENCODED_PASSWORD=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${DB_PASSWORD}', safe=''))")
export DATABASE_URL="postgres://${DB_USER}:${ENCODED_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}?sslmode=disable"

# Try to run dbmate migrations
if ! dbmate up; then
    echo "WARNING: dbmate migrations failed. Attempting to create tables manually..."
    export PGPASSWORD=$DB_PASSWORD
    if psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f ./db/create_tables.sql; then
        echo "Tables created successfully using fallback method!"
    else
        echo "ERROR: Failed to create tables using fallback method!"
        exit 1
    fi
else
    echo "dbmate migrations completed successfully!"
fi

# Verify that required tables exist
echo "Verifying that required tables exist..."
export PGPASSWORD=$DB_PASSWORD
TABLES_EXIST=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "
    SELECT COUNT(*) FROM information_schema.tables 
    WHERE table_name IN ('roles', 'conversations', 'messages') 
    AND table_schema = 'public'
" | tr -d ' ')

if [ "$TABLES_EXIST" -eq "3" ]; then
    echo "✓ All required tables exist!"
else
    echo "✗ Missing tables detected. Expected 3, found $TABLES_EXIST"
    echo "Attempting to create missing tables..."
    export PGPASSWORD=$DB_PASSWORD
    if psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f ./db/create_tables.sql; then
        echo "✓ Tables created successfully!"
    else
        echo "✗ Failed to create tables!"
        exit 1
    fi
fi

# Start the application
echo "Starting application..."
exec "$@"
