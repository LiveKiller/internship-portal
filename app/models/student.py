"""
Student model and schema validation for MongoDB.
"""
from pymongo import MongoClient
from pymongo.errors import OperationFailure

from app import db

def create_student_schema_validator():
    """
    Creates and applies the JSON schema validator for the student collection.
    This ensures data consistency and required fields.
    """
    student_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "name",
                "roll_number",
                "registration_no",
                "date_of_birth",
                "gender",
                "category",
                "caste",
                "aadhar_no",
                "parivar_pehchan_patra_id",
                "blood_group",
                "disability",
                "mobile_no",
                "email_id",
                "address",
                "father",
                "mother",
                "specialization",
                "registered",
                "pass_out_year",
                "year_of_admission",
                "marks",
                "attendance",
                "experience",
                "skills",
                "projects",
                "education",
                "cv",
                "companies",
                "certifications",
                "messages"
            ],
            "properties": {
                "name": {
                    "bsonType": "string",
                    "description": "Student's full name"
                },
                "roll_number": {
                    "bsonType": "string",
                    "description": "Unique roll number"
                },
                "registration_no": {
                    "bsonType": "string",
                    "description": "University registration number"
                },
                "password": {
                    "bsonType": "binData",
                    "description": "Hashed password"
                },
                "date_of_birth": {
                    "bsonType": "string",
                    "description": "Date of birth (YYYY-MM-DD)"
                },
                "gender": {
                    "bsonType": "string",
                    "enum": [
                        "Male",
                        "Female",
                        "Other"
                    ],
                    "description": "Gender"
                },
                "category": {
                    "bsonType": "string",
                    "description": "Category (General, OBC, SC, ST, etc.)"
                },
                "caste": {
                    "bsonType": "string",
                    "description": "Caste of the student"
                },
                "aadhar_no": {
                    "bsonType": "string",
                    "description": "Aadhar number"
                },
                "parivar_pehchan_patra_id": {
                    "bsonType": "string",
                    "description": "Parivar Pehchan Patra ID"
                },
                "blood_group": {
                    "bsonType": "string",
                    "description": "Blood group"
                },
                "disability": {
                    "bsonType": "string",
                    "enum": [
                        "Yes",
                        "No"
                    ],
                    "description": "Disability status"
                },
                "mobile_no": {
                    "bsonType": "string",
                    "description": "Student's mobile number"
                },
                "email_id": {
                    "bsonType": "string",
                    "description": "Student's email ID"
                },
                "address": {
                    "bsonType": "object",
                    "required": [
                        "street",
                        "pin",
                        "district",
                        "state",
                        "country"
                    ],
                    "properties": {
                        "street": {
                            "bsonType": "string",
                            "description": "Street address"
                        },
                        "pin": {
                            "bsonType": "string",
                            "description": "PIN code"
                        },
                        "district": {
                            "bsonType": "string",
                            "description": "District"
                        },
                        "state": {
                            "bsonType": "string",
                            "description": "State"
                        },
                        "country": {
                            "bsonType": "string",
                            "description": "Country"
                        }
                    }
                },
                "father": {
                    "bsonType": "object",
                    "required": [
                        "name",
                        "mobile_no",
                        "email_id"
                    ],
                    "properties": {
                        "name": {
                            "bsonType": "string",
                            "description": "Father's name"
                        },
                        "mobile_no": {
                            "bsonType": "string",
                            "description": "Father's mobile number"
                        },
                        "email_id": {
                            "bsonType": "string",
                            "description": "Father's email ID"
                        }
                    }
                },
                "mother": {
                    "bsonType": "object",
                    "required": [
                        "name",
                        "mobile_no",
                        "email_id"
                    ],
                    "properties": {
                        "name": {
                            "bsonType": "string",
                            "description": "Mother's name"
                        },
                        "mobile_no": {
                            "bsonType": "string",
                            "description": "Mother's mobile number"
                        },
                        "email_id": {
                            "bsonType": "string",
                            "description": "Mother's email ID"
                        }
                    }
                },
                "specialization": {
                    "bsonType": "string",
                    "description": "Specialization area"
                },
                "registered": {
                    "bsonType": "bool",
                    "description": "Registration status"
                },
                "pass_out_year": {
                    "bsonType": "int",
                    "description": "Year of graduation"
                },
                "year_of_admission": {
                    "bsonType": "int",
                    "description": "Admission year"
                },
                "marks": {
                    "bsonType": "double",
                    "description": "Marks percentage"
                },
                "attendance": {
                    "bsonType": "double",
                    "description": "Attendance percentage"
                },
                "experience": {
                    "bsonType": "array",
                    "description": "Experience details",
                    "items": {
                        "bsonType": "object",
                        "required": [
                            "job_title",
                            "company_name",
                            "start_date",
                            "description",
                            "skills"
                        ],
                        "properties": {
                            "job_title": {
                                "bsonType": "string",
                                "description": "Job title"
                            },
                            "company_name": {
                                "bsonType": "string",
                                "description": "Company name"
                            },
                            "start_date": {
                                "bsonType": "string",
                                "description": "Start date (YYYY-MM-DD)"
                            },
                            "end_date": {
                                "bsonType": "string",
                                "description": "End date (YYYY-MM-DD or 'current')"
                            },
                            "description": {
                                "bsonType": "string",
                                "description": "Job responsibilities"
                            },
                            "skills": {
                                "bsonType": "array",
                                "items": {
                                    "bsonType": "string"
                                },
                                "description": "Skills used"
                            }
                        }
                    }
                },
                "skills": {
                    "bsonType": "object",
                    "description": "Skills categorized",
                    "properties": {
                        "technical": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": "string"
                            },
                            "description": "Technical skills"
                        },
                        "non_technical": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": "string"
                            },
                            "description": "Non-technical skills"
                        }
                    }
                },
                "projects": {
                    "bsonType": "array",
                    "description": "Projects details",
                    "items": {
                        "bsonType": "object",
                        "required": [
                            "project_name",
                            "project_description",
                            "project_link"
                        ],
                        "properties": {
                            "project_name": {
                                "bsonType": "string",
                                "description": "Name of the project"
                            },
                            "project_description": {
                                "bsonType": "string",
                                "description": "Description of the project"
                            },
                            "project_link": {
                                "bsonType": "string",
                                "description": "Link to the project"
                            }
                        }
                    }
                },
                "education": {
                    "bsonType": "object",
                    "description": "Educational details",
                    "required": [
                        "tenth",
                        "twelfth",
                        "graduation"
                    ],
                    "properties": {
                        "tenth": {
                            "bsonType": "double",
                            "description": "10th grade percentage"
                        },
                        "twelfth": {
                            "bsonType": "double",
                            "description": "12th grade percentage"
                        },
                        "graduation": {
                            "bsonType": "string",
                            "description": "Graduation or diploma details"
                        }
                    }
                },
                "cv": {
                    "bsonType": "string",
                    "description": "Link to CV"
                },
                "companies": {
                    "bsonType": "object",
                    "description": "Company application details",
                    "required": [
                        "applied",
                        "rejected",
                        "interviews_attended",
                        "interviews_not_attended"
                    ],
                    "properties": {
                        "applied": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": "string"
                            },
                            "description": "Companies applied for"
                        },
                        "rejected": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": "string"
                            },
                            "description": "Companies rejected"
                        },
                        "interviews_attended": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": "string"
                            },
                            "description": "Companies where interviews were attended"
                        },
                        "interviews_not_attended": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": "string"
                            },
                            "description": "Companies where interviews were not attended"
                        }
                    }
                },
                "certifications": {
                    "bsonType": "array",
                    "description": "Certifications received",
                    "items": {
                        "bsonType": "object",
                        "required": [
                            "certificate_name",
                            "institute_name",
                            "verification_link",
                            "pdf"
                        ],
                        "properties": {
                            "certificate_name": {
                                "bsonType": "string",
                                "description": "Name of the certificate"
                            },
                            "institute_name": {
                                "bsonType": "string",
                                "description": "Institute or company name"
                            },
                            "verification_link": {
                                "bsonType": "string",
                                "description": "Link for verification"
                            },
                            "pdf": {
                                "bsonType": "string",
                                "description": "Link to PDF file"
                            }
                        }
                    }
                },
                "messages": {
                    "bsonType": "string",
                    "description": "Messages or comments"
                }
            }
        }
    }

    try:
        # Try to create the collection with validation
        db.create_collection("students", validator=student_validator)
        print("Created students collection with schema validation")
    except OperationFailure as e:
        # If collection already exists, update its validator
        if "already exists" in str(e):
            db.command("collMod", "students", validator=student_validator)
            print("Updated schema validation for existing students collection")
        else:
            print(f"Error setting up student schema: {e}")
            raise

