# Internship Portal API Documentation

This document provides comprehensive documentation for all the API endpoints available in the Internship Portal application.

## Base URL

Production API base URL: `https://internship-portal-backend.onrender.com`
All API endpoints are prefixed with: `/api`

For example: `https://internship-portal-backend.onrender.com/api/auth/login`

## Environment Setup

The API requires the following environment variables to be set:
- `MONGO_URI`: MongoDB connection string
- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `UPLOAD_FOLDER`: Path for file uploads (default: app/uploads)

## Authentication

Most endpoints require authentication using JWT (JSON Web Tokens). To authenticate:

1. Obtain a token by logging in through `/api/auth/login` or `/api/admin/login`
2. Include the token in the Authorization header: `Authorization: Bearer <your_token>`

## Authentication Endpoints

### Student Authentication

#### Register a New Student

- **URL**: `/api/auth/signup`
- **Method**: `POST`
- **Authentication**: None
- **Request Body**:
  ```json
  {
    "registration_no": "STUDENTID",
    "name": "Student Name",
    "email": "student@example.com",
    "password": "password123",
    "department": "Computer Science"
  }
  ```
- **Success Response**:
  - **Code**: `201`
  - **Content**:
    ```json
    {
      "message": "User registered successfully",
      "access_token": "jwt_token_here"
    }
    ```
- **Error Responses**:
  - **Code**: `400` - Invalid inputs
  - **Code**: `409` - User already exists

#### Student Login

- **URL**: `/api/auth/login`
- **Method**: `POST`
- **Authentication**: None
- **Request Body**:
  ```json
  {
    "email_id": "student@example.com",
    "password": "password123"
  }
  ```
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "message": "Login successful",
      "access_token": "jwt_token_here"
    }
    ```
- **Error Responses**:
  - **Code**: `400` - Missing credentials
  - **Code**: `401` - Invalid credentials
  - **Code**: `404` - User not found

#### Check Authentication Status

- **URL**: `/api/auth/check-auth`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "authenticated": true,
      "user": "STUDENTID"
    }
    ```

#### Logout

- **URL**: `/api/auth/logout`
- **Method**: `POST`
- **Authentication**: Required
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "message": "Successfully logged out"
    }
    ```

#### Request Password Reset

- **URL**: `/api/auth/reset-password-request`
- **Method**: `POST`
- **Authentication**: None
- **Request Body**:
  ```json
  {
    "email_id": "student@example.com"
  }
  ```
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "message": "If your email is registered, you will receive a reset link"
    }
    ```

### Admin Authentication

#### Admin Login

- **URL**: `/api/admin/login`
- **Method**: `POST`
- **Authentication**: None
- **Request Body**:
  ```json
  {
    "username": "admin",
    "password": "admin123"
  }
  ```
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "message": "Login successful",
      "access_token": "jwt_token_here"
    }
    ```
- **Error Responses**:
  - **Code**: `401` - Invalid credentials

## Student Endpoints

### Dashboard

#### Get Dashboard Data

- **URL**: `/api/dashboard`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "user": {
        "registration_no": "STUDENTID",
        "name": "Student Name",
        "email_id": "student@example.com",
        ...
      },
      "recent_announcements": [
        {
          "_id": "announcement_id",
          "title": "Announcement Title",
          "content": "Announcement content",
          "date": 1620000000
        },
        ...
      ],
      "stats": {
        "unread_messages": 5,
        "upcoming_interviews": 2,
        "active_companies": 10,
        "applied_companies": 3,
        "rejected_companies": 1,
        "interviews_attended": 2,
        "interviews_not_attended": 0
      }
    }
    ```

#### Get Dashboard Stats Only

- **URL**: `/api/dashboard/stats`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "stats": {
        "unread_messages": 5,
        "upcoming_interviews": 2,
        "active_companies": 10,
        "applied_companies": 3,
        "rejected_companies": 1,
        "interviews_attended": 2,
        "interviews_not_attended": 0
      }
    }
    ```

#### Get Upcoming Deadlines

- **URL**: `/api/dashboard/upcoming-deadlines`
- **Method**: `GET`
- **Authentication**: Required
- **Query Parameters**:
  - `limit` (optional): Number of companies to return (default: 5)
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "companies": [
        {
          "_id": "company_id",
          "name": "Company Name",
          "description": "Company Description",
          "deadline": 1620000000,
          ...
        },
        ...
      ],
      "count": 5
    }
    ```

