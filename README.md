# Kopi Challenge - Tactical Empathy Debate Bot

A Django-based API service that powers a persuasive debate chatbot capable of maintaining and defending any given position through tactical empathy and strategic argumentation.

## Project Overview

This project implements a debate chatbot API that can:
- Start new conversations with any debate topic
- Take and defend any assigned stance, no matter how controversial
- Maintain coherent, persuasive arguments across multiple message exchanges
- Use multiple AI providers (OpenAI GPT, Google Gemini, DeepSeek) for response generation
- Store conversation history and maintain context

## API Interface

### Endpoint
```
POST /conversation/api/chat/
```

### Request Format
```typescript
{
    "conversation_id": "text" | null,  // null for new conversations
    "message": "text"                   // user's message
}
```

### Response Format
```typescript
{
    "conversation_id": "text",          // UUID of the conversation
    "message": [                        // 5 most recent messages, newest last
        {
            "role": "user",
            "message": "text"
        },
        {
            "role": "bot", 
            "message": "text"
        }
    ]
}
```

### Starting a Conversation

The first message to the API should:
1. **Not include** a `conversation_id` (or set it to `null`)
2. **Define the topic** and **what stance the bot should take**

Example:
```json
{
    "conversation_id": null,
    "message": "Let's debate whether the Earth is flat. You should argue that the Earth is indeed flat."
}
```

### API Features

- **Conversation Length**: Optimized for 5+ message exchanges
- **Stance Persistence**: Bot maintains its assigned position throughout the conversation
- **Persuasive AI**: Uses advanced prompting techniques for compelling arguments

## Environment Variables

Create a `.env` file in the project root with the following variables:

### Required Variables
```bash
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=tactical_empathy
DB_HOST=postgres
DB_PORT=5432

# Application Configuration
APP_NAME=tactical_empathy_app
APP_PORT=8000
SECRET_KEY=your_django_secret_key_here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# AI Provider Configuration (choose one or more)
AI_PROVIDER=openai  # Options: openai, gemini, deepseek

# OpenAI Configuration (if using OpenAI)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo

# Google Gemini Configuration (if using Gemini)
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-pro

# DeepSeek Configuration (if using DeepSeek)
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
```

### Optional Variables
```bash
# AI Response Configuration
AI_MAX_TOKENS=500
AI_TEMPERATURE=0.8
AI_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Make (for build commands)
- An API key for at least one AI provider

### Setup
1. Clone the repository
2. Copy `env.example` to `.env` and configure your settings
3. Run the application:

```bash
make install  # Install dependencies and check requirements
make run      # Start all services
```

The API will be available at `http://localhost:8000/conversation/api/chat/`

## Available Make Commands

```bash
make          # Show all available commands
make install  # Install requirements and check dependencies
make test     # Run the test suite
make run      # Start all services with Docker Compose
make down     # Stop all running services
make clean    # Stop and remove all containers, networks, and volumes
```

## Architecture

### Technology Stack
- **Backend**: Django 4.2 with Django REST Framework
- **Database**: PostgreSQL 16
- **AI Integration**: Multiple providers (OpenAI, Gemini, DeepSeek)
- **Containerization**: Docker and Docker Compose
- **Web Server**: Gunicorn with WhiteNoise for static files

### Project Structure
```
src/tactical_empathy/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── tactical_empathy/           # Main Django project
│   ├── settings.py             # Application configuration
│   ├── urls.py                 # Root URL configuration
│   └── wsgi.py                 # WSGI application
└── mirror/                     # Main application
    ├── models.py               # Database models
    ├── api_views.py            # API endpoints
    ├── ai_service.py           # AI response generation
    ├── ai_providers.py         # AI provider implementations
    ├── urls.py                 # Application URLs
    └── migrations/             # Database migrations
```

### Key Components

1. **Conversation Management**: Tracks debate topics and bot stances
2. **Message History**: Stores and retrieves conversation context
3. **AI Integration**: Pluggable AI providers for response generation
4. **Debate Engine**: Maintains argument consistency and persuasiveness

## Testing

Run the comprehensive test suite:
```bash
make test
```

Tests include:
- API endpoint functionality
- AI provider integration
- Database model validation
- Conversation flow logic
- Error handling scenarios

## Deployment

### Docker Deployment
The application is fully containerized and ready for deployment:

```bash
# Production deployment
docker-compose up -d
```

### Environment Considerations
- Set `DEBUG=False` for production
- Configure `ALLOWED_HOSTS` with your domain
- Use strong `SECRET_KEY` and database passwords
- Consider rate limiting for the API endpoint

## API Usage Examples

### Starting a New Debate
```bash
curl -X POST http://localhost:8000/conversation/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": null,
    "message": "I think climate change is not caused by humans. Convince me that human activity is the primary driver of climate change."
  }'
```

### Continuing a Conversation
```bash
curl -X POST http://localhost:8000/conversation/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "your-conversation-uuid-here",
    "message": "But what about natural climate variations throughout history?"
  }'
```

## Development

### Local Development Setup
1. Install Python 3.11+
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r src/tactical_empathy/requirements.txt`
5. Set up environment variables
6. Run migrations: `python manage.py migrate`
7. Start development server: `python manage.py runserver`

### Contributing
- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting

## License

This project is created for the Kopi coding challenge.

## Support

For issues or questions regarding the implementation, please refer to the code documentation or create an issue in the repository.