def create_announcement_schema():
    """Create schema validation for announcements collection."""
    announcement_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["title", "content", "date", "posted_by"],
            "properties": {
                "title": {
                    "bsonType": "string",
                    "description": "Title of the announcement"
                },
                "content": {
                    "bsonType": "string",
                    "description": "Content of the announcement"
                },
                "date": {
                    "bsonType": "date",
                    "description": "Date when the announcement was posted"
                },
                "posted_by": {
                    "bsonType": "string",
                    "description": "ID/name of the person who posted the announcement"
                },
                "attachment": {
                    "bsonType": "string",
                    "description": "Optional attachment file path"
                }
            }
        }
    }

    try:
        # Try to create the collection with validation
        db.create_collection("announcements", validator=announcement_validator)
        print("Created announcements collection with schema validation")
    except OperationFailure as e:
        # If collection already exists, update its validator
        if "already exists" in str(e):
            db.command("collMod", "announcements", validator=announcement_validator)
            print("Updated schema validation for existing announcements collection")
        else:
            print(f"Error setting up announcement schema: {e}")
            raise

def create_message_schema():
    """Create schema validation for messages collection."""
    message_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["sender_id", "recipient_id", "content", "timestamp", "read"],
            "properties": {
                "sender_id": {
                    "bsonType": "string",
                    "description": "Registration number of the message sender"
                },
                "recipient_id": {
                    "bsonType": "string",
                    "description": "Registration number of the message recipient"
                },
                "subject": {
                    "bsonType": "string",
                    "description": "Subject of the message"
                },
                "content": {
                    "bsonType": "string",
                    "description": "Content of the message"
                },
                "timestamp": {
                    "bsonType": "date",
                    "description": "Timestamp when the message was sent"
                },
                "read": {
                    "bsonType": "bool",
                    "description": "Whether the message has been read by recipient"
                },
                "attachment": {
                    "bsonType": "string",
                    "description": "Optional attachment file path"
                }
            }
        }
    }

    try:
        # Try to create the collection with validation
        db.create_collection("messages", validator=message_validator)
        print("Created messages collection with schema validation")
    except OperationFailure as e:
        # If collection already exists, update its validator
        if "already exists" in str(e):
            db.command("collMod", "messages", validator=message_validator)
            print("Updated schema validation for existing messages collection")
        else:
            print(f"Error setting up message schema: {e}")
            raise

