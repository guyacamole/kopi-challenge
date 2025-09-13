FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including postgresql-client and dbmate
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && curl -fsSL -o /usr/local/bin/dbmate https://github.com/amacneil/dbmate/releases/latest/download/dbmate-linux-amd64 \
    && chmod +x /usr/local/bin/dbmate \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY ./src/tactical_empathy/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django app source code
COPY ./src/tactical_empathy .

# Copy .env file from root context
COPY .env .

RUN ls -la

# Remove database operations from build time - they'll run at runtime
# RUN python manage.py migrate

RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Make sure entrypoint script is executable
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "tactical_empathy.wsgi:application", "--bind", "0.0.0.0:8000"]