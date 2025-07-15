import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.google import make_google_blueprint, google
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

    db.init_app(app)

    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # Google OAuth Blueprint
    google_bp = make_google_blueprint(
        client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
        redirect_url="/login/google/authorized",
        scope=["profile", "email"]
    )
    app.register_blueprint(google_bp, url_prefix="/login")

    with app.app_context():
        db.create_all()

    return app
