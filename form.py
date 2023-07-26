from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SelectField, DateField, TimeField
from flask_wtf.csrf import CSRFProtect
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from models import Users, Role

csrf = CSRFProtect()

class RegistrationForm(FlaskForm):
  first_name = StringField(label="First Name", validators=[DataRequired()])
  surname = StringField(label="Surname", validators=[DataRequired()])
  phone_number = StringField(label="Phone Number", validators=[Length(min=10, max=10, message="Invalid Phone Number"), DataRequired()])
  email_address = StringField(label="Email Address", validators=[DataRequired()])
  account = SelectField(label="Account Type", choices=[], validators=[DataRequired()])
  password = PasswordField(label="Password", validators=[Length(min=5, message="Password must be more than 5 characters"), DataRequired()])
  password1 = PasswordField(label="Confirm Password", validators=[EqualTo("password", message="Passwords do not match"), DataRequired()])

  def validate_phone_number(self, phone_number_to_validate):
    phone_number = Users.query.filter_by(phone=phone_number_to_validate.data).first()
    if phone_number:
      raise ValidationError("Phone Number already exists, Please try another one")

  def validate_phone_number(self, phone_number_to_validate):
    phone_number = phone_number_to_validate.data
    if phone_number[0] != str(0):
      raise ValidationError("Invalid phone number. Phone number must begin with 0")
    elif phone_number[1] != str(7) and phone_number[1] != str(1):
      raise ValidationError("Invalid phone number. Phone number must begin with 0 followed by 7 or 1")

  def validate_email_address(self, email_to_validate):
    email = Users.query.filter_by(email=email_to_validate.data).first()
    if email:
      raise ValidationError("Email Address already exists, Please try another one")

class LoginForm(FlaskForm):
  email_address = StringField(label="Email Address", validators=[DataRequired()])
  password = PasswordField(label="Password", validators=[DataRequired()])

class EventCreationForm(FlaskForm):
  name = StringField(label="Event Name",validators=[DataRequired()])
  tagline = StringField(label="Event Tagline",validators=[DataRequired()])
  start_date = DateField(label="Start Date", validators=[DataRequired()])
  end_date = DateField(label="End Date", validators=[DataRequired()])
  start_time = TimeField(label="Start Time", validators=[DataRequired()])
  end_time = TimeField(label="End Time", validators=[DataRequired()])
  location = StringField(label="Event Location",validators=[DataRequired()])
  price = IntegerField(label="Ticket Price",validators=[DataRequired()])
  no_of_tickets = IntegerField(label="Available Tickets",validators=[DataRequired()])

class EditEventForm(FlaskForm):
  name = StringField(label="Event Name",validators=[DataRequired()])
  tagline = StringField(label="Event Tagline",validators=[DataRequired()])
  start_date = DateField(label="Start Date", validators=[DataRequired()])
  end_date = DateField(label="End Date", validators=[DataRequired()])
  start_time = TimeField(label="Start Time", validators=[DataRequired()])
  end_time = TimeField(label="End Time", validators=[DataRequired()])
  location = StringField(label="Event Location",validators=[DataRequired()])
  price = IntegerField(label="Ticket Price",validators=[DataRequired()])
  no_of_tickets = IntegerField(label="Available Tickets",validators=[DataRequired()])