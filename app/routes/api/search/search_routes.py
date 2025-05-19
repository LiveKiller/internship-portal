from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId

from app import db
from app.routes.api.admin.admin_routes import admin_required

search_bp = Blueprint('search', __name__)

@search_bp.route('/companies', methods=['GET'])
@jwt_required()
def search_companies():
    """Search companies by keyword across multiple fields."""
    # Get search query
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Build search query
    search_query = {
        '$or': [
            {'name': {'$regex': query, '$options': 'i'}},
            {'job_title': {'$regex': query, '$options': 'i'}},
            {'job_description': {'$regex': query, '$options': 'i'}},
            {'requirements': {'$regex': query, '$options': 'i'}},
            {'location': {'$regex': query, '$options': 'i'}}
        ],
        'active': True
    }
    
    # Apply additional filters if provided
    job_type = request.args.get('job_type')
    if job_type:
        search_query['job_type'] = job_type
        
    work_place = request.args.get('work_place')
    if work_place:
        search_query['work_place'] = work_place
    
    # Get total count for pagination
    total = db.companies.count_documents(search_query)
    
    # Apply pagination
    companies = list(db.companies.find(search_query).skip((page-1)*per_page).limit(per_page))
    
    # Convert ObjectId to string for JSON serialization
    for company in companies:
        company['_id'] = str(company['_id'])
    
    return jsonify({
        'companies': companies,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page,
        'query': query
    }), 200

@search_bp.route('/students', methods=['GET'])
@jwt_required()
@admin_required
def search_students():
    """Search students by keyword (admin only)."""
    # Get search query
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Build search query
    search_query = {
        '$or': [
            {'registration_no': {'$regex': query, '$options': 'i'}},
            {'name': {'$regex': query, '$options': 'i'}},
            {'email_id': {'$regex': query, '$options': 'i'}},
            {'specialization': {'$regex': query, '$options': 'i'}}
        ]
    }
    
    # Get total count for pagination
    total = db.students.count_documents(search_query)
    
    # Apply pagination
    students = list(db.students.find(search_query).skip((page-1)*per_page).limit(per_page))
    
    # Convert ObjectId to string for JSON serialization and remove sensitive data
    for student in students:
        student['_id'] = str(student['_id'])
        if 'password' in student:
            del student['password']
    
    return jsonify({
        'students': students,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page,
        'query': query
    }), 200

@search_bp.route('/announcements', methods=['GET'])
@jwt_required()
def search_announcements():
    """Search announcements by keyword."""
    # Get search query
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Build search query
    search_query = {
        '$or': [
            {'title': {'$regex': query, '$options': 'i'}},
            {'content': {'$regex': query, '$options': 'i'}}
        ]
    }
    
    # Get total count for pagination
    total = db.announcements.count_documents(search_query)
    
    # Apply pagination
    announcements = list(db.announcements.find(search_query).sort('date', -1).skip((page-1)*per_page).limit(per_page))
    
    # Convert ObjectId to string for JSON serialization
    for announcement in announcements:
        announcement['_id'] = str(announcement['_id'])
    
    return jsonify({
        'announcements': announcements,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page,
        'query': query
    }), 200

@search_bp.route('/global', methods=['GET'])
@jwt_required()
def global_search():
    """Global search across multiple collections."""
    # Get search query
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    results = {
        'companies': [],
        'announcements': [],
        'total': 0
    }
    
    # Search in companies
    company_query = {
        '$or': [
            {'name': {'$regex': query, '$options': 'i'}},
            {'job_title': {'$regex': query, '$options': 'i'}},
            {'job_description': {'$regex': query, '$options': 'i'}}
        ],
        'active': True
    }
    companies = list(db.companies.find(company_query).limit(5))
    for company in companies:
        company['_id'] = str(company['_id'])
        company['type'] = 'company'
    results['companies'] = companies
    
    # Search in announcements
    announcement_query = {
        '$or': [
            {'title': {'$regex': query, '$options': 'i'}},
            {'content': {'$regex': query, '$options': 'i'}}
        ]
    }
    announcements = list(db.announcements.find(announcement_query).sort('date', -1).limit(5))
    for announcement in announcements:
        announcement['_id'] = str(announcement['_id'])
        announcement['type'] = 'announcement'
    results['announcements'] = announcements
    
    # Combine results for pagination
    all_results = companies + announcements
    all_results.sort(key=lambda x: x.get('date', x.get('posted_date', '')), reverse=True)
    
    # Calculate total
    total_companies = db.companies.count_documents(company_query)
    total_announcements = db.announcements.count_documents(announcement_query)
    total = total_companies + total_announcements
    
    results['total'] = total
    results['query'] = query
    
    return jsonify(results), 200
