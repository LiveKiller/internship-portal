# Project Structure

This document outlines the structure of the internship portal backend application.

## Directory Structure

```
internship-portal/
├── app/
│   ├── __init__.py           # Main application initialization
│   ├── config.py             # Application configuration
│   ├── archive/              # Archived functionality (for backward compatibility)
│   │   ├── __init__.py
│   │   └── messages.py       # Archived messages functionality
│   ├── auth/                 # Authentication module
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── utils.py
│   ├── models/               # Database models
│   │   ├── __init__.py
│   │   └── student.py
│   ├── routes/               # API routes (standardized structure)
│   │   ├── __init__.py
│   │   └── api/
│   │       ├── admin/
│   │       │   ├── admin_routes.py
│   │       │   └── analytics_routes.py
│   │       ├── auth/
│   │       │   └── auth_routes.py
│   │       ├── company/
│   │       │   └── company_routes.py
│   │       ├── faculty/
│   │       │   └── dashboard_routes.py
│   │       ├── search/
│   │       │   └── search_routes.py
│   │       └── student/
│   │           ├── __init__.py
│   │           ├── routes.py
│   │           ├── dashboard_routes.py
│   │           ├── profile_routes.py
│   │           ├── portfolio_routes.py
│   │           ├── notifications_routes.py
│   │           ├── recommendations_routes.py
│   │           ├── announcement_routes.py
│   │           └── messages_routes.py
│   ├── templates/            # HTML templates
│   ├── uploads/              # Upload directories
│   │   ├── announcements/
│   │   ├── certifications/
│   │   └── cv/
│   └── utils/                # Utility functions
│       ├── __init__.py
│       ├── file_utils.py
│       └── firebase_setup.py
├── scripts/                  # Utility scripts
├── tests/                    # Test cases
├── .gitignore
├── requirements.txt          # Python dependencies
└── wsgi.py                   # WSGI entry point
```

## Blueprint Structure

The application uses Flask blueprints to organize routes. All blueprints now follow a consistent naming convention and URL prefix structure:

### Main Blueprints:
- `api_bp`: Main API blueprint (`/api`)
- `auth_bp`: Authentication blueprint (`/auth`)

### Student Module Blueprints (all under /api/student):
- `student_bp`: Main student operations (`/api/student`)
- `student_dashboard_bp`: Student dashboard (`/api/student/dashboard`)
- `student_profile_bp`: Student profile management (`/api/student/profile`)
- `student_portfolio_bp`: Student portfolio (`/api/student/portfolio`)
- `student_notifications_bp`: Student notifications (`/api/student/notifications`)
- `student_recommendations_bp`: Student recommendations (`/api/student/recommendations`)
- `student_announcements_bp`: Student announcements (`/api/student/announcements`)
- `message_bp`: Student messages (legacy, points to archived implementation) (`/api/student/messages`)

### Other Role-Based Blueprints:
- `faculty_dashboard_bp`: Faculty dashboard (`/api/faculty/dashboard`)
- `company_bp`: Company operations (`/api/company`)
- `admin_bp`: Admin operations (`/api/admin`)
- `analytics_bp`: Admin analytics (`/api/admin/analytics`)
- `search_bp`: Search functionality (`/api/search`)

### Archive Blueprints:
- `archived_messages_bp`: Archived messages functionality (`/student/messages`)

## Best Practices

1. **Blueprint Naming**: Each blueprint has a unique, descriptive name to avoid conflicts
2. **URL Prefixes**: All URL prefixes follow the pattern `/api/<role>/<feature>` for consistency
3. **Route Organization**: Routes are grouped by user role (student, faculty, admin, company)
4. **Blueprint Registration**: All blueprints are registered directly on the app instance
5. **File Naming**: Route files are named descriptively with a `_routes.py` suffix
6. **Backward Compatibility**: Legacy endpoints are preserved through the archive module 