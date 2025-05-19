from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
import time

from app import db

notification_bp = Blueprint('notifications', __name__)

@notification_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_notifications():
    """Get all notifications for the current user with pagination."""
    current_user = get_jwt_identity()
    
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    skip = (page - 1) * per_page
    
    # Get filter parameters
    read_status = request.args.get('read')
    if read_status == 'true':
        read_filter = True
    elif read_status == 'false':
        read_filter = False
    else:
        read_filter = None
    
    # Build query
    query = {'recipient_id': current_user}
    if read_filter is not None:
        query['read'] = read_filter
    
    # Get total count
    total = db.notifications.count_documents(query)
    
    # Get notifications
    notifications = list(db.notifications.find(query).sort('timestamp', -1).skip(skip).limit(per_page))
    
    # Convert ObjectId to string for JSON serialization
    for notification in notifications:
        notification['_id'] = str(notification['_id'])
    
    return jsonify({
        'notifications': notifications,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }), 200

@notification_bp.route('/<notification_id>', methods=['GET'])
@jwt_required()
def get_notification(notification_id):
    """Get a specific notification by ID."""
    current_user = get_jwt_identity()
    
    try:
        # Validate the ObjectId format
        if not ObjectId.is_valid(notification_id):
            return jsonify({'error': 'Invalid notification ID format'}), 400
        
        # Find the notification
        notification = db.notifications.find_one({
            '_id': ObjectId(notification_id),
            'recipient_id': current_user
        })
        
        if not notification:
            return jsonify({'error': 'Notification not found or you do not have permission to view it'}), 404
        
        # Mark notification as read
        if not notification.get('read', False):
            db.notifications.update_one(
                {'_id': ObjectId(notification_id)},
                {'$set': {'read': True}}
            )
            notification['read'] = True
        
        # Convert ObjectId to string for JSON serialization
        notification['_id'] = str(notification['_id'])
        
        return jsonify({
            'notification': notification
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/mark-read/<notification_id>', methods=['PUT'])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    current_user = get_jwt_identity()
    
    try:
        # Validate the ObjectId format
        if not ObjectId.is_valid(notification_id):
            return jsonify({'error': 'Invalid notification ID format'}), 400
        
        # Find and update the notification
        result = db.notifications.update_one(
            {
                '_id': ObjectId(notification_id),
                'recipient_id': current_user
            },
            {'$set': {'read': True}}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Notification not found or you do not have permission to update it'}), 404
        
        return jsonify({
            'message': 'Notification marked as read'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/mark-all-read', methods=['PUT'])
@jwt_required()
def mark_all_notifications_read():
    """Mark all notifications as read for the current user."""
    current_user = get_jwt_identity()
    
    try:
        # Update all unread notifications for the user
        result = db.notifications.update_many(
            {
                'recipient_id': current_user,
                'read': False
            },
            {'$set': {'read': True}}
        )
        
        return jsonify({
            'message': f'{result.modified_count} notifications marked as read'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get the count of unread notifications for the current user."""
    current_user = get_jwt_identity()
    
    try:
        # Count unread notifications
        count = db.notifications.count_documents({
            'recipient_id': current_user,
            'read': False
        })
        
        return jsonify({
            'unread_count': count
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Helper function to create a notification (not exposed as an API endpoint)
def create_notification(recipient_id, title, message, notification_type, related_id=None):
    """
    Create a new notification for a user.
    
    Args:
        recipient_id (str): The ID of the recipient user
        title (str): The notification title
        message (str): The notification message
        notification_type (str): The type of notification (e.g., 'application', 'announcement')
        related_id (str, optional): The ID of the related object (e.g., application ID)
    
    Returns:
        str: The ID of the created notification
    """
    notification = {
        'recipient_id': recipient_id,
        'title': title,
        'message': message,
        'type': notification_type,
        'related_id': related_id,
        'timestamp': time.time(),
        'read': False
    }
    
    result = db.notifications.insert_one(notification)
    return str(result.inserted_id) if result.inserted_id else None
