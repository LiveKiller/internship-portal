import os
import json
import random
import datetime
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash
from app import db
import logging

def clear_database():
    """Clear all collections in the database."""
    try:
        # Get all collection names
        collections = db.list_collection_names()
        
        # Drop each collection
        for collection in collections:
            db[collection].drop()
        
        logging.info(f"Successfully cleared {len(collections)} collections from the database")
        return True, f"Successfully cleared {len(collections)} collections from the database"
    except Exception as e:
        logging.error(f"Error clearing database: {str(e)}")
        return False, f"Error clearing database: {str(e)}"

def seed_database():
    """Seed the database with initial data for testing."""
    try:
        # Create admin user
        admin_user = {
            "username": "admin",
            "email": "admin@university.edu",
            "password": generate_password_hash("admin123"),
            "is_admin": True,
            "created_at": datetime.datetime.now()
        }
        db.users.insert_one(admin_user)
        logging.info("Admin user created")
        
        # Create test students
        students = []
        departments = ["Computer Science", "Electrical Engineering", "Mechanical Engineering", 
                      "Civil Engineering", "Chemical Engineering", "Business Administration"]
        skills = [
            ["Python", "JavaScript", "React", "Node.js", "MongoDB"],
            ["Java", "Spring Boot", "MySQL", "Docker", "Kubernetes"],
            ["C++", "Data Structures", "Algorithms", "Machine Learning"],
            ["HTML", "CSS", "UI/UX Design", "Figma", "Adobe XD"],
            ["AWS", "Azure", "DevOps", "CI/CD", "Jenkins"]
        ]
        
        for i in range(1, 101):  # Create 100 test students
            reg_no = f"S{2023000 + i}"
            student = {
                "registration_no": reg_no,
                "name": f"Student {i}",
                "email": f"student{i}@university.edu",
                "password": generate_password_hash("password123"),
                "department": random.choice(departments),
                "year": random.randint(1, 4),
                "skills": {
                    "technical": random.sample(random.choice(skills), k=random.randint(2, 5)),
                    "soft": random.sample(["Communication", "Teamwork", "Leadership", "Problem Solving", "Time Management"], 
                                         k=random.randint(2, 4))
                },
                "interests": random.sample(["Web Development", "Mobile Development", "Data Science", 
                                          "Machine Learning", "Cloud Computing", "Cybersecurity"], 
                                         k=random.randint(2, 4)),
                "registration_date": datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 365))
            }
            students.append(student)
        
        db.students.insert_many(students)
        logging.info(f"{len(students)} test students created")
        
        # Create test companies
        companies = []
        job_types = ["Full-time", "Part-time", "Contract", "Internship"]
        work_places = ["Remote", "On-site", "Hybrid"]
        locations = ["New York", "San Francisco", "Boston", "Austin", "Seattle", "Chicago"]
        
        for i in range(1, 51):  # Create 50 test companies
            company = {
                "name": f"Company {i}",
                "logo": f"https://via.placeholder.com/150?text=Company{i}",
                "job_title": f"Software Engineer {random.choice(['I', 'II', 'III', 'Senior', 'Lead'])}",
                "job_description": f"We are looking for a talented software engineer to join our team. You will be responsible for developing and maintaining our software applications.",
                "requirements": ", ".join(random.sample(["Python", "JavaScript", "React", "Node.js", "MongoDB", "Java", 
                                                       "Spring Boot", "MySQL", "Docker", "Kubernetes", "C++", "AWS"], 
                                                     k=random.randint(3, 6))),
                "job_type": random.choice(job_types),
                "work_place": random.choice(work_places),
                "location": random.choice(locations),
                "stipend": random.randint(1000, 5000) * 100,  # Random stipend between 100k and 500k
                "duration": f"{random.randint(3, 12)} months",
                "deadline": datetime.datetime.now() + datetime.timedelta(days=random.randint(7, 30)),
                "posted_date": datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30)),
                "active": random.choice([True, True, True, False]),  # 75% chance of being active
                "company_size": random.choice(["1-50", "51-200", "201-500", "501-1000", "1000+"])
            }
            companies.append(company)
        
        company_ids = db.companies.insert_many(companies).inserted_ids
        logging.info(f"{len(companies)} test companies created")
        
        # Create test applications
        applications = []
        statuses = ["pending", "approved", "rejected", "interview"]
        
        for i in range(1, 201):  # Create 200 test applications
            student_index = random.randint(0, 99)  # Random student from our 100 test students
            company_index = random.randint(0, 49)  # Random company from our 50 test companies
            
            status = random.choice(statuses)
            applied_date = datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30))
            
            application = {
                "company_id": company_ids[company_index],
                "student_id": students[student_index]["registration_no"],
                "cover_letter": f"I am writing to express my interest in the position at your company. I believe my skills and experience make me a strong candidate.",
                "portfolio_link": f"https://portfolio.student{student_index+1}.com",
                "availability": f"{random.randint(1, 3)} weeks",
                "notice_period": f"{random.randint(1, 4)} weeks",
                "status": status,
                "applied_date": applied_date
            }
            
            # Add status update date if status is not pending
            if status != "pending":
                application["status_updated_date"] = applied_date + datetime.timedelta(days=random.randint(1, 7))
            
            applications.append(application)
        
        db.applications.insert_many(applications)
        logging.info(f"{len(applications)} test applications created")
        
        # Create test announcements
        announcements = []
        
        for i in range(1, 21):  # Create 20 test announcements
            announcement = {
                "title": f"Announcement {i}",
                "content": f"This is test announcement {i}. It contains important information for all students.",
                "created_at": datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 60)),
                "created_by": "admin",
                "important": random.choice([True, False]),
                "tags": random.sample(["General", "Internship", "Placement", "Workshop", "Seminar"], k=random.randint(1, 3))
            }
            announcements.append(announcement)
        
        db.announcements.insert_many(announcements)
        logging.info(f"{len(announcements)} test announcements created")
        
        # Create test notifications
        notifications = []
        
        for i in range(1, 301):  # Create 300 test notifications
            student_index = random.randint(0, 99)
            
            notification_types = ["application", "announcement", "message", "deadline"]
            notification_type = random.choice(notification_types)
            
            if notification_type == "application":
                title = "Application Update"
                message = f"Your application status has been updated to {random.choice(statuses)}"
            elif notification_type == "announcement":
                title = "New Announcement"
                message = "A new announcement has been posted"
            elif notification_type == "message":
                title = "New Message"
                message = "You have received a new message"
            else:
                title = "Upcoming Deadline"
                message = "An application deadline is approaching"
            
            notification = {
                "recipient_id": students[student_index]["registration_no"],
                "title": title,
                "message": message,
                "type": notification_type,
                "timestamp": datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30)),
                "read": random.choice([True, False])
            }
            notifications.append(notification)
        
        db.notifications.insert_many(notifications)
        logging.info(f"{len(notifications)} test notifications created")
        
        return True, "Database seeded successfully with test data"
    except Exception as e:
        logging.error(f"Error seeding database: {str(e)}")
        return False, f"Error seeding database: {str(e)}"

