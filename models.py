from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
import random

db = SQLAlchemy()
bcrypt = Bcrypt()

class Role(db.Model):
  __tablename__ = "Roles"
  id = db.Column(db.Integer(), primary_key=True)
  role_name = db.Column(db.String(10), nullable=False)
  seller = db.relationship("Seller", backref="seller-role", lazy=True)
  buyer = db.relationship("Buyer", backref="buyer-role", lazy=True)

class Seller(db.Model, UserMixin):
  __tablename__ = "Seller"
  id = db.Column(db.Integer(), primary_key=True)
  unique_id = db.Column(db.Integer(), nullable=False, default=random.randint(100000,999999))
  username = db.Column(db.String(30), nullable=False)
  password = db.Column(db.String(30), nullable=False, default="11111")
  role = db.Column(db.Integer(), db.ForeignKey('Roles.id'))

class Buyer(db.Model, UserMixin):
  __tablename__ = "Buyer"
  id = db.Column(db.Integer(), primary_key=True)
  unique_id = db.Column(db.Integer(), nullable=False, default=random.randint(100000,999999))
  username = db.Column(db.String(30), nullable=False)
  password = db.Column(db.String(30), nullable=False, default="11111")
  role = db.Column(db.Integer(), db.ForeignKey('Roles.id'))
