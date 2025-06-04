"""
DEPRECATED: This module has been moved to app.archive.messages
Please use the archived_messages_bp from app.archive instead.
"""

# Keep imports for backwards compatibility
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from datetime import datetime

from app import db

# This blueprint is no longer used directly
# It is kept only for backward compatibility
message_bp = Blueprint('student_messages', __name__, url_prefix='/api/student/messages')

# Redirect to the archived module's implementation
@message_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_messages():
    """
    DEPRECATED: Redirects to archived implementation.
    Get all messages for the current user.
    """
    # Import the archived implementation
    from app.archive.messages import get_all_messages as archived_get_all_messages
    return archived_get_all_messages()

@message_bp.route('/<message_id>', methods=['GET'])
@jwt_required()
def get_message(message_id):
    """
    DEPRECATED: Redirects to archived implementation.
    Get a specific message by ID.
    """
    # Import the archived implementation
    from app.archive.messages import get_message as archived_get_message
    return archived_get_message(message_id)

@message_bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    """
    DEPRECATED: Redirects to archived implementation.
    Send a new message.
    """
    # Import the archived implementation
    from app.archive.messages import send_message as archived_send_message
    return archived_send_message()

@message_bp.route('/<message_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_message(message_id):
    """
    DEPRECATED: Redirects to archived implementation.
    Delete a message.
    """
    # Import the archived implementation
    from app.archive.messages import delete_message as archived_delete_message
    return archived_delete_message(message_id)
