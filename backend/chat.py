from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
from pymongo import MongoClient

# Create a blueprint for the chat functionality
chat_bp = Blueprint('chat', __name__)

# MongoDB connection
client = MongoClient("mongodb+srv://sahakartik2952004:8tXLrkqXsnfUEidN@cluster.l9tvc.mongodb.net/")  # Use the correct connection string
db = client['healthbot']
users_collection = db['users']

# Initialize Flask-SocketIO
socketio = SocketIO()

# Route for the chat page (chatroom)
@chat_bp.route('/chatroom')  # Changed from /home to /chatroom to avoid conflict
def chatroom():
    if 'username' in session:
        return render_template('chatroom.html', username=session['username'])
    return redirect(url_for('auth.login'))  # Redirect to login if no user session

# SocketIO handler for real-time chat communication
@socketio.on('send_message')
def handle_message(data):
    user_message = data['message']
    
    # Check if a username exists in the session and format the bot response with the username
    username = session.get('username', 'User')
    assistant_response = f"You: {user_message}"

    # Emit the response back to the chat
    emit('receive_message', {'message': assistant_response, 'sender': 'assistant'}, broadcast=True)

# Remove unnecessary API endpoint, as the SocketIO is sufficient for chat functionality.