### Student Profile

#### Get Student Profile

- **URL**: `/api/profile`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "registration_no": "STUDENTID",
      "name": "Student Name",
      "email_id": "student@example.com",
      "mobile_no": "1234567890",
      "date_of_birth": "2000-01-01",
      "gender": "Male",
      ...
    }
    ```

#### Update Student Profile

- **URL**: `/api/profile`
- **Method**: `PUT`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "name": "Updated Name",
    "mobile_no": "9876543210",
    "date_of_birth": "2000-01-01",
    "gender": "Male",
    ...
  }
  ```
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "message": "Profile updated successfully",
      "user": {
        "registration_no": "STUDENTID",
        "name": "Updated Name",
        ...
      }
    }
    ```

#### Upload CV

- **URL**: `/api/profile/cv`
- **Method**: `POST`
- **Authentication**: Required
- **Content-Type**: `multipart/form-data`
- **Request Body**:
  - `cv_file`: PDF file
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "message": "CV uploaded successfully",
      "file_path": "/uploads/cv/filename.pdf"
    }
    ```
- **Error Responses**:
  - **Code**: `400` - Invalid file type or size

#### Update Skills

- **URL**: `/api/profile/skills`
- **Method**: `PUT`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "technical": ["Python", "JavaScript", "React"],
    "non_technical": ["Communication", "Team Work"]
  }
  ```
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "message": "Skills updated successfully",
      "skills": {
        "technical": ["Python", "JavaScript", "React"],
        "non_technical": ["Communication", "Team Work"]
      }
    }
    ```

### Student Portfolio

#### Get Student Portfolio

- **URL**: `/api/portfolio`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "projects": [...],
      "education": {...},
      "experience": [...],
      "skills": {...},
      "certifications": [...]
    }
    ```

#### Add Project

- **URL**: `/api/portfolio/projects`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "title": "Project Title",
    "description": "Project Description",
    "technologies": ["React", "Node.js"],
    "url": "https://github.com/username/project",
    "start_date": 1620000000,
    "end_date": 1630000000
  }
  ```
- **Success Response**:
  - **Code**: `201`
  - **Content**:
    ```json
    {
      "message": "Project added successfully",
      "project": {
        "id": "project_id",
        "title": "Project Title",
        ...
      }
    }
    ```

#### Add Experience

- **URL**: `/api/portfolio/experience`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "company": "Company Name",
    "position": "Position",
    "description": "Job Description",
    "start_date": 1620000000,
    "end_date": 1630000000,
    "is_current": false
  }
  ```
- **Success Response**:
  - **Code**: `201`
  - **Content**:
    ```json
    {
      "message": "Experience added successfully",
      "experience": {
        "id": "experience_id",
        "company": "Company Name",
        ...
      }
    }
    ```

#### Add Certification

- **URL**: `/api/portfolio/certifications`
- **Method**: `POST`
- **Authentication**: Required
- **Content-Type**: `multipart/form-data`
- **Request Body**:
  - `title`: Certification Title
  - `issuing_organization`: Organization Name
  - `issue_date`: Issue Date (timestamp)
  - `expiry_date`: Expiry Date (timestamp) (optional)
  - `credential_id`: Credential ID (optional)
  - `credential_url`: Credential URL (optional)
  - `certification_file`: PDF/Image file (optional)
- **Success Response**:
  - **Code**: `201`
  - **Content**:
    ```json
    {
      "message": "Certification added successfully",
      "certification": {
        "id": "certification_id",
        "title": "Certification Title",
        ...
      }
    }
    ```

### Announcements

#### Get All Announcements

- **URL**: `/api/announcements`
- **Method**: `GET`
- **Authentication**: Required
- **Query Parameters**:
  - `page` (optional): Page number (default: 1)
  - `limit` (optional): Items per page (default: 10)
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "announcements": [
        {
          "_id": "announcement_id",
          "title": "Announcement Title",
          "content": "Announcement content",
          "date": 1620000000,
          "attachments": [...]
        },
        ...
      ],
      "total": 25,
      "page": 1,
      "limit": 10,
      "pages": 3
    }
    ```

