# Internship Portal Backend

A Flask-based RESTful API for managing internship opportunities, student profiles, and company registrations. This system enables students to find internships, build portfolios, and apply to companies, while allowing companies to post opportunities and review applications.

## Features

- **Authentication System**: JWT-based authentication for students, companies, and admins
- **Student Profiles**: Students can create and manage detailed profiles with education, skills, and projects
- **Company Management**: Companies can register, post internship opportunities, and manage applications
- **Admin Dashboard**: Admins can manage users, internships, and system settings
- **Document Management**: Upload and manage resumes, certificates, and other documents
- **Search & Filtering**: Advanced search capabilities for internships and profiles

## Technology Stack

- **Framework**: Flask (Python 3.11+)
- **Database**: MongoDB
- **Authentication**: JWT (JSON Web Tokens)
- **File Storage**: Local storage (production: S3 compatible)
- **API Documentation**: Swagger/OpenAPI
- **Testing**: pytest
- **CI/CD**: GitHub Actions

## Getting Started

### Prerequisites

- Python 3.11 or higher
- MongoDB 6.0 or higher
- Redis (for caching and rate limiting)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/internship-portal-backend.git
   cd internship-portal-backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file with environment variables:
   ```
   MONGO_URI=mongodb://localhost:27017/internship_portal
   JWT_SECRET_KEY=your-secret-key
   UPLOAD_FOLDER=app/uploads
   ADMIN_USERNAME=admin@example.com
   ADMIN_PASSWORD=securepassword
   ADMIN_ACCESS_KEY=admin-access-key
   ```

5. Initialize the database:
   ```bash
   python scripts/initialize_db.py
   ```

### Running the API Server

```bash
python run.py
```

The API will be available at `http://localhost:5000/api`

### Running with Docker

```bash
docker-compose up --build
```

## API Documentation

API documentation is available at `/api/docs` when the server is running.

The main API endpoints include:

- `/api/auth/*` - Authentication endpoints
- `/api/student/*` - Student profile and application endpoints
- `/api/company/*` - Company profile and internship endpoints
- `/api/admin/*` - Admin-only endpoints

## Deployment

Refer to [deployment_guide.md](deployment_guide.md) for detailed deployment instructions.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [MongoDB](https://www.mongodb.com/)