def export_database(export_dir="exports"):
    """Export all collections to JSON files."""
    try:
        # Create export directory if it doesn't exist
        os.makedirs(export_dir, exist_ok=True)
        
        # Get all collection names
        collections = db.list_collection_names()
        
        # Export each collection
        for collection in collections:
            data = list(db[collection].find())
            
            # Convert ObjectId to string for JSON serialization
            for item in data:
                item['_id'] = str(item['_id'])
                
                # Convert datetime objects to ISO format
                for key, value in item.items():
                    if isinstance(value, datetime.datetime):
                        item[key] = value.isoformat()
                    elif isinstance(value, ObjectId):
                        item[key] = str(value)
            
            # Write to JSON file
            with open(os.path.join(export_dir, f"{collection}.json"), 'w') as f:
                json.dump(data, f, indent=2)
        
        logging.info(f"Successfully exported {len(collections)} collections to {export_dir}")
        return True, f"Successfully exported {len(collections)} collections to {export_dir}"
    except Exception as e:
        logging.error(f"Error exporting database: {str(e)}")
        return False, f"Error exporting database: {str(e)}"

def import_database(import_dir="exports"):
    """Import collections from JSON files."""
    try:
        # Check if import directory exists
        if not os.path.exists(import_dir):
            return False, f"Import directory {import_dir} does not exist"
        
        # Get all JSON files in the import directory
        import_files = [f for f in os.listdir(import_dir) if f.endswith('.json')]
        
        if not import_files:
            return False, f"No JSON files found in {import_dir}"
        
        # Import each file
        for file_name in import_files:
            collection_name = file_name.split('.')[0]
            
            with open(os.path.join(import_dir, file_name), 'r') as f:
                data = json.load(f)
            
            # Drop existing collection
            db[collection_name].drop()
            
            # Insert data if not empty
            if data:
                db[collection_name].insert_many(data)
        
        logging.info(f"Successfully imported {len(import_files)} collections from {import_dir}")
        return True, f"Successfully imported {len(import_files)} collections from {import_dir}"
    except Exception as e:
        logging.error(f"Error importing database: {str(e)}")
        return False, f"Error importing database: {str(e)}"
