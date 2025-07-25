from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='new')
    is_verified = db.Column(db.Boolean, default=False)
    subscription_active = db.Column(db.Boolean, default=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    cards = db.relationship('BusinessCard', backref='user', lazy=True)

    def __init__(self, name, email, password, role='new'):
        self.name = name
        self.email = email
        self.password = password
        self.role = role

class BusinessCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    company = db.Column(db.String(100))
    mobile = db.Column(db.String(20))
    email = db.Column(db.String(100))
    logo = db.Column(db.String(255))
    pdf = db.Column(db.String(255))
    qr = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, user_id, name, designation, company, mobile, email, logo=None, pdf=None, qr=None):
        self.user_id = user_id
        self.name = name
        self.designation = designation
        self.company = company
        self.mobile = mobile
        self.email = email
        self.logo = logo
        self.pdf = pdf
        self.qr = qr
