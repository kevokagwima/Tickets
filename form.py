from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SelectField, DateField, TimeField, TextAreaField, EmailField
from flask_wtf.csrf import CSRFProtect
from wtforms.validators import Length, EqualTo, DataRequired, ValidationError
from models import Users

csrf = CSRFProtect()

class RegistrationForm(FlaskForm):
  first_name = StringField(label="First Name", validators=[DataRequired(message="First Name field is required")])
  surname = StringField(label="Surname", validators=[DataRequired(message="Surname field is required")])
  phone_number = EmailField(label="Phone Number", validators=[Length(min=10, max=10, message="Invalid Phone Number"), DataRequired(message="Phone Number field is required")])
  email_address = StringField(label="Email Address", validators=[DataRequired(message="Email Address field is required")])
  account = SelectField(label="Account Type", choices=[], validators=[DataRequired(message="Account type field is required")])
  password = PasswordField(label="Password", validators=[Length(min=5, message="Password must be more than 5 characters"), DataRequired(message="Password field is required")])
  password1 = PasswordField(label="Confirm Password", validators=[EqualTo("password", message="Passwords do not match"), DataRequired(message="Confirm password field is required")])

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
  email_address = EmailField(label="Email Address", validators=[DataRequired(message="Email Address field is required")])
  password = PasswordField(label="Password", validators=[DataRequired(message="Password field is required")])

class EventForm(FlaskForm):
  name = StringField(label="Event Name",validators=[DataRequired(message="Event name field is required")])
  tagline = StringField(label="Event Tagline")
  description = TextAreaField(label="Event Description",validators=[Length(max=1000)])
  start_date = DateField(label="Start Date", validators=[DataRequired(message="Start Date field is required")])
  end_date = DateField(label="End Date", validators=[DataRequired(message="End Date field is required")])
  start_time = TimeField(label="Start Time", validators=[DataRequired(message="Start Time field is required")])
  end_time = TimeField(label="End Time", validators=[DataRequired(message="End Time field is required")])
  location = StringField(label="Event Location",validators=[DataRequired(message="Event location field is required")])
  no_of_tickets = IntegerField(label="Available Tickets",validators=[DataRequired(message="No of tickets field is required")])

class PricingForm(FlaskForm):
  name = StringField(label="Name",validators=[DataRequired(message="Name field is required")])
  price = IntegerField(label="Ticket Price",validators=[DataRequired(message="Event price field is required")])

class TicketForm(FlaskForm):
  first_name = StringField(label="First Name",validators=[DataRequired(message="First Name field required")])
  last_name = StringField(label="Last Name",validators=[DataRequired(message="Last Name field required")])
  email = EmailField(label="Email Address",validators=[DataRequired(message="Email Address field required")])
  phone_number = StringField(label="Phone Number",validators=[Length(min=10, max=10), DataRequired(message="Phone Number field required")])
  ticket = SelectField(label="Ticket Type", choices=[], validators=[DataRequired(message="Ticket type field is required")])
  tickets = IntegerField(label="Tickets",validators=[DataRequired(message="Tickets field required")])