#### Get Announcement by ID

- **URL**: `/api/announcements/<announcement_id>`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "_id": "announcement_id",
      "title": "Announcement Title",
      "content": "Announcement content",
      "date": 1620000000,
      "attachments": [...]
    }
    ```
- **Error Responses**:
  - **Code**: `404` - Announcement not found

### Notifications

#### Get All Notifications

- **URL**: `/api/notifications`
- **Method**: `GET`
- **Authentication**: Required
- **Query Parameters**:
  - `page` (optional): Page number (default: 1)
  - `limit` (optional): Items per page (default: 10)
  - `unread_only` (optional): Show only unread notifications (default: false)
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "notifications": [
        {
          "_id": "notification_id",
          "message": "Notification message",
          "type": "announcement",
          "reference_id": "announcement_id",
          "date": 1620000000,
          "read": false
        },
        ...
      ],
      "total": 25,
      "page": 1,
      "limit": 10,
      "pages": 3
    }
    ```

#### Mark Notification as Read

- **URL**: `/api/notifications/<notification_id>/read`
- **Method**: `PUT`
- **Authentication**: Required
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "message": "Notification marked as read"
    }
    ```
- **Error Responses**:
  - **Code**: `404` - Notification not found

#### Mark All Notifications as Read

- **URL**: `/api/notifications/read-all`
- **Method**: `PUT`
- **Authentication**: Required
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "message": "All notifications marked as read",
      "count": 5
    }
    ```

### Messages

#### Get All Conversations

- **URL**: `/api/messages/conversations`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "conversations": [
        {
          "participant_id": "USER_ID",
          "participant_name": "User Name",
          "last_message": "Message content",
          "last_message_time": 1620000000,
          "unread_count": 2
        },
        ...
      ]
    }
    ```

#### Get Conversation Messages

- **URL**: `/api/messages/conversation/<participant_id>`
- **Method**: `GET`
- **Authentication**: Required
- **Query Parameters**:
  - `page` (optional): Page number (default: 1)
  - `limit` (optional): Items per page (default: 20)
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "messages": [
        {
          "_id": "message_id",
          "sender_id": "SENDER_ID",
          "recipient_id": "RECIPIENT_ID",
          "content": "Message content",
          "timestamp": 1620000000,
          "read": true
        },
        ...
      ],
      "total": 50,
      "page": 1,
      "limit": 20,
      "pages": 3
    }
    ```

#### Send Message

- **URL**: `/api/messages`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "recipient_id": "RECIPIENT_ID",
    "content": "Message content"
  }
  ```
- **Success Response**:
  - **Code**: `201`
  - **Content**:
    ```json
    {
      "message": "Message sent successfully",
      "message_data": {
        "_id": "message_id",
        "sender_id": "SENDER_ID",
        "recipient_id": "RECIPIENT_ID",
        "content": "Message content",
        "timestamp": 1620000000,
        "read": false
      }
    }
    ```

#### Mark Conversation as Read

- **URL**: `/api/messages/read/<participant_id>`
- **Method**: `PUT`
- **Authentication**: Required
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "message": "Messages marked as read",
      "count": 5
    }
    ```

## Company Endpoints

### Get All Companies

