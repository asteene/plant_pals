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
import json


main = Blueprint('main', __name__)

@main.route("/")
def home():
    # return render_template("login.html")
    # Check if user is authenticated
    # if 'uid' in session:
    #     return redirect(url_for('main.garden'))
    # return redirect(url_for('main.about'))
    if 'uid' in session:
        return redirect(url_for('main.garden')) 
    return redirect(url_for('main.login'))

# @main.route('/about')
# def about():
#     if 'uid' in session:
#         # Get the current user
#         user = firebase_auth.get_user(session['uid'])
#         uid = session['uid']
#         return render_template('about.html', user=user)
#     else:
#         return redirect(url_for('main.about'))
    

@main.route('/login', methods=['GET', 'POST'])
def login():
    # # return render_template('login.html') 
    if 'uid' in session:
        return redirect(url_for('main.garden'))
    # if request.method == 'POST':
    #     # Handle user login logic here
    #     return redirect(url_for('main.profile'))
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
        user_ref = db.collection('users').document(session['uid'])
        user_doc = user_ref.get()
        user_data = user_doc.to_dict()

        # Get the user's garden document from the Firestore database
        garden_ref = db.collection('garden').document(uid)
        garden_doc = garden_ref.get()

        # Initialize plant_ids as empty if no garden exists
        plant_ids = []
        my_garden = []
        potential_friends = []
        friend_request_details = []

        if garden_doc.exists:
            garden_data = garden_doc.to_dict()
            plant_ids = garden_data.get('plant_ids', [])

            for id in plant_ids:
                my_garden.append(trefle.get_species_by_id(id))

        # Get the current user's friends list
        friends_list = user_data['friends']

        # Retrieve the friend requests if they exist
        friend_reqs = user_data['friend_requests']

                
        if friend_reqs:
            # Fetch profile details for each friend request
            for requester_id in friend_reqs:
                requester_ref = db.collection('users').document(requester_id)
                requester_doc = requester_ref.get()
                if requester_doc.exists:
                    requester_data = requester_doc.to_dict()
                    friend_request_details.append({
                        'id': requester_id,
                        'profile_image': requester_data.get('profile_image', ''),  # Default to empty if no image
                        'username': requester_data.get('username', 'Unknown')      # Default if username missing
                    })

            # Get all users, excluding the current user and already friends
        users_ref = db.collection('users')
        users_query = users_ref.stream()

        # Build a list of users who are not the current user or already friends
            
        for doc in users_query:
            other_user = doc.to_dict()
            other_user_id = doc.id
                
            # Skip if the user is the current user or already a friend
            if other_user_id != uid and other_user_id not in friends_list:
                other_user['id'] = other_user_id  # Store the document ID as 'id'
                potential_friends.append(other_user)
        print(potential_friends)

        # Pass the plant_ids to the template for rendering
        return render_template('index.html', user=user_data, my_garden=my_garden, all_users=potential_friends, friend_reqs=friend_request_details)
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
    if True or request.method == 'POST':
        session.pop('uid', None)
        return redirect(url_for('main.login'))
    return redirect(url_for('main.login'))  # Fallback for GET requests


@main.route('/explore')
def profile():
    if 'uid' in session:
        user_ref = db.collection('users').document(session['uid'])
        user_doc = user_ref.get()

        if user_doc.exists:
            user_data = user_doc.to_dict()
            if 'dateJoined' in user_data:
                user_data['dateJoined'] = user_data['dateJoined'].strftime('%B %d, %Y')
            #user_data['friends_list'] = get_friends(user_data)
            all_posts = []

            if user_data['friends']: # fix
                # Reference the posts collection
                posts_ref = db.collection('posts')
                print(f"FRIENDS: {user_data['friends']}")
                for friend_id in user_data['friends']:
                    query = posts_ref.where('uid', '==', friend_id)
                    for doc in query.stream():

                        post = doc.to_dict()
                        post['id'] = doc.id  # Add the document ID to the dictionary
                        author_ref = db.collection('users').document(post['uid'])
                        author_doc = author_ref.get()
                        post['time_created'] = post['time_created'].strftime('%b %Y')
                        print(post['time_created'])
                        post['author'] = author_doc.to_dict()
                        all_posts.append(post)
                
            print(all_posts)
            print(user_data)
            return render_template('profile.html', user=user_data, all_posts=all_posts)
        else:
            return redirect(url_for('main.login'))
    return redirect(url_for('main.login'))

