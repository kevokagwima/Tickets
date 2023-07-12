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
  user = db.relationship("Users", backref="user-role", lazy=True)

class Users(db.Model, UserMixin):
  __tablename__ = "Users"
  id = db.Column(db.Integer(), primary_key=True)
  unique_id = db.Column(db.Integer(), nullable=False, default=random.randint(100000,999999))
  first_name = db.Column(db.String(50), nullable=False)
  surname = db.Column(db.String(50), nullable=False)
  email = db.Column(db.String(100), nullable=False)
  phone = db.Column(db.String(10), nullable=False)
  password = db.Column(db.String(100), nullable=False, default="11111")
  role = db.Column(db.Integer(), db.ForeignKey('Roles.id'))
  event = db.relationship("Event", backref="event-owner", lazy=True)

  @property
  def passwords(self):
    return self.passwords

  @passwords.setter
  def passwords(self, plain_text_password):
    self.password = bcrypt.generate_password_hash(plain_text_password).decode("utf-8")

  def check_password_correction(self, attempted_password):
    return bcrypt.check_password_hash(self.password, attempted_password)

class Event(db.Model):
  __tablename__ = "event"
  id = db.Column(db.Integer(), primary_key=True)
  unique_id = db.Column(db.Integer(), nullable=False, default=random.randint(100000,999999))
  name = db.Column(db.String(100), nullable=False)
  tagline = db.Column(db.String(100))
  start_date = db.Column(db.Date(), nullable=False)
  end_date = db.Column(db.Date(), nullable=False)
  start_time = db.Column(db.Time(), nullable=False)
  end_time = db.Column(db.Time(), nullable=False)
  location = db.Column(db.String(50), nullable=False)
  tickets = db.Column(db.Integer(), nullable=False, default=100)
  price = db.Column(db.Integer(), nullable=False, default=0)
  status = db.Column(db.String(10), nullable=False, default="Active")
  user = db.Column(db.Integer(), db.ForeignKey('Users.id'))

class Bookings(db.Model):
  __tablename__ = "Bookings"
  id = db.Column(db.Integer(), primary_key=True)
  unique_id = db.Column(db.Integer(), nullable=False, default=random.randint(100000,999999))
  user = db.Column(db.Integer(), db.ForeignKey("Users.id"))
  event = db.Column(db.Integer(), db.ForeignKey("event.id"))
  tickets = db.Column(db.Integer(), nullable=False)
  status = db.Column(db.String(10), nullable=False, default="Pending")
