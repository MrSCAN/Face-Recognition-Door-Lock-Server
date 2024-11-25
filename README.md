# Face Verification Access System (Web Portal Setup)

This project is a Python Flask application for managing a real-time face verification system using a Raspberry Pi, a camera module, and a C++ API for face detection and recognition. The system enables secure access control by verifying faces in real-time and providing an easy-to-use interface for managing user data.

---

## Overview

The Face Verification Access System is designed to enhance security and convenience by granting access based on recognized and verified faces. It integrates hardware, software, and machine learning technologies to provide a robust access control solution.

---

## Features

- **Real-Time Face Detection and Recognition**: Seamless integration with a C++ API for real-time processing.
- **Secure Access Control**: Only authorized personnel are granted access.
- **Customizable Face Database**: Easily manage and store face data via the Flask web interface.
- **Alerts and Notifications**: Real-time notifications for granted or denied access (optional feature).
- **User-Friendly Dashboard**: Manage users, faces, and devices via an intuitive web interface.

---

---

## Installation and Setup

## Step 0: Ensure You have setup the C++ + Yocto application on your Raspbery pi following the instruction in this [repository](https://github.com/cu-ecen-aeld/final-project-MrSCAN/wiki)

### Step 1: Clone the Repository
```bash
git clone git@github.com:MrSCAN/Face-Recognition-Door-Lock-Server.git
cd Face-Recognition-Door-Lock-Server
```

### Step 2: Create a Python Virtual Environment


```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure the Flask Application
Update the `config.py` file to include your database URI and secret key. Example:

```bash
class Config:
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
```

### Step 6: Run the Flask Application
Start the Flask server:

```bash
python3 app.py
```
---

### Future Enhancements
- Real-Time Alerts: Integrate email or SMS notifications for access logs.
+ Access Logs: Maintain a history of access attempts with timestamps.
* Mobile Support: Develop a mobile-friendly version of the interface.
