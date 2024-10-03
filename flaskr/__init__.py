from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

from flaskr.config import Config

import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
# import json
from firebase_admin import firestore

db = None
login_manager = LoginManager()
login_manager.login_view = 'main.login'
bcrypt = Bcrypt()

def createApp(config_class=Config):
    '''  
    App Factory for Plant Pals Application
    '''

    app = Flask(__name__)
    app.config.from_object(Config)

   
    cred = credentials.Certificate("secrets/secrets.json")  
    firebase_admin.initialize_app(cred)

    db = firestore.client()
    login_manager.init_app(app)
    bcrypt.init_app(app)

    from flaskr.main.routes import main

    app.register_blueprint(main)

    return app

