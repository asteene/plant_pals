from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

from flaskr.config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
bcrypt = Bcrypt()

def createApp(config_class=Config):
    '''  
    App Factory for Plant Pals Application
    '''

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    from flaskr.main.routes import main

    app.register_blueprint(main)

    return app

