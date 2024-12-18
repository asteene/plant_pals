from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

from flaskr.config import Config

import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
# import json
from firebase_admin import firestore, storage

cred = credentials.Certificate("flaskr/secrets/secrets.json")  
firebase_admin.initialize_app(cred, {
    'storageBucket': 'gs://plantpals-dab2c.appspot.com'  # Replace with your actual bucket name
})
db = firestore.client()
bucket = storage.bucket()

def createApp(config_class=Config):
    '''  
    App Factory for Plant Pals Application
    '''

    app = Flask(__name__)
    app.config.from_object(Config)
    
    # from flaskr.main.routes import main
    from flaskr.main.routes import main, get_friends

    app.jinja_env.globals['get_friends'] = get_friends


    app.register_blueprint(main)

    return app
