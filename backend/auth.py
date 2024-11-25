from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from flask_bcrypt import Bcrypt

# Blueprint setup for auth routes
auth_bp = Blueprint('auth', __name__)

# MongoDB Atlas connection
client = MongoClient("mongodb+srv://sahakartik2952004:8tXLrkqXsnfUEidN@cluster.l9tvc.mongodb.net/")  # Update connection string if needed
db = client['healthbot']  # Database name in Atlas
users_collection = db['users']  # Collection name remains 'users'

# Initialize Bcrypt for password hashing
bcrypt = Bcrypt()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username exists in the database
        user = users_collection.find_one({'username': username})
        if user and bcrypt.check_password_hash(user['password'], password):
            session['username'] = username
            session['logged_in'] = True  # Set logged_in key
            return redirect(url_for('home'))  # Redirect to home page if login is successful
        else:
            flash("Invalid username or password")
            return redirect(url_for('auth.login'))  # Stay on the login page if authentication fails
    
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        # Check if the username already exists
        if users_collection.find_one({'username': username}):
            flash("Username already exists")
            return redirect(url_for('auth.signup'))  # Stay on the signup page if the username exists
        
        # Insert new user data
        users_collection.insert_one({
            'username': username,
            'password': password,
        })
        # Log the user in directly after signup
        session['username'] = username
        session['logged_in'] = True  # Set logged_in key
        flash("Signup successful!")
        return redirect(url_for('home'))  # Redirect to home page after successful signup
    
    return render_template('signup.html')

@auth_bp.route('/profile')
def profile():
    if not session.get('logged_in'):  # Check logged_in status
        flash("Please login to access your profile")
        return redirect(url_for('auth.login'))  # Redirect to login if not authenticated
    
    user = users_collection.find_one({'username': session['username']})
    return render_template('profile.html', username=user['username'])

@auth_bp.route('/update_profile', methods=['POST'])
def update_profile():
    if not session.get('logged_in'):  # Check logged_in status
        flash("Please login to update your profile")
        return redirect(url_for('auth.login'))  # Redirect to login if not authenticated
    
    user = users_collection.find_one({'username': session['username']})
    new_username = request.form['username']
    
    # Check and update username if changed
    if new_username != user['username']:
        if users_collection.find_one({'username': new_username}):
            flash("Username already taken")
            return redirect(url_for('auth.profile'))  # Stay on profile page if username exists
        
        session['username'] = new_username  # Update session with new username
        users_collection.update_one({'username': user['username']}, {'$set': {'username': new_username}})
    
    flash("Username updated successfully!")
    return redirect(url_for('auth.profile'))

@auth_bp.route('/update_password', methods=['POST'])
def update_password():
    if not session.get('logged_in'):  # Check logged_in status
        flash("Please login to update your password")
        return redirect(url_for('auth.login'))  # Redirect to login if not authenticated
    
    user = users_collection.find_one({'username': session['username']})
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    
    # Check if current password matches
    if bcrypt.check_password_hash(user['password'], current_password):
        if new_password == confirm_password:
            # Hash the new password and update
            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            users_collection.update_one({'username': session['username']}, {'$set': {'password': hashed_password}})
            flash("Password updated successfully!")
        else:
            flash("New passwords do not match")
    else:
        flash("Current password is incorrect")

    return redirect(url_for('auth.profile'))

@auth_bp.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    session.pop('logged_in', None)  # Remove logged_in key
    flash("You have been logged out")
    return redirect(url_for('auth.login'))  # Redirect to login page after logout
