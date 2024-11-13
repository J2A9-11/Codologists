from flask import Flask, render_template, session, redirect, url_for
from flask_session import Session
from flask_socketio import SocketIO
from auth import auth_bp  # Import the Blueprint for auth
from chat import chat_bp, socketio  # Import the Blueprint for chat and SocketIO
import os

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

# Set secret key for session management
app.secret_key = os.urandom(24)

# Register the auth Blueprint for login, signup, etc.
app.register_blueprint(auth_bp)

# Register the chat Blueprint for the chat functionality
app.register_blueprint(chat_bp)

# Flask session configuration
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Initialize SocketIO with the app
socketio.init_app(app)

# Route for home page (the one that was already defined)
@app.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('auth.login'))

# Default route for the root URL
@app.route('/')
def index():
    # Redirect to /home by default when visiting the root URL
    return redirect(url_for('home'))

# Start the Flask app and run SocketIO with it
if __name__ == "__main__":
    socketio.run(app, debug=True)
