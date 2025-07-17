import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from .routes.search import search_bp
    app.register_blueprint(search_bp)

    from .routes.pantry_display import pantry_bp
    app.register_blueprint(pantry_bp)

    with app.app_context():
        db.create_all()
    
    # PLEASE NOTE: This is a development secret key.
    # In production, you should set a strong secret key in your environment variables.
    
    app.secret_key = "dev"
    print("WARNING: Using a weak secret key.")

    return app
