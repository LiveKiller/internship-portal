# Internship Portal API Documentation

## Overview
This document provides detailed information about the API endpoints, their usage, and test results.

## Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_token>
```

## Base URL
All endpoints are prefixed with `/api`

## Endpoints

### 1. Debug
- **GET** `/debug`
- **Description**: Check database connection and basic info
- **Auth Required**: No
- **Test Status**: ✅ PASSED
- **Response (200)**:
```json
{
    "status": "success",
    "debug_info": {
        "database_name": "string",
        "collections": ["array"],
        "students_count": 0
    }
}
```

### 2. Authentication

#### 2.1 Signup
- **POST** `/auth/signup`
- **Description**: Register a new student user
- **Auth Required**: No
- **Test Status**: ✅ PASSED
- **Request Body**:
```json
{
    "registration_no": "123456789",
    "email": "user@example.com",
    "password": "Password1"
}
```
- **Response (201)**:
```json
{
    "access_token": "string",
    "message": "User registered successfully"
}
```
- **Error (400)**:
```json
{
    "error": "Registration number, email, and password are required"
}
```

#### 2.2 Login
- **POST** `/auth/login`
- **Description**: Login with email and password
- **Auth Required**: No
- **Test Status**: ✅ PASSED
- **Request Body**:
```json
{
    "email_id": "user@example.com",
    "password": "Password1"
}
```
- **Response (200)**:
```json
{
    "access_token": "string",
    "message": "Login successful"
}
```

### 3. Admin Routes

#### 3.1 Admin Login
- **POST** `/admin/login`
- **Description**: Admin authentication
- **Auth Required**: No
- **Test Status**: ✅ PASSED
- **Request Body**:
```json
{
    "username": "savi@admin",
    "password": "admin@savi"
}
```
- **Response (200)**:
```json
{
    "access_token": "string"
}
```

#### 3.2 Admin Dashboard
- **GET** `/admin/dashboard`
- **Description**: Get admin dashboard statistics
- **Auth Required**: Yes (Admin)
- **Test Status**: ✅ PASSED
- **Response (200)**:
```json
{
    "stats": {
        "total_students": 0,
        "total_companies": 0,
        "active_applications": 0
    }
}
```

#### 3.3 Create Company
- **POST** `/admin/companies`
- **Description**: Create a new company listing
- **Auth Required**: Yes (Admin)
- **Test Status**: ✅ PASSED
- **Request Body**:
```json
{
    "name": "TestCo",
    "job_title": "Engineer"
}
```
- **Response (201)**:
```json
{
    "company": {
        "_id": "string",
        "name": "string",
        "job_title": "string"
    }
}
```

#### 3.4 Analytics
- **GET** `/admin/analytics`
- **Description**: Get analytics data for admin dashboard
- **Auth Required**: Yes (Admin)
- **Response (200)**:
```json
{
    "applications_by_date": [
        {"date": "string", "count": 0}
    ],
    "companies_by_industry": [
        {"industry": "string", "count": 0}
    ],
    "students_by_specialization": [
        {"specialization": "string", "count": 0}
    ]
}
```

### 4. Student Routes

#### 4.1 Profile

##### 4.1.1 Get Profile
- **GET** `/profile/`
- **Description**: Get student profile
- **Auth Required**: Yes
- **Test Status**: ✅ PASSED
- **Response (200)**:
```json
{
    "profile": {
        "registration_no": "string",
        "email_id": "string",
        "name": "string"
    }
}
```

##### 4.1.2 Update Profile
- **PUT** `/profile/`
- **Description**: Update student profile
- **Auth Required**: Yes
- **Test Status**: ✅ PASSED
- **Request Body**:
```json
{
    "mobile_no": "1234567890",
    "specialization": "Computer Science",
    "year_of_admission": 2021
}
```
- **Response (200)**:
```json
{
    "message": "Profile updated successfully"
}
```

##### 4.1.3 Upload CV
- **POST** `/profile/upload-cv`
- **Description**: Upload a CV file (PDF only)
- **Auth Required**: Yes
- **Request**: Multipart form data with 'cv' file
- **Response (200)**:
```json
{
    "message": "CV uploaded successfully",
    "filename": "string"
}
```

##### 4.1.4 Download CV
- **GET** `/profile/download-cv`
- **Description**: Download the user's CV
- **Auth Required**: Yes
- **Response**: File download response

##### 4.1.5 Add Experience
- **POST** `/profile/add-experience`
- **Description**: Add new experience to profile
- **Auth Required**: Yes
- **Request Body**:
```json
{
    "company_name": "string",
    "position": "string",
    "start_date": "string",
    "end_date": "string",
    "description": "string",
    "skills_used": ["string"]
}
```
- **Response (201)**:
```json
{
    "message": "Experience added successfully",
    "experience": {
        "company_name": "string",
        "position": "string",
        "start_date": "string",
        "end_date": "string",
        "description": "string",
        "skills_used": ["string"]
    }
}
```

##### 4.1.6 Update Experience
- **PUT** `/profile/update-experience/<index>`
- **Description**: Update an existing experience in profile
- **Auth Required**: Yes
- **Request Body**: Fields to update
- **Response (200)**:
```json
{
    "message": "Experience updated successfully",
    "experience": {}
}
```

##### 4.1.7 Delete Experience
- **DELETE** `/profile/delete-experience/<index>`
- **Description**: Delete an experience from profile
- **Auth Required**: Yes
- **Response (200)**:
```json
{
    "message": "Experience deleted successfully"
}
```

##### 4.1.8 Add Project
- **POST** `/profile/add-project`
- **Description**: Add new project to profile
- **Auth Required**: Yes
- **Request Body**:
```json
{
    "title": "string",
    "description": "string",
    "technologies": ["string"],
    "link": "string"
}
```
- **Response (201)**:
```json
{
    "message": "Project added successfully",
    "project": {}
}
```

##### 4.1.9 Add Certification
- **POST** `/profile/add-certification`
- **Description**: Add new certification to profile
- **Auth Required**: Yes
- **Request Body**:
```json
{
    "name": "string",
    "issuer": "string",
    "date": "string",
    "description": "string"
}
```
- **Response (201)**:
```json
{
    "message": "Certification added successfully",
    "certification": {}
}
```

##### 4.1.10 Upload Certification
- **POST** `/profile/upload-certification/<certification_index>`
- **Description**: Upload certification file
- **Auth Required**: Yes
- **Request**: Multipart form data with 'certificate' file
- **Response (200)**:
```json
{
    "message": "Certification uploaded successfully",
    "filename": "string"
}
```

##### 4.1.11 Update Skills
- **PUT** `/profile/update-skills`
- **Description**: Update skills in profile
- **Auth Required**: Yes
- **Request Body**:
```json
{
    "skills": ["string"]
}
```
- **Response (200)**:
```json
{
    "message": "Skills updated successfully",
    "skills": ["string"]
}
```

#### 4.2 Dashboard
- **GET** `/dashboard`
- **Description**: Get student dashboard data
- **Auth Required**: Yes
- **Response (200)**:
```json
{
    "recent_applications": [],
    "upcoming_interviews": [],
    "recommended_companies": []
}
```

#### 4.3 Announcements
- **GET** `/announcements`
- **Description**: Get all announcements
- **Auth Required**: Yes
- **Response (200)**:
```json
{
    "announcements": [
        {
            "_id": "string",
            "title": "string",
            "content": "string",
            "date": "string"
        }
    ]
}
```

#### 4.4 Portfolio
- **GET** `/portfolio`
- **Description**: Get student portfolio
- **Auth Required**: Yes
- **Response (200)**:
```json
{
    "portfolio": {
        "experience": [],
        "projects": [],
        "certifications": [],
        "skills": []
    }
}
```

#### 4.5 Messages
- **GET** `/messages`
- **Description**: Get student messages
- **Auth Required**: Yes
- **Response (200)**:
```json
{
    "messages": [
        {
            "_id": "string",
            "sender": "string",
            "content": "string",
            "timestamp": "string",
            "read": false
        }
    ]
}
```

#### 4.6 Recommendations
- **GET** `/recommendations`
- **Description**: Get recommended companies for student
- **Auth Required**: Yes
- **Response (200)**:
```json
{
    "recommendations": [
        {
            "_id": "string",
            "name": "string",
            "job_title": "string",
            "match_score": 0
        }
    ]
}
```

### 5. Company Routes

#### 5.1 List Companies
- **GET** `/company/`
- **Description**: Get list of companies
- **Auth Required**: Yes
- **Test Status**: ✅ PASSED
- **Query Parameters**: 
  - `jobType`: Filter by job type
  - `workPlace`: Filter by workplace type
  - `duration`: Filter by internship duration
  - `stipend`: Filter by minimum stipend
  - `postedTime`: Filter by days since posting
  - `page`: Page number for pagination
  - `per_page`: Items per page
- **Response (200)**:
```json
{
    "companies": [
        {
            "_id": "string",
            "name": "string",
            "job_title": "string"
        }
    ],
    "total": 0,
    "page": 1,
    "per_page": 10,
    "pages": 1
}
```

#### 5.2 Get Company Details
- **GET** `/company/{company_id}`
- **Description**: Get detailed information about a specific company
- **Auth Required**: Yes
- **Response (200)**:
```json
{
    "company": {
        "_id": "string",
        "name": "string",
        "job_title": "string",
        "description": "string",
        "requirements": ["string"],
        "benefits": ["string"]
    }
}
```

#### 5.3 Apply to Company
- **POST** `/company/{company_id}/apply`
- **Description**: Submit application to a company
- **Auth Required**: Yes
- **Test Status**: ✅ PASSED
- **Request Body**:
```json
{
    "coverLetter": "string",
    "portfolio": "string",
    "availability": "string",
    "noticePeriod": "string"
}
```
- **Response (201)**:
```json
{
    "message": "Application submitted successfully",
    "application_id": "string"
}
```

#### 5.4 Get Applications
- **GET** `/company/applications`
- **Description**: Get all applications for the current user
- **Auth Required**: Yes
- **Response (200)**:
```json
{
    "applications": [
        {
            "_id": "string",
            "company_id": "string",
            "status": "string",
            "applied_date": "string",
            "company": {
                "name": "string",
                "logo": "string",
                "job_title": "string"
            }
        }
    ]
}
```

#### 5.5 Check Application Status
- **GET** `/company/{company_id}/status`
- **Description**: Get application status
- **Auth Required**: Yes
- **Test Status**: ✅ PASSED
- **Response (200)**:
```json
{
    "status": "pending",
    "application": {
        "_id": "string",
        "status": "string"
    }
}
```

### 6. Search Routes

#### 6.1 Search Companies
- **GET** `/search/companies`
- **Description**: Search companies by keyword
- **Auth Required**: Yes
- **Test Status**: ✅ PASSED
- **Query Parameters**: `q` (search term)
- **Response (200)**:
```json
{
    "companies": [
        {
            "name": "string",
            "job_title": "string"
        }
    ]
}
```

#### 6.2 Search Announcements
- **GET** `/search/announcements`
- **Description**: Search announcements
- **Auth Required**: Yes
- **Test Status**: ✅ PASSED
- **Query Parameters**: `q` (search term)
- **Response (200)**:
```json
{
    "announcements": [
        {
            "_id": "string",
            "title": "string",
            "content": "string"
        }
    ]
}
```

#### 6.3 Search Students
- **GET** `/search/students`
- **Description**: Search students (admin only)
- **Auth Required**: Yes (Admin)
- **Query Parameters**: `q` (search term)
- **Response (200)**:
```json
{
    "students": [
        {
            "_id": "string",
            "registration_no": "string",
            "name": "string",
            "email_id": "string"
        }
    ]
}
```

### 7. Notification Routes

#### 7.1 Get Notifications
- **GET** `/notifications/`
- **Description**: Get user notifications
- **Auth Required**: Yes
- **Test Status**: ✅ PASSED
- **Response (200)**:
```json
{
    "notifications": [
        {
            "_id": "string",
            "title": "string",
            "content": "string",
            "read": false,
            "created_at": "string"
        }
    ]
}
```

#### 7.2 Mark Notification as Read
- **PUT** `/notifications/{notification_id}/read`
- **Description**: Mark a notification as read
- **Auth Required**: Yes
- **Response (200)**:
```json
{
    "message": "Notification marked as read"
}
```

#### 7.3 Mark All Notifications as Read
- **PUT** `/notifications/read-all`
- **Description**: Mark all notifications as read
- **Auth Required**: Yes
- **Response (200)**:
```json
{
    "message": "All notifications marked as read",
    "count": 0
}
```

## Error Handling
All API endpoints follow a consistent error response format:

```json
{
    "error": "Error message description"
}
```

Common HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 409: Conflict
- 422: Unprocessable Entity
- 500: Internal Server Error

## Pagination
List endpoints support pagination with the following query parameters:
- `page`: Page number (default: 1)
- `per_page`: Number of items per page (default: 10)

Paginated responses include:
```json
{
    "items": [],
    "total": 0,
    "page": 1,
    "per_page": 10,
    "pages": 1
}
```

## Test Summary
- Total Tests: 14
- Passed: 14 ✅
- Failed: 0 ❌
- Warning: 1 (Deprecated datetime.utcnow() usage)

### Test Details
1. `test_index` - ✅ PASSED
2. `test_debug` - ✅ PASSED
3. `test_signup_missing_fields` - ✅ PASSED
4. `test_signup_and_login` - ✅ PASSED
5. `test_admin_login_and_dashboard` - ✅ PASSED
6. `test_admin_token_fixture` - ✅ PASSED
7. `test_full_company_and_application_flow` - ✅ PASSED
8. `test_search_endpoints_and_announcements` - ✅ PASSED
9. `test_company_listing` - ✅ PASSED
10. `test_login` - ✅ PASSED
11. `test_notification_system` - ✅ PASSED
12. `test_profile_update` - ✅ PASSED
13. `test_protected_route` - ✅ PASSED
14. `test_signup` - ✅ PASSED

## Notes
- All routes requiring authentication expect a valid JWT token in the Authorization header
- Error responses follow a consistent format with an "error" field containing the error message
- Pagination is implemented for list endpoints with `page` and `per_page` query parameters
- ObjectId values are always returned as strings in responses
- File uploads support PDF and common image formats
- Rate limiting is applied to prevent abuse 