from flask import Flask, render_template, flash, redirect, url_for, request
from flask_login import login_manager, LoginManager, login_user, logout_user, current_user, login_required
from models import * 
from form import *
from datetime import datetime, date

app = Flask(__name__)
app.config["SECRET_KEY"] = "fvjdnjkdsnsnd"
app.config["SQLALCHEMY_DATABASE_URI"] = "mssql+pyodbc://KEVINKAGWIMA/tickets?driver=ODBC+Driver+11+for+SQL+Server"
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://kevokagwima:Hunter1234@kevokagwima.mysql.pythonanywhere-services.com/kevokagwima$tickets"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = '/login'
login_manager.login_message = "Please login to access this page"
login_manager.login_message_category = "danger"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
  try:
    return Users.query.filter_by(unique_id=user_id).first()
  except:
    flash("Failed to login the user", category="danger")

# @app.before_request
# def before_request():
#   flash("Before request", category="success")
#   return None

@app.route("/register", methods=["POST", "GET"])
def register():
  form = Registration()
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
      return redirect(url_for('login'))
    
    if form.errors != {}:
      for err_msg in form.errors.values():
        flash(f"{err_msg}", category="danger")

  return render_template("register.html", form=form)

@app.route("/login", methods=["POST", "GET"])
def login():
  form = Login()
  if request.method == "POST":
    if form.validate_on_submit():
      user = Users.query.filter_by(email=form.email_address.data).first()
      if user and user.check_password_correction(attempted_password=form.password.data):
        login_user(user, remember=True)
        flash("Login successfull", category="success")
        return redirect(url_for("home"))
      elif user is None:
        flash("No user with that email", category="danger")
        return redirect(url_for('login'))
      else:
        flash("Invalid credentials", category="danger")
        return redirect(url_for('login'))
  return render_template("login.html", form=form)

@app.route("/")
@app.route("/home")
@login_required
def home():
  events = Event.query.all()
  roles = Role.query.all()
  return render_template("index.html", events=events, roles=roles)

@app.route("/create-event", methods=["POST", "GET"])
@login_required
def create_event():
  roles = Role.query.all()
  if request.method == "POST":
    todays_date = date.today()
    event_date = request.form.get("event-date")
    if event_date < str(todays_date):
      flash("Invalid event date", category="danger")
      return redirect(url_for('create_event'))
    else:
      new_event = Event(
        name = request.form.get("event-name"),
        date = event_date,
        time = request.form.get("event-time"),
        price = request.form.get("price"),
        location = request.form.get("location"),
        tickets = request.form.get("tickets"),
      )
      db.session.add(new_event)
      db.session.commit()
      flash(f"Event '{new_event.name}' created successfully", category="success")
      return redirect(url_for('home'))
  return render_template("event.html", roles=roles)

@app.route("/tickets/<int:event_id>", methods=["POST", "GET"])
def tickets(event_id):
  event = Event.query.get(event_id)
  roles = Role.query.all()
  if event:
    if request.method == "POST":
      users_phone = request.form.get("phone")
      existing_user = Users.query.filter_by(phone=users_phone).first()
      if existing_user is None:
        new_user = Users(
          first_name = request.form.get("fname"),
          surname = request.form.get("sname"),
          email = request.form.get("email"),
          phone = request.form.get("phone"),
        )
        db.session.add(new_user)
        db.session.commit()
        new_booking = Bookings(
          user = new_user.id,
          event = event.id,
          tickets = request.form.get("tickets")
        )
        db.session.add(new_booking)
        db.session.commit()
        flash("Your tickets are ready", category="success")
        return redirect(url_for('home'))
  else:
    flash("Event could not be found", category="danger")
    return redirect(url_for('home'))
  return render_template("book.html", event=event, roles=roles)

@app.route("/logout")
@login_required
def logout():
  logout_user()
  flash("Logout successfull", category="success")
  return redirect(url_for('login'))

if __name__ == "__main__":
  app.run(debug=True)
