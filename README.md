# CV Project

A modern Django-based CV management system with PDF generation, email functionality, AI-powered analysis, and Docker deployment. Perfect for job applications and professional CV management.

## ✨ Features

- 📝 **CV Management**: Create, edit, and manage professional CVs
- 📄 **PDF Generation**: Generate beautiful PDFs with custom styling
- 📧 **Email Integration**: Send CVs via email with PDF attachments
- 🤖 **AI Analysis**: OpenAI-powered CV analysis and suggestions
- 🌐 **Translation**: Multi-language CV translation support
- 📊 **Analytics**: Request logging and usage statistics
- 🔄 **Async Processing**: Background tasks with Celery and Redis
- 🐳 **Docker Support**: Fast, optimized Docker setup
- 📱 **Responsive UI**: Modern, mobile-friendly interface
- 🔐 **Authentication**: User registration and login system

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

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Tk4V/cv_library.git
cd cv_library
```

### 2. Environment Setup

Copy the example environment file and configure:

```bash
cp env.dev.example .env
```

Edit `.env` file with your settings:

```bash
# Django Settings
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database (Docker handles this)
DATABASE_URL=postgresql://postgres:postgres@db:5432/cvdb
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

    # OpenAI (Optional - for AI features)
    OPENAI_API_KEY=your-openai-api-key
    OPENAI_MODEL=gpt-3.5-turbo

    # SendGrid Email (Optional - for email features)
    # Get your API key from https://app.sendgrid.com/settings/api_keys
    # Verify your sender at https://app.sendgrid.com/settings/sender_auth/senders
    SENDGRID_API_KEY=your-sendgrid-api-key
    SENDGRID_FROM_EMAIL=your-verified-email@example.com
```

### 3. Start the Application

```bash
# Start all services with optimized Docker setup
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

### 4. Access the Application

- **Web Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/ (admin/admin123)

### 5. Sample Data

The application comes with **3 sample CVs** pre-loaded for immediate testing and demonstration.

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

## 📡 API Endpoints

### CV Management
- `GET /api/cv/` - List all CVs
- `POST /api/cv/` - Create new CV
- `GET /api/cv/{id}/` - Get CV details
- `PUT /api/cv/{id}/` - Update CV
- `DELETE /api/cv/{id}/` - Delete CV

### Logs & Analytics
- `GET /api/logs/` - View request logs
- `GET /api/logs/?since=2024-01-01&until=2024-12-31` - Filter logs by date

### Web Interface
- `GET /` - Home page
- `GET /cvs/` - CV list page
- `GET /cv/create/` - Create CV form
- `GET /cv/{id}/` - CV detail page
- `GET /cv/{id}/edit/` - Edit CV form
- `GET /login/` - Login page
- `GET /register/` - Registration page

## 📁 Project Structure

```
cv_library/
├── CVProject/                    # Django project settings
│   ├── settings/                # Environment-specific settings
│   └── celery.py               # Celery configuration
├── main/                        # Main Django app
│   ├── api/                    # REST API views and serializers
│   ├── fixtures/               # Sample data fixtures
│   │   └── sample_cvs.json     # 3 sample CVs for demo
│   ├── models.py               # Database models
│   ├── services.py             # Business logic services
│   ├── templates/              # HTML templates
│   └── web/                    # Web views
├── celery_tasks/               # Celery tasks and services
│   ├── tasks/                  # Background tasks
│   └── services/               # Task services
├── docker-compose.dev.yml      # Development Docker setup
├── docker-compose.prod.yml     # Production Docker setup
├── Dockerfile                  # Optimized Docker image
├── entrypoint.sh              # Docker entrypoint script
├── env.dev.example            # Development environment template
└── README.md                  # This file
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
