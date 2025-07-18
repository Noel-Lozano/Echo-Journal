from app import db

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    text = db.Column(db.Text, nullable=True)
    date_joined = db.Column(db.DateTime, nullable=False)
    photo = db.Column(db.String(255), nullable=True, default=None)  # URL or path to photo
    preferences = db.Column(db.JSON, nullable=True, default=None)  # Store tags/groups as JSON
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    user = db.relationship('User', back_populates='profile')