@main.route('/friends/<friend_id>/<journal_id>')
def friend_journal(friend_id, journal_id):
    if 'uid' in session:
        user_ref = db.collection('users').document(session['uid'])
        user_doc = user_ref.get()
        user_data = user_doc.to_dict()
        friend_ref = db.collection('users').document(friend_id)
        friend_doc = friend_ref.get()
        friend_data = friend_doc.to_dict()

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
                    post_data['id'] = post_id
                    posts.append(post_data)

            print(posts)

            if len(posts) == 0:
                posts = None
            # Pass the journal data and posts to the template
            return render_template('journal.html', journal_id=journal_id, user=user_doc, journal=journal_data, posts=posts, journal_name=journal_name, plant=plant, friend=friend_data)
       
    else:
        return redirect(url_for('main.login'))

@main.route('/friends/<friend_id>')
def friend(friend_id):
    if 'uid' in session:
        user_ref = db.collection('users').document(session['uid'])
        user_doc = user_ref.get()
        user_data = user_doc.to_dict()
        friend_ref = db.collection('users').document(friend_id)
        friend_doc = friend_ref.get()
             
        if friend_doc.exists:
            friend_data = friend_doc.to_dict()
            # Extract username and profile image
            friend_info = {
                "id": friend_doc.id,
                "username": friend_data.get("username"),
                "photoURL": friend_data.get("photoURL"),
                "friends": friend_data.get("friends"),
                'dateJoined' : friend_data['dateJoined'].strftime('%B %d, %Y')
            }

            print( friend_data.get("friends"))
            # Query to get all journals associated with the user's UID
            friend_journals_ref = db.collection('journals').where('uid', '==', friend_id).get()

            # Create a list to hold the journal documents
            friend_journals_list = []

            for journal in friend_journals_ref:
                journal_data = journal.to_dict()  # Convert to a dictionary
                journal_data['id'] = journal.id    # Add the document ID to the journal data
                print(journal_data)
                plant = trefle.get_species_by_id(journal_data['plant_id'])
                print(plant)
                journal_data['image'] = plant['image']
                journal_data['plant_name'] = plant['common_name']
                journal_data['sun'] = plant['maintenence']['sun_requirements']
                journal_data['sow'] = plant['maintenence']['sowing_method']
                friend_journals_list.append(journal_data)  # Append to the list
        return render_template('journals.html', user=user_data, friend=friend_info, friend_journals=friend_journals_list)
    else:
        return redirect(url_for('main.login'))

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
        plant_id = request.form.get('journal-plant-id')
        journal_title = request.form.get('journal-title')
        journal_desc = request.form.get('journal-description')

        # If plant_id is provided, create a new journal entry
        if plant_id:
            new_journal_ref = db.collection('journals').document()  # Firestore will generate a new doc ID
            # Create a new journal document with the plant_id
            new_journal_ref.set({
                'uid': uid,               # User's UID
                'name': journal_title,               # Placeholder for journal name
                'plant_id': plant_id, # Plant ID associated with this journal
                'post_ids': [],            # Empty list for posts
                'desc': journal_desc
            })

        # Redirect back to the garden page after creating the journal
        return redirect(url_for('main.journals'))
    else:
        return redirect(url_for('main.login'))