- **URL**: `/api/companies`
- **Method**: `GET`
- **Authentication**: Required
- **Query Parameters**:
  - `page` (optional): Page number (default: 1)
  - `limit` (optional): Items per page (default: 10)
  - `active_only` (optional): Show only active companies (default: false)
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "companies": [
        {
          "_id": "company_id",
          "name": "Company Name",
          "description": "Company Description",
          "logo": "logo_url",
          "website": "company_website",
          "industry": "Industry",
          "active": true,
          "positions": [...],
          "deadline": 1620000000
        },
        ...
      ],
      "total": 25,
      "page": 1,
      "limit": 10,
      "pages": 3
    }
    ```

### Get Company by ID

- **URL**: `/api/companies/<company_id>`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "_id": "company_id",
      "name": "Company Name",
      "description": "Company Description",
      "logo": "logo_url",
      "website": "company_website",
      "industry": "Industry",
      "active": true,
      "positions": [
        {
          "title": "Software Engineer",
          "description": "Job description",
          "requirements": ["Requirement 1", "Requirement 2"],
          "salary_range": {
            "min": 500000,
            "max": 800000
          }
        }
      ],
      "deadline": 1620000000,
      "contact_person": "Contact Person",
      "contact_email": "contact@company.com",
      "contact_phone": "1234567890"
    }
    ```
- **Error Responses**:
  - **Code**: `404` - Company not found

### Apply to Company

- **URL**: `/api/companies/<company_id>/apply`
- **Method**: `POST`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "position_id": "position_id",
    "cover_letter": "Cover letter content",
    "use_uploaded_cv": true
  }
  ```
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "message": "Application submitted successfully",
      "application": {
        "company_id": "company_id",
        "student_id": "STUDENTID",
        "position_id": "position_id",
        "status": "pending",
        "application_date": 1620000000
      }
    }
    ```
- **Error Responses**:
  - **Code**: `400` - Already applied or deadline passed
  - **Code**: `404` - Company or position not found

## Admin Endpoints

### Dashboard Analytics

- **URL**: `/api/admin/analytics/dashboard`
- **Method**: `GET`
- **Authentication**: Admin Required
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "total_students": 500,
      "total_companies": 25,
      "active_companies": 10,
      "applications": {
        "total": 750,
        "pending": 200,
        "accepted": 300,
        "rejected": 250
      },
      "interviews": {
        "scheduled": 150,
        "completed": 100,
        "no_show": 20
      },
      "recent_activities": [...]
    }
    ```

### Student Management

#### Get All Students

- **URL**: `/api/admin/students`
- **Method**: `GET`
- **Authentication**: Admin Required
- **Query Parameters**:
  - `page` (optional): Page number (default: 1)
  - `limit` (optional): Items per page (default: 20)
  - `department` (optional): Filter by department
  - `year` (optional): Filter by passing out year
  - `search` (optional): Search by name or registration number
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "students": [
        {
          "registration_no": "STUDENTID",
          "name": "Student Name",
          "email_id": "student@example.com",
          "department": "Computer Science",
          "pass_out_year": 2023,
          "profile_completion": 85
        },
        ...
      ],
      "total": 500,
      "page": 1,
      "limit": 20,
      "pages": 25
    }
    ```

#### Get Student Details

- **URL**: `/api/admin/students/<registration_no>`
- **Method**: `GET`
- **Authentication**: Admin Required
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "registration_no": "STUDENTID",
      "name": "Student Name",
      "email_id": "student@example.com",
      "mobile_no": "1234567890",
      "department": "Computer Science",
      "pass_out_year": 2023,
      "profile": {...},
      "portfolio": {...},
      "applications": [...]
    }
    ```
- **Error Responses**:
  - **Code**: `404` - Student not found

### Company Management

#### Add New Company

- **URL**: `/api/admin/companies`
- **Method**: `POST`
- **Authentication**: Admin Required
- **Request Body**:
  ```json
  {
    "name": "Company Name",
    "description": "Company Description",
    "website": "company_website",
    "industry": "Industry",
    "active": true,
    "positions": [
      {
        "title": "Software Engineer",
        "description": "Job description",
        "requirements": ["Requirement 1", "Requirement 2"],
        "salary_range": {
          "min": 500000,
          "max": 800000
        }
      }
    ],
    "deadline": 1620000000,
    "contact_person": "Contact Person",
    "contact_email": "contact@company.com",
    "contact_phone": "1234567890"
  }
  ```
- **Success Response**:
  - **Code**: `201`
  - **Content**:
    ```json
    {
      "message": "Company added successfully",
      "company": {
        "_id": "company_id",
        "name": "Company Name",
        ...
      }
    }
    ```

#### Update Company

- **URL**: `/api/admin/companies/<company_id>`
- **Method**: `PUT`
- **Authentication**: Admin Required
- **Request Body**:
  ```json
  {
    "name": "Updated Company Name",
    "description": "Updated description",
    ...
  }
  ```
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "message": "Company updated successfully",
      "company": {
        "_id": "company_id",
        "name": "Updated Company Name",
        ...
      }
    }
    ```
