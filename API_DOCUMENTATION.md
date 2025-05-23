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

### 4. Student Routes

#### 4.1 Profile
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

#### 4.2 Update Profile
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

### 5. Company Routes

#### 5.1 List Companies
- **GET** `/company/`
- **Description**: Get list of companies
- **Auth Required**: Yes
- **Test Status**: ✅ PASSED
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
    "per_page": 10
}
```

#### 5.2 Apply to Company
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

#### 5.3 Check Application Status
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
            "read": false
        }
    ]
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