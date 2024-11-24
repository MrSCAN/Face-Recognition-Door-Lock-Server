from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
import requests
import json, uuid


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


# Device model
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# Face model
class Face(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    image_url = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())


# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
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
            flash('Login Unsuccessful. Please check username and password.',
                  'danger')
    return render_template('login.html')


# Route for the signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords must match!', 'danger')
            return redirect(url_for('signup'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.',
                  'danger')
            return redirect(url_for('signup'))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully. Please log in!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')


# Route for the dashboard (authenticated)
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    faces = Face.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', faces=faces)


@app.route('/add_face')
@login_required
def add_face():
    return render_template('add_face.html')


@app.route('/view_face/<int:face_id>')
@login_required
def view_face(face_id):
    face = Face.query.get_or_404(face_id)
    if face.user_id != current_user.id:
        flash('You do not have permission to view this face.', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('view_face.html', face=face)


@app.route('/delete_face/<int:face_id>', methods=['POST'])
@login_required
def delete_face(face_id):
    face = Face.query.get_or_404(face_id)
    if face.user_id != current_user.id:
        flash('You do not have permission to delete this face.', 'danger')
        return redirect(url_for('dashboard'))

    # Send the delete request to the C++ API
    url = "http://127.0.0.1:8080/api/v0/remove"
    try:
        # Prepare the JSON data
        data = json.dumps({'name': face.name})  # Send the face name in JSON format
        headers = {'Content-Type': 'application/json'}

        # Send the request to the API
        response = requests.post(url, data=data, headers=headers)

        # If the API call is successful, delete the face from the database and file
        if response.status_code == 200:
            # Delete the file from the disk
            file_path = os.path.join('static', face.image_url)  # Path of the file to be deleted
            if os.path.exists(file_path):
                os.remove(file_path)

            # Delete the face record from the database
            db.session.delete(face)
            db.session.commit()
            flash('Face deleted successfully from both the database and the device.', 'success')
        else:
            flash(f'Failed to delete face from the device: {response.text}', 'danger')
    except Exception as e:
        flash(f'Error deleting face from the device: {str(e)}', 'danger')

    return redirect(url_for('dashboard'))


# Route for logging out
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/upload', methods=['POST'])
@login_required
def upload_image():
    name = request.form['name']

    # Validate if an image file is provided
    if 'image' not in request.files:
        flash('No image file provided', 'danger')
        return redirect(url_for('add_face'))

    file = request.files['image']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('add_face'))

    if file:
        # Sanitize the filename
        filename = secure_filename(file.filename)
        filename = str(uuid.uuid4()) + os.path.splitext(filename)[1]


        # Define the paths
        relative_path = os.path.join(
            'uploads', filename)  # Path for database: 'uploads/scan.jpg'
        absolute_path = os.path.join(
            'static',
            relative_path)  # Full path for saving: 'static/uploads/scan.jpg'

        try:
            # Send the image and name to the C++ API first
            url = "http://127.0.0.1:8080/api/v0/add"
            files = {'image': (filename, file.stream, file.content_type)}
            data = {'name': name}
            response = requests.post(url, data=data, files=files)

            # If the API call is successful, save the file and update the database
            if response.status_code == 200:
                # Save the file to the static/uploads directory
                # Open the file in write-binary mode and write the stream content to it
                file.stream.seek(0)
                file.save(absolute_path)

                # Update the database with the new face
                face = Face(name=name,
                            image_url=relative_path,
                            user_id=current_user.id)
                db.session.add(face)
                db.session.commit()

                flash(
                    'Image uploaded and data sent to the C++ API successfully!',
                    'success')
            else:
                flash(f'Failed to send data to the C++ API: {response.text}',
                      'danger')
        except Exception as e:
            flash(f'Error uploading image to Device: {str(e)}', 'danger')

        return redirect(url_for('dashboard'))



# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables
    app.run(debug=True)