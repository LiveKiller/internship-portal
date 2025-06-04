"""
Student routes module.
Contains all route definitions for student-related functionality.
"""

# Import all blueprints with standardized naming
from app.routes.api.student.dashboard_routes import student_dashboard_bp
from app.routes.api.student.profile_routes import student_profile_bp
from app.routes.api.student.portfolio_routes import student_portfolio_bp
from app.routes.api.student.notifications_routes import student_notifications_bp
from app.routes.api.student.recommendations_routes import student_recommendations_bp
from app.routes.api.student.announcement_routes import student_announcements_bp
from app.routes.api.student.messages_routes import message_bp

# Import main student routes
from app.routes.api.student.routes import student_bp