@main.route('/journals', methods=['POST', 'GET'])
def journals():
    if 'uid' in session:
        user = firebase_auth.get_user(session['uid'])
        user_ref = db.collection('users').document(session['uid'])
        user_doc = user_ref.get()
        # user_doc = user_doc.to_dict()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            if 'dateJoined' in user_data:
                user_data['dateJoined'] = user_data['dateJoined'].strftime('%B %d, %Y')
        uid = session['uid']

        # Query to get all journals associated with the user's UID
        friend_journals_ref = db.collection('journals').where('uid', '==', uid).get()

        # Create a list to hold the journal documents
        journals_list = []

        for journal in friend_journals_ref:
            journal_data = journal.to_dict()  # Convert to a dictionary
            journal_data['id'] = journal.id    # Add the document ID to the journal data
            print(journal_data)
            plant = trefle.get_species_by_id(journal_data['plant_id'])
            print(plant)
            journal_data['image'] = plant['image']
            journal_data['plant_name'] = plant['common_name']
            journal_data['sun'] = plant['maintenence']['sun_requirements']
            journal_data['sow'] = plant['maintenence']['sowing_method']
            journals_list.append(journal_data)  # Append to the list

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

        # Pass the journals list to the template
        return render_template('journals.html', user=user_data, journals=journals_list, my_garden=my_garden)
    else:
        return redirect(url_for('main.login'))

@main.route('/like/<post_id>', methods=['POST'])
def like_post(post_id):
    if 'uid' in session:
        uid = session['uid']

        journal_id = request.form.get('journal_id')
        
        # Reference to the post document in Firestore
        post_ref = db.collection('posts').document(post_id)
        post_doc = post_ref.get()
        
        # Check if the post exists
        if post_doc.exists:
            post_data = post_doc.to_dict()
            
            # If likes[] doesn't exist, initialize it as an empty array
            if 'likes' not in post_data:
                post_data['likes'] = []
            
            # Check if the user already liked the post
            if uid not in post_data['likes']:
                # Add the user ID to the likes array
                post_data['likes'].append(uid)
                
                # Update the post with the new likes array
                post_ref.update({
                    'likes': post_data['likes']
                })
            
            # Redirect the user back to the post page
            return redirect(url_for('main.journal', journal_id=journal_id))
        else:
            return jsonify({'status': 'error', 'message': 'Post not found'}), 404
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
            #print(post_ids)
            posts = []

            # Loop through post_ids and fetch each post from the posts collection
            for post_id in post_ids:
                post_ref = db.collection('posts').document(post_id)
                post_doc = post_ref.get()
                if post_doc.exists:
                    post_data = post_doc.to_dict()
                    timestamp = post_data['time_created'].timestamp() 
                    post_data['time_readable'] = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%B %d, %Y')  # Format the date
                    post_data['id'] = post_id
                    
                    comment_ids = post_data.get('comments', [])
                    comments = []
                    if comment_ids:    
                        for comment_id in comment_ids:
                            comment_ref = db.collection('comments').document(comment_id)
                            comment_data = comment_ref.get().to_dict()
                            comment_data['id'] = comment_id  # Include the comment document ID
                            comment_author = db.collection('users').document(comment_data['uid']).get().to_dict()
                            comment_data['author'] = comment_author
                            comments.append(comment_data)
                        
                    post_data['comments'] = comments
                    
                    posts.append(post_data)
            for p in posts:
                print(f"{p['title']}: {p['comments']}")

            if len(posts) == 0:
                posts = None
            # Pass the journal data and posts to the template
            return render_template('journal.html', journal_id=journal_id, user=user_doc, journal=journal_data, posts=posts, journal_name=journal_name, plant=plant)
    else:
        return redirect(url_for('main.login'))
    
