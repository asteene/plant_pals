from flaskr import createApp
# from flask import Flask, render_template

from flask import Flask, render_template, redirect, url_for, request, jsonify, session
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
# import json
from firebase_admin import firestore
import os



app = createApp()
#app.secret_key = os.getenv('FLASK_SECRET_KEY', '3729fusnjcjwhafuJKAJFadkfj@74920akdj&hejahreu2hakjdc') # fill in when you test, but dont push to public repo

# Initialize Firebase Admin SDK

if __name__ == "__main__":
    app.run(debug=True)