"""
Students module for the internship portal.
Contains routes and functionality for student operations.
"""

# Import all student related modules
from app.students.dashboard import dashboard_bp
from app.students.profile import profile_bp
from app.students.portfolio import portfolio_bp
from app.students.notifications import notifications_bp
from app.students.recommendations import recommendations_bp
from app.students.announcements import announcements_bp

# Import the main students blueprint (for operations not specific to submodules)
from app.students.routes import students_bp 