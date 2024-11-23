from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

import requests

# Create Flask app
app = Flask(__name__)
app.config.from_object('config.Config')  # Load configuration from config.py

# Initialize database and login manager
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"  # Redirect to login if not authenticated

# User model


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

# Load user for Flask-Login


@login_manager.user_loader
def load_user(user_id):
    # Use session.get() to retrieve the user by primary key
    return User.query.get(int(user_id))

# Route for the login page


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password.', 'danger')
    return render_template('login.html')

# Route for the signup page


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validation
        if password != confirm_password:
            flash('Passwords must match!', 'danger')
            return redirect(url_for('signup'))

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('signup'))

        # Create new user and add to the database
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully. Please log in!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

# Route for the dashboard (authenticated)


@app.route('/')
@login_required
def home():
    return render_template('dashboard.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Route for logging out


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Route for uploading an image (POST)


# @app.route('/upload', methods=['POST'])
# @login_required
# def upload_image():
#     # Check if the image and name are in the request
#     name = request.form['name']
#     if 'image' not in request.files:
#         flash('No image file provided', 'danger')
#         return redirect(url_for('dashboard'))
#     file = request.files['image']
#     if file.filename == '':
#         flash('No selected file', 'danger')
#         return redirect(url_for('dashboard'))

#     if file:
#         # Save the file locally
#         filename = os.path.join('static/uploads', file.filename)
#         file.save(filename)

#         # Prepare the data as a JSON object
#         json_data = {
#             'name': name,
#             'image_path': os.path.join('static/uploads', file.filename)
#         }

#         # Send the data as JSON to the C++ API
#         url = "http://127.0.0.1:8080/api/v0/add"
#         try:
#             response = requests.post(url, json=json_data)  # Send as JSON
#             if response.status_code == 200:
#                 flash('Image uploaded and data sent to the C++ API successfully!', 'success')
#             else:
#                 flash('Failed to send data to the C++ API.', 'danger')
#         except Exception as e:
#             flash(f'Error uploading image: {str(e)}', 'danger')

#         return redirect(url_for('dashboard'))


@app.route('/upload', methods=['POST'])
@login_required
def upload_image():
    # Check if the image and name are in the request
    name = request.form['name']
    if 'image' not in request.files:
        flash('No image file provided', 'danger')
        return redirect(url_for('dashboard'))
    file = request.files['image']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('dashboard'))

    if file:
        # Save the file locally
        filename = os.path.join('static/uploads', file.filename)
        file.save(filename)

        # Send the file directly to the C++ API
        url = "http://127.0.0.1:8080/api/v0/add"
        try:
            # Prepare the file and data payload
            with open(filename, 'rb') as f:
                files = {'image': (file.filename, f, file.content_type)}
                data = {'name': name}
                response = requests.post(url, data=data, files=files)

            # Handle the response
            if response.status_code == 200:
                flash(
                    'Image uploaded and data sent to the C++ API successfully!', 'success')
            else:
                flash('Failed to send data to the C++ API.', 'danger')
        except Exception as e:
            flash(f'Error uploading image: {str(e)}', 'danger')

        return redirect(url_for('dashboard'))


# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables
    app.run(debug=True)
