from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SelectField
from flask_wtf.csrf import CSRFProtect
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError

csrf = CSRFProtect()

class Registration(FlaskForm):
  username = StringField(label="Username", validators=[DataRequired()])
  account = SelectField(label="Account Type", choices=["Seller", "Buyer"], validators=[DataRequired()])
  password = PasswordField(label="Password", validators=[Length(min=5, message="Password must be more than 5 characters"), DataRequired()])
  password1 = PasswordField(label="Confirm Password", validators=[EqualTo("password", message="Passwords do not match"), DataRequired()])

class Login(FlaskForm):
  email_address = StringField(label="Email Address", validators=[DataRequired()])
  password = PasswordField(label="Password", validators=[DataRequired()])
