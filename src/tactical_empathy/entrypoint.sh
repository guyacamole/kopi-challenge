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

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Start the application
echo "Starting application..."
exec "$@"
