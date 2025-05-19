from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
import re

from app import db

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/companies', methods=['GET'])
@jwt_required()
def get_recommended_companies():
    """Get recommended companies based on user skills and interests."""
    current_user = get_jwt_identity()
    
    # Get user data
    user = db.students.find_one({'registration_no': current_user})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user skills and interests
    technical_skills = user.get('skills', {}).get('technical', [])
    interests = user.get('interests', [])
    
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # If user has no skills or interests, return active companies
    if not technical_skills and not interests:
        query = {'active': True}
        total = db.companies.count_documents(query)
        companies = list(db.companies.find(query).skip((page-1)*per_page).limit(per_page))
        
        # Convert ObjectId to string for JSON serialization
        for company in companies:
            company['_id'] = str(company['_id'])
        
        return jsonify({
            'companies': companies,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page,
            'recommendation_type': 'general'
        }), 200
    
    # Build query to find companies that match user skills or interests
    skill_queries = []
    for skill in technical_skills:
        skill_queries.append({'requirements': {'$regex': re.escape(skill), '$options': 'i'}})
    
    interest_queries = []
    for interest in interests:
        interest_queries.append({'job_description': {'$regex': re.escape(interest), '$options': 'i'}})
        interest_queries.append({'job_title': {'$regex': re.escape(interest), '$options': 'i'}})
    
    # Combine queries
    combined_queries = skill_queries + interest_queries
    
    if combined_queries:
        query = {
            '$or': combined_queries,
            'active': True
        }
    else:
        query = {'active': True}
    
    # Get total count for pagination
    total = db.companies.count_documents(query)
    
    # Apply pagination
    companies = list(db.companies.find(query).skip((page-1)*per_page).limit(per_page))
    
    # Calculate match score for each company
    for company in companies:
        company['_id'] = str(company['_id'])
        
        # Calculate match score based on how many skills and interests match
        match_count = 0
        requirements = company.get('requirements', '').lower()
        job_description = company.get('job_description', '').lower()
        job_title = company.get('job_title', '').lower()
        
        for skill in technical_skills:
            if skill.lower() in requirements:
                match_count += 2  # Skills are weighted more heavily
        
        for interest in interests:
            if interest.lower() in job_description or interest.lower() in job_title:
                match_count += 1
        
        # Calculate match percentage
        total_factors = len(technical_skills) * 2 + len(interests)
        if total_factors > 0:
            company['match_percentage'] = min(100, int((match_count / total_factors) * 100))
        else:
            company['match_percentage'] = 0
    
    # Sort by match percentage
    companies.sort(key=lambda x: x.get('match_percentage', 0), reverse=True)
    
    return jsonify({
        'companies': companies,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page,
        'recommendation_type': 'personalized'
    }), 200

@recommendations_bp.route('/similar-companies/<company_id>', methods=['GET'])
@jwt_required()
def get_similar_companies(company_id):
    """Get companies similar to the specified company."""
    try:
        # Validate the ObjectId format
        if not ObjectId.is_valid(company_id):
            return jsonify({'error': 'Invalid company ID format'}), 400
        
        # Find the company
        company = db.companies.find_one({'_id': ObjectId(company_id)})
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Extract key features for similarity matching
        job_title = company.get('job_title', '')
        job_type = company.get('job_type', '')
        requirements = company.get('requirements', '')
        
        # Build query to find similar companies
        query = {
            '_id': {'$ne': ObjectId(company_id)},  # Exclude the current company
            'active': True,
            '$or': [
                {'job_title': {'$regex': job_title.split(' ')[0] if job_title else '', '$options': 'i'}},
                {'job_type': job_type},
                {'requirements': {'$regex': '|'.join(requirements.split(',')[:3]) if requirements else '', '$options': 'i'}}
            ]
        }
        
        # Get limit parameter
        limit = int(request.args.get('limit', 5))
        
        # Find similar companies
        similar_companies = list(db.companies.find(query).limit(limit))
        
        # Convert ObjectId to string for JSON serialization
        for similar in similar_companies:
            similar['_id'] = str(similar['_id'])
        
        return jsonify({
            'similar_companies': similar_companies,
            'count': len(similar_companies)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recommendations_bp.route('/trending', methods=['GET'])
@jwt_required()
def get_trending_companies():
    """Get trending companies based on application count and recency."""
    try:
        # Get limit parameter
        limit = int(request.args.get('limit', 10))
        
        # Aggregate applications by company with recency factor
        pipeline = [
            # Match only recent applications (last 30 days)
            {'$match': {
                'applied_date': {'$gte': {'$subtract': [{'$now': {}}, {'$multiply': [30, 24, 60, 60, 1000]}]}}
            }},
            # Group by company
            {'$group': {
                '_id': '$company_id',
                'application_count': {'$sum': 1},
                'latest_application': {'$max': '$applied_date'}
            }},
            # Calculate trending score (application count * recency factor)
            {'$addFields': {
                'days_ago': {
                    '$divide': [
                        {'$subtract': [{'$now': {}}, '$latest_application']},
                        {'$multiply': [24, 60, 60, 1000]}  # Convert ms to days
                    ]
                }
            }},
            {'$addFields': {
                'recency_factor': {'$divide': [1, {'$add': [1, '$days_ago']}]},
                'trending_score': {
                    '$multiply': [
                        '$application_count',
                        {'$divide': [1, {'$add': [1, '$days_ago']}]}
                    ]
                }
            }},
            # Sort by trending score
            {'$sort': {'trending_score': -1}},
            # Limit results
            {'$limit': limit}
        ]
        
        trending_results = list(db.applications.aggregate(pipeline))
        
        # Get company details for each trending company
        trending_companies = []
        for result in trending_results:
            company_id = result['_id']
            company = db.companies.find_one({'_id': company_id})
            if company and company.get('active', False):
                company['_id'] = str(company['_id'])
                company['application_count'] = result['application_count']
                company['trending_score'] = result['trending_score']
                trending_companies.append(company)
        
        return jsonify({
            'trending_companies': trending_companies,
            'count': len(trending_companies)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
