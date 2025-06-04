# API Testing Guide

This directory contains tests for the internship portal API endpoints. The main test file is `test_api_endpoints.py`, which contains comprehensive tests for all API endpoints in the application.

## Test Structure

The tests are organized by API category:
- Authentication tests
- Admin tests
- Student tests
- Company tests
- Search tests
- Faculty tests
- Recommendations tests
- Analytics tests

Each test verifies the correct functioning of a specific API endpoint, including proper status codes and response data.

## Prerequisites

Before running the tests, ensure you have:
1. MongoDB running locally on the default port (27017)
2. The application dependencies installed
3. Test configuration properly set up in `app/config.py`

## Running the Tests

To run all the tests, use the following command from the project root:

```bash
python -m pytest tests/test_api_endpoints.py -v
```

To run a specific test, you can specify the test name:

```bash
python -m pytest tests/test_api_endpoints.py::APITestCase::test_2_auth_login -v
```

## Test Database

The tests use a separate test database configuration defined in `app/config.py` as `TestConfig`. This ensures that your production or development data is not affected by the tests.

During test setup, the test database collections are dropped and populated with test data. This includes:
- Test students
- Test companies
- Test announcements
- Test applications

## Authentication

The tests use JWT authentication. Test users are created during setup:
- Student user: TEST123/testpassword
- Admin user: admin/admin@savi

## HTML Report Generation

You can generate an HTML report of the test results by running:

```bash
python tests/run_tests.py
```

This will run all the tests and generate both a JSON and HTML report in the tests directory.

## Notes

- Some tests depend on the results of previous tests. For example, company application tests need a company ID from a previous test.
- Tests are numbered to ensure they run in the correct order.
- Some tests may fail if the API behavior changes or if the test data doesn't match the expected format.
- If a test fails, check the error message for details on what went wrong. 