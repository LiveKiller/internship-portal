from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import calendar

from app import db
from app.routes.api.admin.admin_routes import admin_required

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/overview', methods=['GET'])
@jwt_required()
@admin_required
def get_analytics_overview():
    """Get overview analytics for the admin dashboard."""
    try:
        # Get total counts
        total_students = db.students.count_documents({})
        total_companies = db.companies.count_documents({})
        total_applications = db.applications.count_documents({})
        
        # Get active counts
        active_companies = db.companies.count_documents({'active': True})
        
        # Get application statistics
        pending_applications = db.applications.count_documents({'status': 'pending'})
        approved_applications = db.applications.count_documents({'status': 'approved'})
        rejected_applications = db.applications.count_documents({'status': 'rejected'})
        
        # Calculate application success rate
        if total_applications > 0:
            success_rate = (approved_applications / total_applications) * 100
        else:
            success_rate = 0
        
        return jsonify({
            'total_students': total_students,
            'total_companies': total_companies,
            'total_applications': total_applications,
            'active_companies': active_companies,
            'application_stats': {
                'pending': pending_applications,
                'approved': approved_applications,
                'rejected': rejected_applications,
                'success_rate': round(success_rate, 2)
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/applications/timeline', methods=['GET'])
@jwt_required()
@admin_required
def get_application_timeline():
    """Get application timeline data for charts."""
    try:
        # Get time range from query parameters (default to last 30 days)
        days = int(request.args.get('days', 30))
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Create date range for the timeline
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        
        # Initialize data structure for timeline
        timeline_data = {
            'dates': date_range,
            'applications': [0] * len(date_range),
            'approvals': [0] * len(date_range),
            'rejections': [0] * len(date_range)
        }
        
        # Get applications within the date range
        applications = list(db.applications.find({
            'applied_date': {'$gte': start_date, '$lte': end_date}
        }))
        
        # Process applications
        for app in applications:
            applied_date = app['applied_date'].strftime('%Y-%m-%d')
            if applied_date in date_range:
                index = date_range.index(applied_date)
                timeline_data['applications'][index] += 1
                
                # Check status updates
                if app.get('status_updated_date') and app['status_updated_date'] >= start_date:
                    status_date = app['status_updated_date'].strftime('%Y-%m-%d')
                    if status_date in date_range:
                        status_index = date_range.index(status_date)
                        if app['status'] == 'approved':
                            timeline_data['approvals'][status_index] += 1
                        elif app['status'] == 'rejected':
                            timeline_data['rejections'][status_index] += 1
        
        return jsonify(timeline_data), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/companies/popular', methods=['GET'])
@jwt_required()
@admin_required
def get_popular_companies():
    """Get most popular companies based on application count."""
    try:
        # Get limit from query parameters
        limit = int(request.args.get('limit', 10))
        
        # Aggregate applications by company
        pipeline = [
            {'$group': {
                '_id': '$company_id',
                'application_count': {'$sum': 1}
            }},
            {'$sort': {'application_count': -1}},
            {'$limit': limit}
        ]
        
        popular_companies = list(db.applications.aggregate(pipeline))
        
        # Get company details
        result = []
        for item in popular_companies:
            company_id = item['_id']
            company = db.companies.find_one({'_id': company_id})
            if company:
                result.append({
                    'company_id': str(company_id),
                    'name': company.get('name', 'Unknown'),
                    'job_title': company.get('job_title', 'Unknown'),
                    'logo': company.get('logo', ''),
                    'application_count': item['application_count']
                })
        
        return jsonify({
            'popular_companies': result
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/students/activity', methods=['GET'])
@jwt_required()
@admin_required
def get_student_activity():
    """Get student activity metrics."""
    try:
        # Get time range from query parameters (default to last 30 days)
        days = int(request.args.get('days', 30))
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get new student registrations
        new_students = db.students.count_documents({
            'registration_date': {'$gte': start_date, '$lte': end_date}
        })
        
        # Get active students (those who have applied to at least one company)
        active_students = db.applications.distinct('student_id', {
            'applied_date': {'$gte': start_date, '$lte': end_date}
        })
        active_count = len(active_students)
        
        # Get total students
        total_students = db.students.count_documents({})
        
        # Calculate engagement rate
        engagement_rate = (active_count / total_students) * 100 if total_students > 0 else 0
        
        # Get average applications per active student
        if active_count > 0:
            total_applications = db.applications.count_documents({
                'applied_date': {'$gte': start_date, '$lte': end_date}
            })
            avg_applications = total_applications / active_count
        else:
            avg_applications = 0
        
        return jsonify({
            'new_students': new_students,
            'active_students': active_count,
            'total_students': total_students,
            'engagement_rate': round(engagement_rate, 2),
            'avg_applications_per_student': round(avg_applications, 2)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/monthly-report', methods=['GET'])
@jwt_required()
@admin_required
def get_monthly_report():
    """Get monthly report data for the current year."""
    try:
        # Get year from query parameters (default to current year)
        year = int(request.args.get('year', datetime.now().year))
        
        # Initialize monthly data
        months = list(calendar.month_name)[1:]  # Get month names
        monthly_data = {
            'months': months,
            'new_students': [0] * 12,
            'new_companies': [0] * 12,
            'applications': [0] * 12,
            'approvals': [0] * 12
        }
        
        # Get student registrations by month
        student_pipeline = [
            {'$match': {
                'registration_date': {
                    '$gte': datetime(year, 1, 1),
                    '$lt': datetime(year + 1, 1, 1)
                }
            }},
            {'$group': {
                '_id': {'$month': '$registration_date'},
                'count': {'$sum': 1}
            }}
        ]
        
        student_results = list(db.students.aggregate(student_pipeline))
        for result in student_results:
            month_index = result['_id'] - 1  # MongoDB months are 1-indexed
            monthly_data['new_students'][month_index] = result['count']
        
        # Get company registrations by month
        company_pipeline = [
            {'$match': {
                'posted_date': {
                    '$gte': datetime(year, 1, 1),
                    '$lt': datetime(year + 1, 1, 1)
                }
            }},
            {'$group': {
                '_id': {'$month': '$posted_date'},
                'count': {'$sum': 1}
            }}
        ]
        
        company_results = list(db.companies.aggregate(company_pipeline))
        for result in company_results:
            month_index = result['_id'] - 1
            monthly_data['new_companies'][month_index] = result['count']
        
        # Get applications by month
        application_pipeline = [
            {'$match': {
                'applied_date': {
                    '$gte': datetime(year, 1, 1),
                    '$lt': datetime(year + 1, 1, 1)
                }
            }},
            {'$group': {
                '_id': {'$month': '$applied_date'},
                'count': {'$sum': 1}
            }}
        ]
        
        application_results = list(db.applications.aggregate(application_pipeline))
        for result in application_results:
            month_index = result['_id'] - 1
            monthly_data['applications'][month_index] = result['count']
        
        # Get approvals by month
        approval_pipeline = [
            {'$match': {
                'status': 'approved',
                'status_updated_date': {
                    '$gte': datetime(year, 1, 1),
                    '$lt': datetime(year + 1, 1, 1)
                }
            }},
            {'$group': {
                '_id': {'$month': '$status_updated_date'},
                'count': {'$sum': 1}
            }}
        ]
        
        approval_results = list(db.applications.aggregate(approval_pipeline))
        for result in approval_results:
            month_index = result['_id'] - 1
            monthly_data['approvals'][month_index] = result['count']
        
        return jsonify(monthly_data), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