@main.route('/add_comment', methods=['POST'])
def add_comment():
    # Get data from the request
    comment_text = request.form.get('comment')
    post_id = request.form.get('post_id')
    user_id = session.get('uid')
    journal_id = request.form.get('journal_id')

    if not comment_text or not post_id or not user_id:
        return jsonify({'error': 'Missing required fields'}), 400

    # Reference to the post and comments collection
    post_ref = db.collection('posts').document(post_id)
    comments_ref = db.collection('comments')

    # Create a new comment document
    comment_data = {
        'comment': comment_text,
        'uid': user_id
    }
    new_comment_ref = comments_ref.add(comment_data)  # Add the comment to the Firestore

    # Get the comment ID
    new_comment_id = new_comment_ref[1].id

    # Update the post document's comments[] field
    try:
        post_doc = post_ref.get()
        if post_doc.exists:
            post_data = post_doc.to_dict()
            if 'comments' in post_data:
                # Append the comment ID to the existing comments[] field
                post_ref.update({'comments': firestore.ArrayUnion([new_comment_id])})
            else:
                # Create the comments[] field and add the comment ID
                post_ref.update({'comments': [new_comment_id]})
        else:
            return jsonify({'error': 'Post not found'}), 404

        #return jsonify({'success': True, 'comment_id': new_comment_id}), 200
        return redirect(url_for('main.journal', journal_id=journal_id))

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@main.route('/posts/update/<post_id>', methods=['PUT'])
def update_post(post_id):
    # Step 2: Create a function to handle the update logic
    data = request.get_json()  # or request.form if you're using form data
    new_content = data.get('content')  # Assuming your JSON has a 'content' field

    if not new_content:
        return jsonify({"error": "No content provided"}), 400

    # Step 3: Update the post in the database
    try:
        # Assuming you're using Firebase's Python SDK
        db.collection('posts').document(post_id).update({
            'content': new_content
        })

        return jsonify({"message": "Post updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/posts/delete/<post_id>', methods=['POST'])
def delete_post(post_id):
    if 'uid' in session:
        uid = session['uid']
        
        # Reference to the post document in Firestore
        post_ref = db.collection('posts').document(post_id)
        post_doc = post_ref.get()
        
        # Check if the post exists and belongs to the current user
        if post_doc.exists:
            post_data = post_doc.to_dict()
            if post_data.get('uid') == uid:
                # Remove post_id from the associated journal's post_ids array
                journal_id = post_data.get('journal_id')
                if journal_id:
                    journal_ref = db.collection('journals').document(journal_id)
                    journal_ref.update({
                        'post_ids': firestore.ArrayRemove([post_id])
                    })

                # Remove all comments related to the post
                if 'comments' in post_data:
                    comment_ids = post_data['comments']
                    for comment_id in comment_ids:
                        comment_ref = db.collection('comments').document(comment_id)
                        comment_ref.delete()
                
                # Delete the post document from Firestore
                post_ref.delete()
                return redirect(url_for('main.journal', journal_id=journal_id))
            else:
                return jsonify({'status': 'error', 'message': 'Unauthorized action'}), 403
        else:
            return jsonify({'status': 'error', 'message': 'Post not found'}), 404
    else:
        return redirect(url_for('main.login'))


@main.route('/journals/<journal_id>/delete', methods=['POST'])
def delete_journal(journal_id):
    if 'uid' in session:
        # Fetch the journal document reference
        journal_ref = db.collection('journals').document(journal_id)

        # Check if the journal document exists
        journal_doc = journal_ref.get()
        if journal_doc.exists:
            # Delete all associated posts
            posts_ref = db.collection('posts')
            posts_query = posts_ref.where('journal_id', '==', journal_id)

            # Fetch and delete each associated post
            posts = posts_query.stream()
            for post in posts:
                post.reference.delete()
            
            journal_ref.delete()
            return redirect(url_for('main.journals'))
        else:
            # Handle case where the journal does not exist
            return jsonify({'status': 'error', 'message': 'Journal not found'}), 404
    else:
        return redirect(url_for('main.login'))


@main.route('/addplant', methods=['POST', 'GET'])
def add_plant():
    # call the api for the default values
    

    if 'uid' in session:
        user = firebase_auth.get_user(session['uid'])
        default_plants = trefle.get_default_plants()

        # Get user's uid from session
        uid = session['uid']

        #uid = session['uid']
        user_ref = db.collection('users').document(session['uid'])
        user_doc = user_ref.get()
        user_doc = user_doc.to_dict()


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

        return render_template('addPlant.html', user=user_doc, default_plants=default_plants)
    else:
        return redirect(url_for('main.login'))


@main.route('/settings')
def setting():
    if 'uid' in session:
        # Fetch the user's profile information from Firestore
        user_ref = db.collection('users').document(session['uid'])
        user_data = user_ref.get()
        
        if user_data.exists:
            # Retrieve the blocked users (add logic to fetch blocked users)
            blocked_users = []  
            current_user_id = session['uid']
            
            # Get the current user's friends list
            friends_list = user_data.to_dict().get('friends', [])

            # Get all users, excluding the current user and already friends
            users_ref = db.collection('users')
            users_query = users_ref.stream()

            # Build a list of users who are not the current user or already friends
            potential_friends = []
            for doc in users_query:
                user = doc.to_dict()
                user_id = doc.id

                # Retrieve the friend requests if they exist
                friend_reqs = user.get('friend_requests', [])

                friend_request_details = []

                 # Fetch profile details for each friend request
                for requester_id in friend_reqs:
                    requester_ref = db.collection('users').document(requester_id)
                    requester_doc = requester_ref.get()
                    if requester_doc.exists:
                        requester_data = requester_doc.to_dict()
                        friend_request_details.append({
                            'id': requester_id,
                            'profile_image': requester_data.get('profile_image', ''),  # Default to empty if no image
                            'username': requester_data.get('username', 'Unknown')      # Default if username missing
                        })

                print(friend_request_details)
                
                # Skip if the user is the current user or already a friend
                if user_id != current_user_id and user_id not in friends_list:
                    user['id'] = user_id  # Store the document ID as 'id'
                    potential_friends.append(user)

            return render_template('settings.html', user=user_data.to_dict(), blocked_users=blocked_users, all_users=potential_friends, friend_reqs=friend_request_details)
        
        else:
            return redirect(url_for('login'))
    
    return redirect(url_for('login'))

@main.route('/search_users')
def search_users():
    query = request.args.get('query', '').lower()
    if not query:
        return jsonify([])

    users_ref = db.collection('users')
    results = []

    # Firestore doesn't support "startsWith" directly, so we manually filter results
    docs = users_ref.stream()
    for doc in docs:
        user_data = doc.to_dict()
        if user_data['username'].lower().startswith(query):  # Ensure it starts with the query
            results.append({
                'id': doc.id,
                'username': user_data['username'],
                'photoURL': user_data.get('photoURL', '')  # Include photoURL if available
            })

    return jsonify(results)



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


@main.route('/add_friend/<friend_id>', methods=['POST'])
def add_friend(friend_id):
    if 'uid' in session:
        current_user_id = session['uid']

        # Get the current user document
        user_ref = db.collection('users').document(current_user_id)
        user_doc = user_ref.get()

        # Get the friend document
        friend_ref = db.collection('users').document(friend_id)
        friend_doc = friend_ref.get()

        if user_doc.exists and friend_doc.exists:
            user_data = user_doc.to_dict()
            friend_data = friend_doc.to_dict()

            # Ensure 'friends' field exists for the current user
            if 'friends' not in user_data:
                user_ref.update({'friends': []})
                user_data['friends'] = []

            # Ensure 'friend_requests' field exists for the friend user
            if 'friend_requests' not in friend_data:
                friend_ref.update({'friend_requests': []})
                friend_data['friend_requests'] = []

            # Add the friend_id to the user's friends list if not already in it
            if friend_id not in user_data['friends']:
                user_data['friends'].append(friend_id)
                user_ref.update({'friends': user_data['friends']})

            # Add the current user ID to the friend's friend_requests list if not already in it
            if current_user_id not in friend_data['friend_requests']:
                friend_data['friend_requests'].append(current_user_id)
                friend_ref.update({'friend_requests': friend_data['friend_requests']})


            return redirect(url_for('main.new_friends'))
            #return redirect(url_for('main.setting'))  # Or wherever you want to redirect after adding a friend
        else:
            return "User not found", 404
    else:
        return redirect(url_for('main.login'))
    
@main.route('/accept_friend/<requester_id>', methods=['POST'])
def accept_friend(requester_id):
    if 'uid' in session:
        current_user_id = session['uid']

        # Get the current user document
        user_ref = db.collection('users').document(current_user_id)
        user_doc = user_ref.get()

        # Get the requester document
        requester_ref = db.collection('users').document(requester_id)
        requester_doc = requester_ref.get()

        if user_doc.exists and requester_doc.exists:
            user_data = user_doc.to_dict()
            requester_data = requester_doc.to_dict()

            # Ensure 'friends' field exists for both users
            if 'friends' not in user_data:
                user_data['friends'] = []
            if 'friends' not in requester_data:
                requester_data['friends'] = []

            # Ensure 'friend_requests' field exists for the current user
            if 'friend_requests' not in user_data:
                user_data['friend_requests'] = []

            # Remove requester from current user's friend requests
            if requester_id in user_data['friend_requests']:
                user_data['friend_requests'].remove(requester_id)

            # Add each other as friends
            if requester_id not in user_data['friends']:
                user_data['friends'].append(requester_id)
            if current_user_id not in requester_data['friends']:
                requester_data['friends'].append(current_user_id)

            # Update Firestore documents
            user_ref.update({
                'friend_requests': user_data['friend_requests'],
                'friends': user_data['friends']
            })
            requester_ref.update({
                'friends': requester_data['friends']
            })

            return redirect(url_for('main.setting'))
        else:
            return "User not found", 404
    else:
        return redirect(url_for('main.login'))

    
@main.route('/remove_friend/<friend_id>', methods=['POST'])
def remove_friend(friend_id):
    if 'uid' in session:
        # Fetch the current user's data
        current_user_ref = db.collection('users').document(session['uid'])
        current_user_data = current_user_ref.get()

        if current_user_data.exists:
            # Get the current user's friends list
            friends_list = current_user_data.to_dict().get('friends', [])

            # Check if the given user (uid) is in the friends list
            if friend_id in friends_list:
                # Remove the uid from the friends list
                friends_list.remove(friend_id)
                
                # Update the current user's document to reflect the change
                current_user_ref.update({
                    'friends': friends_list
                })

                # Optionally, you could also remove this user from the other user's friend list
                # (If you want to keep the relationship bi-directional)
                friend_ref = db.collection('users').document(friend_id)
                friend_data = friend_ref.get()

                if friend_data.exists:
                    friend_friends_list = friend_data.to_dict().get('friends', [])
                    if session['uid'] in friend_friends_list:
                        friend_friends_list.remove(session['uid'])
                        friend_ref.update({
                            'friends': friend_friends_list
                        })

                return redirect(url_for('main.new_friends'))
                #return redirect(url_for('main.setting'))  # Or wherever you want to redirect after adding a friend
            else:
                # If the user is not in the friends list
                return "User is not in your friends list.", 400
        else:
            return redirect(url_for('login'))  # If no user is logged in
    
    return redirect(url_for('login'))  # If 'uid' is not in session


@main.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')  # Your forgot password page

#Error Handler for 404 Page Not Found
@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def get_friends(user_data):
    friends_info = []

    print(user_data)

    for friend_id in user_data['friends']:
        # Reference each friend document by their ID
        friend_ref = db.collection('users').document(friend_id)
        friend_doc = friend_ref.get()
             
        if friend_doc.exists:
            friend_data = friend_doc.to_dict()
            # Extract username and profile image
            friend_info = {
                "id": friend_doc.id,
                "username": friend_data.get("username"),
                "photoURL": friend_data.get("photoURL")
            }
            friends_info.append(friend_info)

    return friends_info

@main.route('/friends') 
def new_friends():
    if 'uid' in session:
        user_ref = db.collection('users').document(session['uid'])
        user_doc = user_ref.get()

        if user_doc.exists:
            user_data = user_doc.to_dict()

            # Fetch the user's friends
            friends_ids = user_data.get('friends', [])
            friends_data = []
            for friend_id in friends_ids:
                friend_doc = db.collection('users').document(friend_id).get()
                if friend_doc.exists:
                    friend_info = friend_doc.to_dict()
                    friend_info['UID'] = friend_id  # Include UID for linking profiles
                    friends_data.append(friend_info)

            # Fetch friend requests
            friend_reqs_ids = user_data.get('friend_requests', [])
            friend_reqs = []
            for requester_id in friend_reqs_ids:
                requester_doc = db.collection('users').document(requester_id).get()
                if requester_doc.exists:
                    requester_data = requester_doc.to_dict()
                    friend_reqs.append({
                        'id': requester_id,
                        'username': requester_data.get('username', 'Unknown'),
                        'photoURL': requester_data.get('photoURL', '')  # Default to empty if missing
                    })

            return render_template(
                'new_friends.html',
                user=user_data,
                friends=friends_data,
                friend_reqs=friend_reqs
            )

    return redirect('/login')
