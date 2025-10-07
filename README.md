# CV Project

A Django-based CV management system with PDF generation, email functionality, and AI-powered analysis features.

## Features

- 📝 **CV Management**: Create, edit, and manage CVs
- 📄 **PDF Generation**: Generate professional PDFs of your CVs
- 📧 **Email Integration**: Send CVs via email with PDF attachments
- 🤖 **AI Analysis**: AI-powered CV analysis and suggestions
- 🌐 **Translation**: Multi-language CV translation support
- 📊 **Analytics**: Request logging and statistics
- 🔄 **Async Processing**: Background tasks with Celery
- 🐳 **Docker Support**: Easy deployment with Docker Compose

## Tech Stack

- **Backend**: Django 5.2, Django REST Framework
- **Database**: PostgreSQL
- **Cache/Queue**: Redis
- **Task Queue**: Celery
- **PDF Generation**: xhtml2pdf
- **AI Integration**: OpenAI API
- **Containerization**: Docker, Docker Compose
- **Monitoring**: Flower (Celery monitoring)

## Prerequisites

- Docker and Docker Compose
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd CVProject
```

### 2. Environment Setup

Create a `.env` file in the project root:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (for local development)
DATABASE_URL=sqlite:///db.sqlite3

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email Configuration - Gmail SMTP
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your-email@gmail.com

# OpenAI (Optional)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_PROJECT=your-openai-project-id
```

### 3. Gmail Setup (for Email Functionality)

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification**
3. Go to **App passwords** → **Mail**
4. Generate a new App Password
5. Update `EMAIL_HOST_PASSWORD` in your `.env` file

### 4. Start the Application

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 5. Access the Application

- **Web Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/schema/swagger-ui/
- **Celery Monitoring**: http://localhost:5555

## Development Setup

### Local Development (without Docker)

1. **Install Dependencies**:
   ```bash
   pip install poetry
   poetry install
   ```

2. **Database Setup**:
   ```bash
   poetry run python manage.py migrate
   poetry run python manage.py createsuperuser
   ```

3. **Start Services**:
   ```bash
   # Terminal 1: Django server
   poetry run python manage.py runserver

   # Terminal 2: Celery worker
   poetry run celery -A CVProject worker --loglevel=info

   # Terminal 3: Celery beat (optional)
   poetry run python manage.py run_celery_beat
   ```

### Running Tests

```bash
# With Docker
docker exec cvproject-web-1 python manage.py test

# Local development
poetry run python manage.py test
```

## API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout

### CV Management
- `GET /api/cvs/` - List all CVs
- `POST /api/cvs/` - Create new CV
- `GET /api/cvs/{id}/` - Get CV details
- `PUT /api/cvs/{id}/` - Update CV
- `DELETE /api/cvs/{id}/` - Delete CV

### Email
- `POST /api/cvs/{id}/email/` - Send CV via email

### Analysis
- `POST /api/cvs/{id}/analyze/` - Analyze CV with AI

## Project Structure

```
CVProject/
├── CVProject/              # Django project settings
│   ├── settings/           # Environment-specific settings
│   └── celery.py          # Celery configuration
├── main/                   # Main Django app
│   ├── api/               # REST API views and serializers
│   ├── models.py          # Database models
│   ├── services.py        # Business logic services
│   ├── templates/         # HTML templates
│   └── web/               # Web views
├── celery_tasks/          # Celery tasks and services
│   ├── tasks/             # Background tasks
│   └── services/          # Task services
├── docker-compose.yml     # Docker services configuration
├── Dockerfile            # Docker image definition
└── .env                  # Environment variables
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required |
| `DJANGO_DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `DATABASE_URL` | Database connection | `sqlite:///db.sqlite3` |
| `EMAIL_HOST_USER` | Gmail username | Required for email |
| `EMAIL_HOST_PASSWORD` | Gmail App Password | Required for email |
| `OPENAI_API_KEY` | OpenAI API key | Optional |

## Docker Services

- **web**: Django application server
- **worker**: Celery worker for background tasks
- **beat**: Celery beat scheduler
- **flower**: Celery monitoring interface
- **db**: PostgreSQL database
- **redis**: Redis cache and message broker

## Email Configuration

The application supports multiple email backends:

### Gmail (Recommended)
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

### SendGrid
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
EMAIL_USE_TLS=True
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**:
   ```bash
   docker-compose down
   docker-compose up -d
   docker exec cvproject-web-1 python manage.py migrate
   ```

2. **Email Not Sending**:
   - Check Gmail App Password is correct
   - Ensure 2-Step Verification is enabled
   - Verify email credentials in `.env` file

3. **Celery Tasks Not Running**:
   ```bash
   docker-compose logs worker
   docker-compose restart worker
   ```

4. **Permission Errors**:
   ```bash
   docker-compose down
   docker system prune -f
   docker-compose up -d
   ```

### Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs web
docker-compose logs worker
docker-compose logs db
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Search existing [Issues](https://github.com/your-repo/issues)
3. Create a new issue with detailed information

## Changelog

### v1.0.0
- Initial release
- CV management system
- PDF generation
- Email functionality
- AI analysis integration
- Docker support
