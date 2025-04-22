from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from datetime import datetime

from app import db

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_messages():
    """Get all messages for the current user."""
    current_user = get_jwt_identity()
    
    # Get messages where the user is either sender or recipient
    messages = list(db.messages.find({
        '$or': [
            {'sender_id': current_user},
            {'recipient_id': current_user}
        ]
    }).sort('timestamp', -1))
    
    # Convert ObjectId to string for JSON serialization
    for message in messages:
        message['_id'] = str(message['_id'])
    
    return jsonify({
        'messages': messages
    }), 200

@messages_bp.route('/<message_id>', methods=['GET'])
@jwt_required()
def get_message(message_id):
    """Get a specific message by ID."""
    current_user = get_jwt_identity()
    
    try:
        # Validate the ObjectId format
        if not ObjectId.is_valid(message_id):
            return jsonify({'error': 'Invalid message ID format'}), 400
        
        # Find the message
        message = db.messages.find_one({
            '_id': ObjectId(message_id),
            '$or': [
                {'sender_id': current_user},
                {'recipient_id': current_user}
            ]
        })
        
        if not message:
            return jsonify({'error': 'Message not found or you do not have permission to view it'}), 404
        
        # Mark message as read if user is recipient
        if message['recipient_id'] == current_user and not message.get('read', False):
            db.messages.update_one(
                {'_id': ObjectId(message_id)},
                {'$set': {'read': True}}
            )
            message['read'] = True
        
        # Convert ObjectId to string for JSON serialization
        message['_id'] = str(message['_id'])
        
        return jsonify({
            'message': message
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@messages_bp.route('/', methods=['POST'])
@jwt_required()
def send_message():
    """Send a new message."""
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('recipient_id') or not data.get('content'):
        return jsonify({'error': 'Recipient ID and content are required'}), 400
    
    recipient_id = data.get('recipient_id')
    
    # Check if recipient exists
    recipient = db.students.find_one({'registration_no': recipient_id})
    if not recipient:
        return jsonify({'error': 'Recipient not found'}), 404
    
    # Create new message
    new_message = {
        'sender_id': current_user,
        'recipient_id': recipient_id,
        'content': data.get('content'),
        'subject': data.get('subject', ''),
        'timestamp': datetime.utcnow(),
        'read': False
    }
    
    # Insert the message
    result = db.messages.insert_one(new_message)
    
    if result.inserted_id:
        return jsonify({
            'message': 'Message sent successfully',
            'message_id': str(result.inserted_id)
        }), 201
    else:
        return jsonify({'error': 'Failed to send message'}), 500

@messages_bp.route('/<message_id>', methods=['DELETE'])
@jwt_required()
def delete_message(message_id):
    """Delete a message."""
    current_user = get_jwt_identity()
    
    try:
        # Validate the ObjectId format
        if not ObjectId.is_valid(message_id):
            return jsonify({'error': 'Invalid message ID format'}), 400
        
        # Check if message exists and belongs to the user
        message = db.messages.find_one({
            '_id': ObjectId(message_id),
            '$or': [
                {'sender_id': current_user},
                {'recipient_id': current_user}
            ]
        })
        
        if not message:
            return jsonify({'error': 'Message not found or you do not have permission to delete it'}), 404
        
        # Delete the message
        result = db.messages.delete_one({'_id': ObjectId(message_id)})
        
        if result.deleted_count:
            return jsonify({
                'message': 'Message deleted successfully'
            }), 200
        else:
            return jsonify({'error': 'Failed to delete message'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500