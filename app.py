from flask import Flask, render_template, flash, redirect, url_for, request
from flask_login import login_manager, LoginManager, login_user, logout_user, current_user, login_required
from models import * 
from form import *
from datetime import datetime, date
import qrcode, io, os, shutil

app = Flask(__name__)
app.config["SECRET_KEY"] = "fvjdnjkdsnsnd"
app.config["SQLALCHEMY_DATABASE_URI"] = "mssql+pyodbc://KEVINKAGWIMA/tickets?driver=ODBC+Driver+11+for+SQL+Server"
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://kevokagwima:Hunter1234@kevokagwima.mysql.pythonanywhere-services.com/kevokagwima$tickets"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
UPLOAD_FOLDER = 'static/images/Qr_codes'
UPLOAD_FOLDER = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
login_manager = LoginManager()
login_manager.login_view = '/login'
login_manager.login_message = "Please login to access this page"
login_manager.login_message_category = "danger"
login_manager.init_app(app)

if not os.path.exists(UPLOAD_FOLDER):
  os.makedirs(UPLOAD_FOLDER)

@login_manager.user_loader
def load_user(user_id):
  try:
    return Users.query.filter_by(unique_id=user_id).first()
  except:
    flash("Failed to login the user", category="danger")

@app.before_request
def event_expiry():
  all_events = Event.query.filter_by(status="Active").all()
  for event in all_events:
    today = date.today()
    current_time = datetime.now()
    if event.end_date < today or (event.end_date == today and event.end_time.strftime("%H:%M") < current_time.strftime("%H:%M")):
      event.status = "Ended"
      db.session.commit()
  return None

@app.route("/register", methods=["POST", "GET"])
def register():
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
      return redirect(url_for('login'))
    
    if form.errors != {}:
      for err_msg in form.errors.values():
        flash(f"{err_msg}", category="danger")

  return render_template("register.html", form=form)

@app.route("/login", methods=["POST", "GET"])
def login():
  form = LoginForm()
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
  today = date.today()
  current_time = datetime.now()
  return render_template("index.html", events=events, roles=roles, today=today, current_time=current_time)

@app.route("/create-event", methods=["POST", "GET"])
@login_required
def create_event():
  form = EventCreationForm()
  roles = Role.query.all()
  if form.validate_on_submit():
    event = Event.query.filter_by(name=form.name.data, status="Active").first()
    todays_date = date.today()
    start_date = form.start_date.data
    end_date = form.end_date.data
    if str(start_date) < str(todays_date):
      flash("Start date cannot be before current date", category="danger")
      return redirect(url_for('create_event'))
    elif event:
      flash("An event with that name already exists and it's ongoing", category="danger")
      return redirect(url_for('create_event'))
    elif end_date < start_date:
      flash("End Date cannot be before start date", category="danger")
      return redirect(url_for('create_event'))
    else:
      new_event = Event(
        name = form.name.data,
        tagline = form.tagline.data,
        description = form.description.data,
        start_date = start_date,
        end_date = end_date,
        start_time = form.start_time.data,
        end_time = form.end_time.data,
        price = form.price.data,
        location = form.location.data,
        tickets = form.no_of_tickets.data,
        user = current_user.id
      )
      db.session.add(new_event)
      db.session.commit()
      generate_qrcode(new_event.id, new_event.tickets)
      flash(f"Event '{new_event.name}' created successfully", category="success")
      return redirect(url_for('home'))
  return render_template("event.html", roles=roles, form=form)

def allowed_file(filename):
  return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_qrcode(event_id, tickets):
  event = Event.query.get(event_id)
  for i in range(tickets):
    new_qrcode = Qrcodes(
      event = event_id,
      unique_id = random.randint(100000000,999999999)
    )
    db.session.add(new_qrcode)
    qrcode_name = f'{event.name}-{new_qrcode.unique_id}'
    new_qrcode.qrcode = qrcode_name
    db.session.commit()
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.make(fit=True)
    qr.add_data(qrcode_name)
    folder = f"{event.name}"
    if not os.path.exists(folder):
      os.makedirs(folder)
    filename = os.path.join(folder, f'{qrcode_name}.png')
    img = qr.make_image(fill_color='black', back_color='white')
    img.save(filename)
  shutil.move(folder, UPLOAD_FOLDER)

@app.route("/edit-event/<int:event_id>", methods=["POST", "GET"])
@login_required
def edit_event(event_id):
  form = EditEventForm()
  roles = Role.query.all()
  # try:
  event = Event.query.filter_by(unique_id=event_id).first()
  if form.validate_on_submit():
    todays_date = date.today()
    start_date = form.start_date.data
    end_date = form.end_date.data
    if str(start_date) < str(event.start_date):
      flash("Start date cannot be before current date", category="danger")
      return redirect(url_for('edit_event', event_id=event.id))
    elif end_date < start_date:
      flash("End Date cannot be before start date", category="danger")
      return redirect(url_for('edit_event', event_id=event.id))
    else:
      event.name = form.name.data,
      event.tagline = form.tagline.data,
      event.start_date = form.start_date.data,
      event.end_date = form.end_date.data,
      event.start_time = form.start_time.data,
      event.end_time = form.end_time.data,
      event.price = form.price.data,
      event.location = form.location.data,
      event.tickets = form.no_of_tickets.data,
      event.user = current_user.id
      db.session.commit()
      flash(f"Event '{event.name}' updated successfully", category="success")
      return redirect(url_for('home'))
  return render_template("edit_event.html", roles=roles, form=form, event=event)
  # except:
  #   flash("Event not found", category="danger")
  # return redirect(url_for('home'))

@app.route("/delete-event/<int:event_id>")
@login_required
def delete_event(event_id):
  try:
    event = Event.query.filter_by(unique_id=event_id).first()
    qrcodes = Qrcodes.query.filter_by(event=event.id).all()
    for qrcode in qrcodes:
      db.session.delete(qrcode)
    db.session.delete(event)
    db.session.commit()
    flash(f"Event {event.name} has been removed successfully", category="success")
  except:
    flash("An error occured", category="danger")
  return redirect(url_for('home'))

@app.route("/tickets/<int:event_id>", methods=["POST", "GET"])
def tickets(event_id):
  event = Event.query.get(event_id)
  roles = Role.query.all()
  if event:
    if request.method == "POST":
      if current_user.is_authenticated:
        new_booking = Bookings(
          user = current_user.id,
          event = event.id,
          tickets = request.form.get("tickets")
        )
        db.session.add(new_booking)
        event.tickets = event.tickets - int(new_booking.tickets)
        db.session.commit()
        flash("Your tickets are ready", category="success")
        return redirect(url_for('home'))
      else:
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
        event.tickets = event.tickets - new_booking.tickets
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
