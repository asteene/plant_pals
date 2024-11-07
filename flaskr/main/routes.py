from flask import Blueprint, request, redirect, render_template, url_for, session, jsonify
from flaskr import db, bucket
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
# import json
from firebase_admin import firestore, storage
import datetime
from datetime import datetime, timezone

import flaskr.utils.api as trefle
import uuid 


main = Blueprint('main', __name__)

@main.route("/")
def home():
    # return render_template("login.html")
    # Check if user is authenticated
    if 'uid' in session:
        return redirect(url_for('main.garden'))
    return redirect(url_for('main.about'))

@main.route('/about')
def about():
    if 'uid' in session:
        # Get the current user
        user = firebase_auth.get_user(session['uid'])
        uid = session['uid']
        return render_template('about.html', user=user)
    else:
        return redirect(url_for('main.about'))
    

@main.route('/login', methods=['GET', 'POST'])
def login():
    if 'uid' in session:
        return redirect(url_for('main.garden'))
    if request.method == 'POST':
        # Handle user login logic here
        return redirect(url_for('main.profile'))
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
    if 'uid' in session:
        # Get the current user
        user = firebase_auth.get_user(session['uid'])
        uid = session['uid']

        # Get the user's garden document from the Firestore database
        garden_ref = db.collection('garden').document(uid)
        garden_doc = garden_ref.get()

        # Initialize plant_ids as empty if no garden exists
        plant_ids = []
        my_garden = []

        if garden_doc.exists:
            garden_data = garden_doc.to_dict()
            plant_ids = garden_data.get('plant_ids', [])

            for id in plant_ids:
                my_garden.append(trefle.get_species_by_id(id))

        # Pass the plant_ids to the template for rendering
        return render_template('index.html', user=user, my_garden=my_garden)
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
    
''' 
@main.route('/new')
def create_post(): # TODO change to add_plant?
    if 'uid' in session:
        user = firebase_auth.get_user(session['uid'])
        return render_template('new.html', user=user) # change to addPlant.html if needed
    else:
        return redirect(url_for('main.login'))
'''

@main.route('/create_post', methods=['POST','GET'])
def create_post():
    if 'uid' in session:
        uid = session['uid']

        journal_id = request.form.get('journal_id')
        title = request.form.get('title')
        content = request.form.get('content')

        # Handle image upload if provided
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file:
                filename = str(uuid.uuid4()) + '.' + file.filename.split('.')[-1]
                blob = bucket.blob(filename)
                blob.upload_from_file(file)
                image_url = blob.public_url
        
        # If plant_id is provided, create a new journal entry
        if journal_id:
            new_post_ref = db.collection('posts').document()  # Firestore will generate a new doc ID

            # Create a new journal document with the plant_id
            new_post_ref.set({
                'uid': uid,               # User's UID
                'title': title,               # Placeholder for journal name
                'journal_id': journal_id, # Plant ID associated with this journal
                'text': content,
                'image_url': image_url,
                'time_created': datetime.now()
            })

            journal_ref = db.collection('journals').document(journal_id)
            journal_ref.update({
                'post_ids': firestore.ArrayUnion([new_post_ref.id])  # Use ArrayUnion to append the post ID
            })

        # Redirect back to the garden page after creating the journal
        return redirect(url_for('main.journal', journal_id=journal_id))
    else:
        return redirect(url_for('main.login'))

@main.route('/create_journal', methods=['POST','GET'])
def create_journal():
    if 'uid' in session:
        uid = session['uid']

        # Get plant_id from the form data
        plant_id = request.form.get('plant_id')

        # If plant_id is provided, create a new journal entry
        if plant_id:
            journals_ref = db.collection('journals')
            query = journals_ref.where('uid', '==', uid).where('plant_id', '==', int(plant_id)).limit(1)
            existing_journal = query.stream()

            # Check if a journal with this plant_id already exists
            journal_list = list(existing_journal)
            if journal_list:  # If a journal already exists
                existing_journal_id = journal_list[0].id  # Get the document ID of the existing journal
                return redirect(url_for('main.journal', journal_id=existing_journal_id))

            new_journal_ref = db.collection('journals').document()  # Firestore will generate a new doc ID
            # Create a new journal document with the plant_id
            new_journal_ref.set({
                'uid': uid,               # User's UID
                'name': '',               # Placeholder for journal name
                'plant_id': int(plant_id), # Plant ID associated with this journal
                'post_ids': [],            # Empty list for posts
                'desc': 'Test Description until the form is implemented'
            })

        # Redirect back to the garden page after creating the journal
        return redirect(url_for('main.garden'))
    else:
        return redirect(url_for('main.login'))


