# Internship Portal API Usage Guide

This document provides information on how to use the Internship Portal API, including authentication, endpoints, and testing procedures.

## Table of Contents

1. [Authentication](#authentication)
2. [Role-Based Access](#role-based-access)
3. [API Endpoints](#api-endpoints)
4. [Testing with Postman](#testing-with-postman)
5. [Error Handling](#error-handling)
6. [Development Tools](#development-tools)

## Authentication

The API uses JSON Web Tokens (JWT) for authentication. To access protected endpoints, you need to:

1. Obtain a JWT token by logging in
2. Include the token in the `Authorization` header of your requests

### Login Example

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"registration_no": "2013XXXXX", "password": "your_password"}'
```

The response will include a JWT token:

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer"
}
```

### Using the Token

Include the token in your requests:

```bash
curl -X GET http://localhost:5000/api/dashboard \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

## Role-Based Access

The API uses role-based access control to serve appropriate content based on the user's role. The system automatically detects whether a user is a student, faculty, or admin based on their JWT token.

### Available Roles

- **Student**: Regular student users with access to their profile, dashboard, etc.
- **Faculty**: Faculty members with access to student records, analytics, etc.
- **Admin**: Administrative users with full system access

## API Endpoints

### General Endpoints

- `GET /`: API root showing service status
- `GET /api/debug`: Debug information about the API and database

### Authentication Endpoints

- `POST /auth/login`: Login to get JWT token
- `POST /auth/register`: Register a new account

### Dashboard Endpoints

- `GET /api/dashboard`: Get dashboard data based on user role
- `GET /api/dashboard/stats`: Get statistical data for the dashboard

### Profile Endpoints

- `GET /api/profile`: Get profile data for the current user
- `PUT /api/profile`: Update profile information

### Utility Endpoints

- `GET /api/firebase-test`: Test the Firebase connection
- `POST /api/populate-dummy-data`: Populate the database with dummy data for testing

## Testing with Postman

A Postman collection is included in the repository (`postman_collection.json`) for easy testing of API endpoints.

### Setting Up Postman

1. Import the collection into Postman
2. Set the `baseUrl` variable to your API URL (default: `http://localhost:5000`)
3. Use the login request to get a JWT token
4. Copy the token to the `jwt_token` collection variable

### Testing Flow

1. Send the login request and get your token
2. Test the dashboard endpoint
3. Test the profile endpoint
4. Try other endpoints as needed

## Error Handling

The API uses standard HTTP status codes and returns structured error responses:

### Example Error Response

```json
{
  "status": "error",
  "error": "Unauthorized access",
  "message": "You do not have permission to access this resource"
}
```

### Common Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required or failed
- `403 Forbidden`: Authenticated but not authorized
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

## Development Tools

### Populating Test Data

To quickly populate the database with test data for development:

```bash
curl -X POST http://localhost:5000/api/populate-dummy-data \
  -H "Authorization: Bearer your_jwt_token"
```

This will create:
- 5 student profiles
- 3 companies
- Multiple applications
- 5 announcements

### Checking Firebase Integration

To verify Firebase integration is working:

```bash
curl -X GET http://localhost:5000/api/firebase-test \
  -H "Authorization: Bearer your_jwt_token"
```

### Running Tests

To run the automated tests:

```bash
cd internship-portal
pytest
``` 