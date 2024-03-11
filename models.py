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
  user = db.relationship("Users", backref="user_role", lazy=True)

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
  booking = db.relationship("Bookings", backref="bookings_owner", lazy=True)
  event = db.relationship("Event", backref="event_owner", lazy=True)

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
  description = db.Column(db.String(1000))
  start_date = db.Column(db.Date(), nullable=False)
  end_date = db.Column(db.Date(), nullable=False)
  start_time = db.Column(db.Time(), nullable=False)
  end_time = db.Column(db.Time(), nullable=False)
  location = db.Column(db.String(50), nullable=False)
  tickets = db.Column(db.Integer(), nullable=False, default=0)
  user = db.Column(db.Integer(), db.ForeignKey("Users.id"))
  is_active = db.Column(db.Boolean(), default=True)
  is_soldout = db.Column(db.Boolean(), default=False)
  is_ended = db.Column(db.Boolean(), default=False)
  booking = db.relationship("Bookings", backref="booking_owners", lazy=True)
  qrcode = db.relationship("Qrcodes", backref="qrcode_event", lazy=True)
  pricing = db.relationship("Pricing", backref="event_price", lazy=True)

class Pricing(db.Model):
  __tablename__ = "Pricing"
  id = db.Column(db.Integer(), primary_key=True)
  name = db.Column(db.String(50), nullable=False, default="Regular")
  amount = db.Column(db.Integer(), nullable=False, default=0)
  event = db.Column(db.Integer(), db.ForeignKey("event.id"))
  booking = db.relationship("Bookings", backref="booking_ticket", lazy=True)

class Bookings(db.Model):
  __tablename__ = "Bookings"
  id = db.Column(db.Integer(), primary_key=True)
  unique_id = db.Column(db.Integer(), nullable=False, default=random.randint(100000,999999))
  user = db.Column(db.Integer(), db.ForeignKey("Users.id"))
  event = db.Column(db.Integer(), db.ForeignKey("event.id"))
  tickets = db.Column(db.Integer(), nullable=False)
  ticket = db.Column(db.Integer(), db.ForeignKey("Pricing.id"))
  total = db.Column(db.Integer(), default=0)
  status = db.Column(db.String(10), nullable=False, default="Pending")
  qrcode = db.relationship("Qrcodes", backref="qrcode_booking", lazy=True)

class Qrcodes(db.Model):
  __tablename__ = "qrcodes"
  id = db.Column(db.Integer(), primary_key=True)
  unique_id = db.Column(db.Integer(), nullable=False)
  bucket = db.Column(db.String(100))
  region = db.Column(db.String(100))
  booking = db.Column(db.Integer(), db.ForeignKey('Bookings.id'))
  event = db.Column(db.Integer(), db.ForeignKey("event.id"))
  status = db.Column(db.String(10), default="Active")
