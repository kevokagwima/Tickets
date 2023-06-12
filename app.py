from flask import Flask, render_template, flash, redirect, url_for, request
from flask_login import login_manager, LoginManager, login_user, logout_user, current_user
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
login_manager.login_view = '/register' 
login_manager.login_message_category = "danger"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
  pass

@app.route("/register")
def register():
  form = Registration()
  return render_template("register.html", form=form)

@app.route("/")
@app.route("/home")
def home():
  events = Event.query.all()
  return render_template("index.html", events=events)

@app.route("/create-event", methods=["POST", "GET"])
def create_event():
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
        tickets = request.form.get("tickets"),
      )
      db.session.add(new_event)
      db.session.commit()
      flash(f"Event '{new_event.name}' created successfully", category="success")
      return redirect(url_for('home'))
  return render_template("event.html")

@app.route("/tickets/<int:event_id>", methods=["POST", "GET"])
def tickets(event_id):
  event = Event.query.get(event_id)
  if event:
    if request.method == "POST":
      new_user = Users(
        first_name = request.form.get("fname"),
        surname = request.form.get("sname"),
        email = request.form.get("email"),
        phone = request.form.get("phone"),
        tickets = request.form.get("tickets"),
      )
      db.session.add(new_user)
      db.session.commit()
      flash("Tickets saved successfully", category="success")
  else:
    flash("Event could not be found", category="danger")
    return redirect(url_for('home'))
  return render_template("book.html", event=event)

if __name__ == "__main__":
  app.run(debug=True)