@main.route('/journals', methods=['POST', 'GET'])
def journals():
    if 'uid' in session:
        user = firebase_auth.get_user(session['uid'])
        user_ref = db.collection('users').document(session['uid'])
        user_doc = user_ref.get()
        user_doc = user_doc.to_dict()
        uid = session['uid']

        # Query to get all journals associated with the user's UID
        journals_ref = db.collection('journals').where('uid', '==', uid).get()

        # Create a list to hold the journal documents
        journals_list = []

        for journal in journals_ref:
            journal_data = journal.to_dict()  # Convert to a dictionary
            journal_data['id'] = journal.id    # Add the document ID to the journal data
            print(journal_data)
            plant = trefle.get_species_by_id(int(journal_data['plant_id']))
            print(plant)
            journal_data['image'] = plant['image']
            journal_data['plant_name'] = plant['common_name']
            journals_list.append(journal_data)  # Append to the list

        # Pass the journals list to the template
        return render_template('journals.html', user=user_doc, journals=journals_list)
    else:
        return redirect(url_for('main.login'))

@main.route('/journals/<journal_id>')
def journal(journal_id): # beware that when you create route to journal, that this is rightfully renamed or the other is or might cause issues
    if 'uid' in session:
        user = firebase_auth.get_user(session['uid'])
        user_ref = db.collection('users').document(session['uid'])
        user_doc = user_ref.get()
        user_doc = user_doc.to_dict()

        # Fetch the journal document based on journal_id
        journal_ref = db.collection('journals').document(journal_id)
        journal_doc = journal_ref.get()

        if journal_doc.exists:
            # Convert the document to a dictionary
            journal_data = journal_doc.to_dict()

            # Get other relevant journal information (like name, plant_id, etc.)
            journal_name = journal_data.get('name', 'Untitled Journal')
            plant_id = journal_data.get('plant_id', -1)  # Assuming -1 means no plant associated

            plant = trefle.get_species_by_id(plant_id)

            # Fetch the posts from the journal, assuming they are stored in an array under 'post_ids'
            post_ids = journal_data.get('post_ids', [])
            print(post_ids)
            posts = []

            # Loop through post_ids and fetch each post from the posts collection
            for post_id in post_ids:
                post_ref = db.collection('posts').document(post_id)
                post_doc = post_ref.get()
                if post_doc.exists:
                    post_data = post_doc.to_dict()
                    timestamp = post_data['time_created'].timestamp() 
                    post_data['time_readable'] = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%B %d, %Y')  # Format the date
                    posts.append(post_data)

            print(posts)

            if len(posts) == 0:
                posts = None
            # Pass the journal data and posts to the template
            return render_template('journal.html', journal_id=journal_id, user=user_doc, journal=journal_data, posts=posts, journal_name=journal_name, plant=plant)
    else:
        return redirect(url_for('main.login'))


@main.route('/addplant', methods=['POST', 'GET'])
def add_plant():
    # call the api for the default values
    

    if 'uid' in session:
        user = firebase_auth.get_user(session['uid'])
        default_plants = trefle.get_default_species()

        # Get user's uid from session
        uid = session['uid']

        # Check if the garden document exists for the user
        garden_ref = db.collection('garden').document(uid)
        garden_doc = garden_ref.get()

        # If garden document doesn't exist, create it
        if not garden_doc.exists:
            garden_ref.set({
                'uid': uid,
                'plant_ids': []
            })

        # Check if it's a POST request to add a plant
        if request.method == 'POST':
            # Get plant_id from form data
            plant_id = request.form.get('plant_id')

            # If plant_id is provided, add it to the garden
            if plant_id:
                garden_data = garden_ref.get().to_dict()
                plant_ids = garden_data.get('plant_ids', [])

                # Add the new plant_id to the list if it's not already there
                if plant_id not in plant_ids:
                    plant_ids.append(plant_id)
                    garden_ref.update({'plant_ids': plant_ids})

            return redirect(url_for('main.garden'))

        

        return render_template('addPlant.html', user=user, default_plants=default_plants)
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

