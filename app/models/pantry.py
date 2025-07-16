from app import db

class Pantry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(255))
    eco_score = db.Column(db.String(10))
    score = db.Column(db.String(10))
    pros = db.Column(db.String(500))
    cons = db.Column(db.String(500))
