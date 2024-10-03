from flask import Blueprint, request, redirect, render_template, url_for, session, jsonify
from flaskr import db
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
# import json
from firebase_admin import firestore

main = Blueprint('main', __name__)

@main.route("/")
def home():
    # return render_template("login.html")
    # Check if user is authenticated
    if 'uid' in session:
        return redirect(url_for('garden'))
    return redirect(url_for('main.login'))

@main.route('/login')
def login():
    return render_template('login.html')

# @main.route('/signup')
# def signup():
#     return render_template('signup.html')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Handle user signup
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            user = firebase_auth.create_user(
                email=email,
                password=password,
                display_name=username
            )
            # Create a user document in Firestore
            user_ref = db.collection('users').document(user.uid)
            user_ref.set({
                'username': username,
                'email': email
            })

            return jsonify({'status': 'success', 'message': 'User created successfully'}), 201
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400

    return render_template('signup.html')

@main.route('/garden')
def garden():
    # return render_template('index.html')
    if 'uid' in session:
        user = firebase_auth.get_user(session['uid'])
        return render_template('index.html', user=user)
    else:
        return redirect(url_for('main.login'))

@main.route('/session', methods=['POST'])
def create_session():
    data = request.get_json()
    id_token = data.get('token')
    if id_token:
        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            session['uid'] = uid
            return jsonify({'status': 'success'})
        except firebase_admin.exceptions.FirebaseError as e:
            print(e)
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 400
    return jsonify({'status': 'error', 'message': 'No token provided'}), 400

@main.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.pop('uid', None)
        return redirect(url_for('main.login'))
    return redirect(url_for('main.login'))  # Fallback for GET requests

# db = firestore.client()

@main.route('/profile')
def profile():
    if 'uid' in session:
        user_ref = db.collection('users').document(session['uid'])
        user_data = user_ref.get()
        if user_data.exists:
            return render_template('profile.html', user=user_data.to_dict())
        else:
            return redirect(url_for('main.login'))
    return redirect(url_for('main.login'))
