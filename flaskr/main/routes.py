from flask import Blueprint, request, redirect, render_template, url_for, session, jsonify
from flaskr import db, bucket
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
# import json
from firebase_admin import firestore, storage
import datetime


main = Blueprint('main', __name__)

@main.route("/")
def home():
    # return render_template("login.html")
    # Check if user is authenticated
    if 'uid' in session:
        return redirect(url_for('main.garden'))
    return redirect(url_for('main.login'))

@main.route('/login')
def login():
    return render_template('login.html')


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


@main.route('/profile')
def profile():
    if 'uid' in session:
        user_ref = db.collection('users').document(session['uid'])
        user_doc = user_ref.get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            if 'dateJoined' in user_data:
                user_data['dateJoined'] = user_data['dateJoined'].strftime('%B %d, %Y')
            return render_template('profile.html', user=user_data)
        else:
            return redirect(url_for('main.login'))
    return redirect(url_for('main.login'))

@main.route('/friends')
def friend():
    if 'uid' in session:
        user = firebase_auth.get_user(session['uid'])
        return render_template('friends.html', user=user)
    else:
        return redirect(url_for('main.login'))
    
@main.route('/new')
def create_post():
    if 'uid' in session:
        user = firebase_auth.get_user(session['uid'])
        return render_template('new.html', user=user) # change to addPlant.html if needed
    else:
        return redirect(url_for('main.login'))
    

@main.route('/journals')
def journal(): # beware that when you create route to journal, that this is rightfully renamed or the other is or might cause issues
    if 'uid' in session:
        user = firebase_auth.get_user(session['uid'])
        return render_template('journals.html', user=user)
    else:
        return redirect(url_for('main.login'))
    
@main.route('/settings')
def setting():
    # if 'uid' in session:
    #     user = firebase_auth.get_user(session['uid'])
    #     return render_template('settings.html', user=user)
    # else:
    #     return redirect(url_for('main.login'))
    
    if 'uid' in session:
        # Fetch the user's profile information from Firestore
        user_ref = db.collection('users').document(session['uid'])
        user_data = user_ref.get()
        
        if user_data.exists:
            blocked_users = []  # Retrieve blocked users (add logic to fetch blocked users)
            return render_template('settings.html', user=user_data.to_dict(), blocked_users=blocked_users)
        else:
            return redirect(url_for('login'))
    return redirect(url_for('login'))


# Update Username route
@main.route('/update-username', methods=['POST'])
def update_username():
    if 'uid' in session:
        data = request.get_json()
        new_username = data.get('username')

        try:
            # Update in Firebase Auth
            firebase_auth.update_user(session['uid'], display_name=new_username)

            # Update in Firestore
            user_ref = db.collection('users').document(session['uid'])
            user_ref.update({'username': new_username})

            return jsonify({'status': 'success', 'message': 'Username updated successfully.'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    return jsonify({'status': 'error', 'message': 'User not authenticated.'}), 403

# Update Email route
@main.route('/update-email', methods=['POST'])
def update_email():
    if 'uid' in session:
        data = request.get_json()
        new_email = data.get('email')

        try:
            # Update in Firebase Auth
            firebase_auth.update_user(session['uid'], email=new_email)

            # Update in Firestore
            user_ref = db.collection('users').document(session['uid'])
            user_ref.update({'email': new_email})

            return jsonify({'status': 'success', 'message': 'Email updated successfully.'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    return jsonify({'status': 'error', 'message': 'User not authenticated.'}), 403

# Update Password route
@main.route('/update-password', methods=['POST'])
def update_password():
    if 'uid' in session:
        data = request.get_json()
        new_password = data.get('password')

        try:
            # Update password in Firebase Auth
            firebase_auth.update_user(session['uid'], password=new_password)
            return jsonify({'status': 'success', 'message': 'Password updated successfully.'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    return jsonify({'status': 'error', 'message': 'User not authenticated.'}), 403

# Update Profile Photo route
@main.route('/update-photo', methods=['POST'])
def update_photo():
    if 'uid' in session:
        file = request.files.get('photo')
        
        if file:
            try:
                # Upload to Firebase Storage
                blob = bucket.blob(f'profile_photos/{session["uid"]}')
                blob.upload_from_file(file)
                
                # Get download URL
                photo_url = blob.public_url

                # Update user's photoURL in Firestore
                user_ref = db.collection('users').document(session['uid'])
                user_ref.update({'photo_url': photo_url})

                return jsonify({'status': 'success', 'message': 'Profile photo updated successfully.'})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)})
        return jsonify({'status': 'error', 'message': 'No photo provided.'}), 400
    return jsonify({'status': 'error', 'message': 'User not authenticated.'}), 403

# Fetch blocked users route (dummy route for now)
@main.route('/blocked-users', methods=['GET'])
def get_blocked_users():
    if 'uid' in session:
        # Logic to retrieve blocked users from Firestore or wherever you store the data
        blocked_users = []  # Replace with actual logic
        return jsonify({'status': 'success', 'blocked_users': blocked_users})
    return jsonify({'status': 'error', 'message': 'User not authenticated.'}), 403

# Search users route
@main.route('/search-users', methods=['POST'])
def search_users():
    if 'uid' in session:
        data = request.get_json()
        search_query = data.get('query')
        
        try:
            # Perform a query in Firestore to find users with matching username
            users_ref = db.collection('users')
            query = users_ref.where('username', '>=', search_query).where('username', '<=', search_query + '\uf8ff').limit(10)
            results = query.stream()
            
            users = [{'username': user.to_dict()['username'], 'email': user.to_dict()['email']} for user in results]

            return jsonify({'status': 'success', 'users': users})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    return jsonify({'status': 'error', 'message': 'User not authenticated.'}), 403


@main.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')  # Your forgot password page
