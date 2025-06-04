import random
import string
import bcrypt
from datetime import datetime, timedelta
from bson.objectid import ObjectId

from app import db

def generate_random_string(length=10):
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def hash_password(password):
    """Hash a password for storing."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def generate_registration_number():
    """Generate a random registration number in the format 2X13XXXXX."""
    year = random.choice(['2', '2'])
    branch = random.choice(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
    program = '13'  # Placeholder for program code
    sequence = ''.join(random.choice(string.digits) for _ in range(5))
    
    return f"{year}{branch}{program}{sequence}"

def generate_dummy_skills():
    """Generate a list of random skills."""
    all_skills = [
        "Python", "JavaScript", "React", "Node.js", "MongoDB", "SQL", "HTML", "CSS",
        "Java", "C++", "C#", "Flutter", "Dart", "Machine Learning", "Data Analysis",
        "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Git", "CI/CD", "Agile",
        "TensorFlow", "PyTorch", "NLP", "Computer Vision", "Blockchain", "IoT"
    ]
    
    return random.sample(all_skills, random.randint(5, 10))

def generate_dummy_projects():
    """Generate a list of random projects."""
    project_titles = [
        "E-commerce Platform", "Chat Application", "Task Management System",
        "Portfolio Website", "Weather App", "Social Media Dashboard",
        "Machine Learning Classifier", "Blockchain Wallet", "IoT Home Automation",
        "Mobile Game", "Recipe Finder", "Fitness Tracker", "Student Management System",
        "Music Player", "Video Streaming Service", "Blog Platform", "News Aggregator"
    ]
    
    technologies = [
        "Python", "JavaScript", "React", "Node.js", "MongoDB", "SQL", "HTML", "CSS",
        "Java", "C++", "C#", "Flutter", "Dart", "TensorFlow", "PyTorch", "AWS", 
        "Azure", "Firebase", "Docker", "Kubernetes", "Swift", "Kotlin"
    ]
    
    projects = []
    
    for _ in range(random.randint(2, 5)):
        title = random.choice(project_titles)
        project_titles.remove(title)  # Ensure unique titles
        
        project = {
            "title": title,
            "description": f"A {title.lower()} built with modern technologies.",
            "technologies": random.sample(technologies, random.randint(3, 6)),
            "url": f"https://github.com/username/{title.lower().replace(' ', '-')}",
            "start_date": (datetime.now() - timedelta(days=random.randint(100, 500))).strftime("%Y-%m-%d"),
            "end_date": (datetime.now() - timedelta(days=random.randint(10, 90))).strftime("%Y-%m-%d")
        }
        
        projects.append(project)
    
    return projects

def generate_dummy_academics():
    """Generate dummy academic records."""
    return {
        "cgpa": round(random.uniform(7.0, 9.5), 2),
        "semester": random.randint(1, 8),
        "department": random.choice(["CSE", "IT", "ECE", "EEE", "ME", "CE", "BT"]),
        "degree": "B.Tech",
        "graduation_year": random.randint(2023, 2026),
        "backlogs": random.randint(0, 2)
    }

def generate_dummy_students(count=5):
    """
    Generate dummy student records and insert them into the database.
    
    Args:
        count (int): Number of dummy students to generate
        
    Returns:
        list: List of generated student IDs
    """
    first_names = ["Aiden", "Sophia", "Noah", "Emma", "Liam", "Olivia", "Jackson", "Ava", "Lucas", "Mia",
                 "Raj", "Priya", "Arjun", "Divya", "Rahul", "Neha", "Vikram", "Ananya", "Amit", "Sneha"]
    
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                "Patel", "Sharma", "Kumar", "Singh", "Joshi", "Gupta", "Desai", "Shah", "Reddy", "Verma"]
    
    student_ids = []
    
    for _ in range(count):
        # Generate basic info
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        registration_no = generate_registration_number()
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        
        # Generate student document
        student = {
            "registration_no": registration_no,
            "email": email,
            "password": hash_password("password123"),  # Default password
            "name": {
                "first": first_name,
                "last": last_name
            },
            "phone": f"+91{random.randint(7000000000, 9999999999)}",
            "academics": generate_dummy_academics(),
            "skills": generate_dummy_skills(),
            "projects": generate_dummy_projects(),
            "resume_url": None,
            "profile_complete": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "companies": {
                "applied": [],
                "rejected": [],
                "interviews_attended": [],
                "interviews_not_attended": []
            },
            "placed": random.choice([True, False]),
            "placement_details": None,
            "settings": {
                "email_notifications": True,
                "sms_notifications": False
            }
        }
        
        # Insert student into database
        result = db.students.insert_one(student)
        student_ids.append(str(result.inserted_id))
        
        print(f"Created dummy student: {first_name} {last_name} ({registration_no})")
    
    return student_ids

def generate_dummy_companies(count=3):
    """
    Generate dummy company records and insert them into the database.
    
    Args:
        count (int): Number of dummy companies to generate
        
    Returns:
        list: List of generated company IDs
    """
    company_names = [
        "TechSolutions Inc.", "Innovate Systems", "DataMinds", "CloudWave Technologies",
        "NextGen Software", "Global Tech Partners", "Quantum Innovations", "Digital Dynamics",
        "CyberSphere Solutions", "Future Technologies", "CodeCraft", "Silicon Valley Innovations"
    ]
    
    company_ids = []
    
    for _ in range(count):
        company_name = random.choice(company_names)
        company_names.remove(company_name)  # Ensure unique names
        
        # Current time plus random days (1-30) for deadline
        deadline = datetime.now() + timedelta(days=random.randint(1, 30))
        
        company = {
            "name": company_name,
            "email": f"careers@{company_name.lower().replace(' ', '')}.com",
            "description": f"{company_name} is a leading technology company focused on innovation.",
            "website": f"https://www.{company_name.lower().replace(' ', '')}.com",
            "logo_url": None,
            "positions": ["Software Engineer", "Data Scientist", "Product Manager", "UX Designer"],
            "requirements": {
                "cgpa": round(random.uniform(6.0, 8.0), 1),
                "backlogs": random.randint(0, 2),
                "skills": random.sample(generate_dummy_skills(), 3)
            },
            "package": {
                "min": random.randint(8, 12),
                "max": random.randint(15, 25)
            },
            "deadline": int(deadline.timestamp()),
            "active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Insert company into database
        result = db.companies.insert_one(company)
        company_ids.append(str(result.inserted_id))
        
        print(f"Created dummy company: {company_name}")
    
    return company_ids

def generate_dummy_applications(student_ids, company_ids, count=10):
    """
    Generate dummy applications between students and companies.
    
    Args:
        student_ids (list): List of student IDs
        company_ids (list): List of company IDs
        count (int): Maximum number of applications to generate
        
    Returns:
        int: Number of applications generated
    """
    if not student_ids or not company_ids:
        print("No students or companies to generate applications")
        return 0
    
    # Ensure we don't try to create more applications than possible
    max_possible = len(student_ids) * len(company_ids)
    count = min(count, max_possible)
    
    applications_created = 0
    
    # Track student-company pairs to avoid duplicates
    application_pairs = set()
    
    for _ in range(count):
        student_id = random.choice(student_ids)
        company_id = random.choice(company_ids)
        
        # Skip if this student-company pair already exists
        pair = (student_id, company_id)
        if pair in application_pairs:
            continue
        
        application_pairs.add(pair)
        
        # Get student and company documents
        student = db.students.find_one({"_id": ObjectId(student_id)})
        company = db.companies.find_one({"_id": ObjectId(company_id)})
        
        if not student or not company:
            continue
        
        # Create application in student document
        if 'applied' not in student.get('companies', {}):
            student['companies'] = student.get('companies', {})
            student['companies']['applied'] = []
        
        # Add company to student's applied list
        application_date = datetime.now() - timedelta(days=random.randint(1, 30))
        
        application = {
            "company_id": ObjectId(company_id),
            "company_name": company["name"],
            "applied_date": application_date,
            "status": random.choice(["pending", "shortlisted", "rejected", "selected"])
        }
        
        db.students.update_one(
            {"_id": ObjectId(student_id)},
            {"$push": {"companies.applied": application}}
        )
        
        applications_created += 1
        print(f"Created application: {student['name']['first']} applied to {company['name']}")
    
    return applications_created

def generate_dummy_announcements(count=5):
    """
    Generate dummy announcements and insert them into the database.
    
    Args:
        count (int): Number of dummy announcements to generate
        
    Returns:
        list: List of generated announcement IDs
    """
    announcement_titles = [
        "Campus Placement Drive", "Internship Opportunity", "Upcoming Workshop",
        "Webinar on Industry Trends", "Career Fair", "Technical Symposium",
        "Hackathon Announcement", "Mock Interview Session", "Resume Building Workshop",
        "Soft Skills Training", "Industry Expert Talk", "New Course Registration"
    ]
    
    announcement_ids = []
    
    for _ in range(count):
        title = random.choice(announcement_titles)
        announcement_titles.remove(title)  # Ensure unique titles
        
        # Date between 1-30 days ago
        date = datetime.now() - timedelta(days=random.randint(1, 30))
        
        announcement = {
            "title": title,
            "content": f"We are pleased to announce the {title.lower()}. Please check the details and register accordingly.",
            "date": date,
            "author": random.choice(["Placement Cell", "Training Department", "Faculty Coordinator", "Dean"]),
            "important": random.choice([True, False]),
            "attachment_url": None
        }
        
        # Insert announcement into database
        result = db.announcements.insert_one(announcement)
        announcement_ids.append(str(result.inserted_id))
        
        print(f"Created dummy announcement: {title}")
    
    return announcement_ids

def populate_dummy_data():
    """
    Populate the database with dummy data for testing.
    
    This function generates:
    - 5 student profiles
    - 3 companies
    - Applications between students and companies
    - 5 announcements
    
    Returns:
        dict: Summary of data generation
    """
    print("Generating dummy data for testing...")
    
    # Generate dummy students
    student_ids = generate_dummy_students(5)
    
    # Generate dummy companies
    company_ids = generate_dummy_companies(3)
    
    # Generate applications
    applications_count = generate_dummy_applications(student_ids, company_ids)
    
    # Generate announcements
    announcement_ids = generate_dummy_announcements(5)
    
    summary = {
        "students_created": len(student_ids),
        "companies_created": len(company_ids),
        "applications_created": applications_count,
        "announcements_created": len(announcement_ids)
    }
    
    print("\nDummy data generation complete!")
    print(f"Created {summary['students_created']} students")
    print(f"Created {summary['companies_created']} companies")
    print(f"Created {summary['applications_created']} applications")
    print(f"Created {summary['announcements_created']} announcements")
    
    return summary

if __name__ == "__main__":
    # This allows running the script directly
    from app import create_app
    app = create_app()
    with app.app_context():
        populate_dummy_data() 