def create_interview_schema():
    """Create schema validation for interviews collection."""
    interview_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["company_name", "student_id", "date", "time", "status"],
            "properties": {
                "company_name": {
                    "bsonType": "string",
                    "description": "Name of the company"
                },
                "student_id": {
                    "bsonType": "string",
                    "description": "Registration number of the student"
                },
                "date": {
                    "bsonType": "date",
                    "description": "Date of the interview"
                },
                "time": {
                    "bsonType": "string",
                    "description": "Time of the interview"
                },
                "location": {
                    "bsonType": "string",
                    "description": "Location of the interview"
                },
                "mode": {
                    "bsonType": "string",
                    "enum": ["Online", "In-person"],
                    "description": "Mode of the interview"
                },
                "status": {
                    "bsonType": "string",
                    "enum": ["scheduled", "completed", "cancelled", "missed"],
                    "description": "Status of the interview"
                },
                "notes": {
                    "bsonType": "string",
                    "description": "Additional notes or instructions"
                }
            }
        }
    }

    try:
        # Check if collection exists before trying to create it
        collection_names = db.list_collection_names()
        if "interviews" in collection_names:
            # Collection exists, just update the validator
            db.command("collMod", "interviews", validator=interview_validator)
            print("Updated schema validation for existing interviews collection")
        else:
            # Collection doesn't exist, create it
            db.create_collection("interviews", validator=interview_validator)
            print("Created interviews collection with schema validation")
    except Exception as e:
        print(f"Error setting up interview schema: {e}")
        # Don't raise error to allow application to continue
def initialize_db_schemas():
    """Initialize all database collection schemas."""
    try:
        create_student_schema_validator()
        create_announcement_schema()
        create_message_schema()
        create_interview_schema()
        print("Database schema initialization complete")
    except Exception as e:
        print(f"Warning: Error during schema initialization: {e}")
        print("The application will continue, but some database validations may not be in effect.")