@main.route('/upload_image', methods=['POST'])
def upload_image():
    if 'uid' in session:
        file = request.files.get('image')
        if file:
            # Create a unique name for the image
            filename = str(uuid.uuid4()) + '.' + file.filename.split('.')[-1]
            blob = bucket.blob(filename)
            blob.upload_from_file(file)
            image_url = blob.public_url
            return jsonify({'status': 'success', 'image_url': image_url})
        return jsonify({'status': 'error', 'message': 'No image uploaded'}), 400
    return jsonify({'status': 'error', 'message': 'User not authenticated'}), 401


# # Update Username route
# @main.route('/update-username', methods=['POST'])
# def update_username():
#     if 'uid' in session:
#         data = request.get_json()
#         new_username = data.get('username')

#         try:
#             # Update in Firebase Auth
#             firebase_auth.update_user(session['uid'], display_name=new_username)

#             # Update in Firestore
#             user_ref = db.collection('users').document(session['uid'])
#             user_ref.update({'username': new_username})

#             return jsonify({'status': 'success', 'message': 'Username updated successfully.'})
#         except Exception as e:
#             return jsonify({'status': 'error', 'message': str(e)})
#     return jsonify({'status': 'error', 'message': 'User not authenticated.'}), 403

# # Update Email route
# @main.route('/update-email', methods=['POST'])
# def update_email():
#     if 'uid' in session:
#         data = request.get_json()
#         new_email = data.get('email')

#         try:
#             # Update in Firebase Auth
#             firebase_auth.update_user(session['uid'], email=new_email)

#             # Update in Firestore
#             user_ref = db.collection('users').document(session['uid'])
#             user_ref.update({'email': new_email})

#             return jsonify({'status': 'success', 'message': 'Email updated successfully.'})
#         except Exception as e:
#             return jsonify({'status': 'error', 'message': str(e)})
#     return jsonify({'status': 'error', 'message': 'User not authenticated.'}), 403

# # Update Password route
# @main.route('/update-password', methods=['POST'])
# def update_password():
#     if 'uid' in session:
#         data = request.get_json()
#         new_password = data.get('password')

#         try:
#             # Update password in Firebase Auth
#             firebase_auth.update_user(session['uid'], password=new_password)
#             return jsonify({'status': 'success', 'message': 'Password updated successfully.'})
#         except Exception as e:
#             return jsonify({'status': 'error', 'message': str(e)})
#     return jsonify({'status': 'error', 'message': 'User not authenticated.'}), 403

# # Update Profile Photo route
# @main.route('/update-photo', methods=['POST'])
# def update_photo():
#     if 'uid' in session:
#         file = request.files.get('photo')
        
#         if file:
#             try:
#                 # Upload to Firebase Storage
#                 blob = bucket.blob(f'profile_photos/{session["uid"]}')
#                 blob.upload_from_file(file)
                
#                 # Get download URL
#                 photo_url = blob.public_url

#                 # Update user's photoURL in Firestore
#                 user_ref = db.collection('users').document(session['uid'])
#                 user_ref.update({'photo_url': photo_url})

#                 return jsonify({'status': 'success', 'message': 'Profile photo updated successfully.'})
#             except Exception as e:
#                 return jsonify({'status': 'error', 'message': str(e)})
#         return jsonify({'status': 'error', 'message': 'No photo provided.'}), 400
#     return jsonify({'status': 'error', 'message': 'User not authenticated.'}), 403

# # Fetch blocked users route (dummy route for now)
# @main.route('/blocked-users', methods=['GET'])
# def get_blocked_users():
#     if 'uid' in session:
#         # Logic to retrieve blocked users from Firestore or wherever you store the data
#         blocked_users = []  # Replace with actual logic
#         return jsonify({'status': 'success', 'blocked_users': blocked_users})
#     return jsonify({'status': 'error', 'message': 'User not authenticated.'}), 403

# # Search users route
# @main.route('/search-users', methods=['POST'])
# def search_users():
#     if 'uid' in session:
#         data = request.get_json()
#         search_query = data.get('query')
        
#         try:
#             # Perform a query in Firestore to find users with matching username
#             users_ref = db.collection('users')
#             query = users_ref.where('username', '>=', search_query).where('username', '<=', search_query + '\uf8ff').limit(10)
#             results = query.stream()
            
#             users = [{'username': user.to_dict()['username'], 'email': user.to_dict()['email']} for user in results]

#             return jsonify({'status': 'success', 'users': users})
#         except Exception as e:
#             return jsonify({'status': 'error', 'message': str(e)})
#     return jsonify({'status': 'error', 'message': 'User not authenticated.'}), 403


@main.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')  # Your forgot password page

#Error Handler for 404 Page Not Found
@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404