from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required
from form import *
from models import *

auth = Blueprint("auth", __name__)

@auth.route("/signup", methods=["POST", "GET"])
def signup():
  form = RegistrationForm()
  form.account.choices = [(role.id, role.role_name) for role in Role.query.all()]
  if request.method == "POST":
    if form.validate_on_submit():
      new_user = Users(
        first_name = form.first_name.data,
        surname = form.surname.data,
        email = form.email_address.data,
        phone = form.phone_number.data,
        passwords = form.password.data,
        role = form.account.data
      )
      db.session.add(new_user)
      db.session.commit()
      flash("Registration successfull", category="success")
      return redirect(url_for('auth.signin'))
    
    if form.errors != {}:
      for err_msg in form.errors.values():
        flash(f"{err_msg}", category="danger")

  return render_template("signup.html", form=form)

@auth.route("/signin", methods=["POST", "GET"])
def signin():
  form = LoginForm()
  if request.method == "POST" and form.validate_on_submit():
    user = Users.query.filter_by(email=form.email_address.data).first()
    if user and user.check_password_correction(attempted_password=form.password.data):
      login_user(user, remember=True)
      flash("Login successfull", category="success")
      return redirect(url_for("users.home"))
    elif user is None:
      flash("No user with that email", category="danger")
      return redirect(url_for('auth.signin'))
    else:
      flash("Invalid credentials", category="danger")
      return redirect(url_for('auth.signin'))

  if form.errors != {}:
    for err_msg in form.errors.values():
      flash(f"{err_msg}", category="danger")

  return render_template("signin.html", form=form)

@auth.route("/logout")
@login_required
def logout():
  logout_user()
  flash("Logout successfull", category="success")
  return redirect(url_for('auth.signin'))