- **Error Responses**:
  - **Code**: `404` - Company not found

#### Deactivate Company

- **URL**: `/api/admin/companies/<company_id>/deactivate`
- **Method**: `PUT`
- **Authentication**: Admin Required
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "message": "Company deactivated successfully"
    }
    ```
- **Error Responses**:
  - **Code**: `404` - Company not found

### Announcement Management

#### Create Announcement

- **URL**: `/api/admin/announcements`
- **Method**: `POST`
- **Authentication**: Admin Required
- **Content-Type**: `multipart/form-data`
- **Request Body**:
  - `title`: Announcement Title
  - `content`: Announcement Content
  - `attachments[]`: Attachment files (optional)
- **Success Response**:
  - **Code**: `201`
  - **Content**:
    ```json
    {
      "message": "Announcement created successfully",
      "announcement": {
        "_id": "announcement_id",
        "title": "Announcement Title",
        "content": "Announcement content",
        "date": 1620000000,
        "attachments": [...]
      }
    }
    ```

#### Update Announcement

- **URL**: `/api/admin/announcements/<announcement_id>`
- **Method**: `PUT`
- **Authentication**: Admin Required
- **Request Body**:
  ```json
  {
    "title": "Updated Title",
    "content": "Updated content"
  }
  ```
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "message": "Announcement updated successfully",
      "announcement": {
        "_id": "announcement_id",
        "title": "Updated Title",
        ...
      }
    }
    ```
- **Error Responses**:
  - **Code**: `404` - Announcement not found

#### Delete Announcement

- **URL**: `/api/admin/announcements/<announcement_id>`
- **Method**: `DELETE`
- **Authentication**: Admin Required
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "message": "Announcement deleted successfully"
    }
    ```
- **Error Responses**:
  - **Code**: `404` - Announcement not found

## Search Endpoints

### Search Companies

- **URL**: `/api/search/companies`
- **Method**: `GET`
- **Authentication**: Required
- **Query Parameters**:
  - `query` (required): Search query
  - `page` (optional): Page number (default: 1)
  - `limit` (optional): Items per page (default: 10)
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "results": [
        {
          "_id": "company_id",
          "name": "Company Name",
          "description": "Company Description",
          ...
        },
        ...
      ],
      "total": 5,
      "page": 1,
      "limit": 10,
      "pages": 1
    }
    ```

### Search Students

- **URL**: `/api/search/students`
- **Method**: `GET`
- **Authentication**: Admin Required
- **Query Parameters**:
  - `query` (required): Search query
  - `page` (optional): Page number (default: 1)
  - `limit` (optional): Items per page (default: 10)
- **Success Response**:
  - **Code**: `200`
  - **Content**:
    ```json
    {
      "results": [
        {
          "registration_no": "STUDENTID",
          "name": "Student Name",
          "email_id": "student@example.com",
          ...
        },
        ...
      ],
      "total": 15,
      "page": 1,
      "limit": 10,
      "pages": 2
    }
    ```

## Error Codes

The API uses standard HTTP status codes:

- `200` - OK: The request has succeeded
- `201` - Created: A new resource has been created
- `400` - Bad Request: The request was invalid or cannot be served
- `401` - Unauthorized: Authentication is required and has failed or not been provided
- `403` - Forbidden: The server understood the request but refuses to authorize it
- `404` - Not Found: The requested resource could not be found
- `409` - Conflict: The request conflicts with the current state of the server
- `500` - Internal Server Error: The server encountered an unexpected condition

## Rate Limiting

The API implements rate limiting to prevent abuse. If you exceed the rate limit, you will receive a `429 Too Many Requests` response. 