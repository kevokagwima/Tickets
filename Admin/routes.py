from flask import Blueprint, flash, redirect, render_template, url_for, request
from flask_login import login_required, current_user
from models import *
from form import *
from datetime import date, datetime
from io import BytesIO
import qrcode, boto3

admin = Blueprint("admin", __name__)
s3 = boto3.resource(
  "s3",
  aws_access_key_id = "AKIAW3MEB6Z756PC7WX4",
  aws_secret_access_key = "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"
)
client = boto3.client(
  "s3",
  aws_access_key_id = "AKIAW3MEB6Z756PC7WX4",
  aws_secret_access_key = "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"
)
bucket_name = "soundsoffreedom"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

@admin.before_request
def event_expiry():
  all_events = Event.query.filter_by(status="Active").all()
  for event in all_events:
    today = date.today()
    current_time = datetime.now()
    if event.end_date < today or (event.end_date == today and event.end_time.strftime("%H:%M") < current_time.strftime("%H:%M")):
      event.status = "Ended"
      qrcodes = Qrcodes.query.filter_by(event=event.id).all()
      for qrcode in qrcodes:
        qrcode.status = "Closed"
        db.session.commit()
    if event.tickets <= 0:
      event.status = "Sold Out"
    db.session.commit()
  return None

@admin.route("/create-event", methods=["POST", "GET"])
@login_required
def create_event():
  form = EventForm()
  if form.validate_on_submit():
    event = Event.query.filter_by(name=form.name.data, status="Active").first()
    todays_date = date.today()
    start_date = form.start_date.data
    end_date = form.end_date.data
    if str(start_date) < str(todays_date):
      flash("Start date cannot be before current date", category="danger")
      return redirect(url_for('admin.create_event'))
    elif event:
      flash("An event with that name already exists and it's ongoing", category="danger")
      return redirect(url_for('admin.create_event'))
    elif end_date < start_date:
      flash("End Date cannot be before start date", category="danger")
      return redirect(url_for('admin.create_event'))
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
      return redirect(url_for('users.home'))
  return render_template("create_event.html", form=form)

def generate_qrcode(event_id, tickets):
  event = Event.query.get(event_id)
  if event:
    folder_name = event.name
    for i in range(tickets):
      new_qrcode = Qrcodes(
        event = event_id,
        unique_id = random.randint(100000000,999999999),
        bucket = bucket_name,
        region = "eu-north-1"
      )
      db.session.add(new_qrcode)
      db.session.commit()
      qr = qrcode.QRCode(version=1, box_size=10, border=4)
      qr.make(fit=True)
      qr.add_data(new_qrcode.unique_id)
      img_buffer = BytesIO()
      qr.make_image(fill_color="black", back_color="white").save(img_buffer)
      img_buffer.seek(0)
      image_name = f"{folder_name}/" + str(new_qrcode.unique_id) + '.png'
      s3.Bucket(bucket_name).upload_fileobj(img_buffer, image_name)

@admin.route("/event-details/<int:event_id>")
def event_details(event_id):
  try:
    event = Event.query.get(event_id)
    if event:
      return render_template("event.html", event=event)
    else:
      flash("Event not found", category="danger")
      return redirect(url_for('users.home'))
  except:
    flash("An error ocurred", category="danger")
    return redirect(url_for('users.home'))

@admin.route("/edit-event/<int:event_id>", methods=["POST", "GET"])
@login_required
def edit_event(event_id):
  event = Event.query.filter_by(unique_id=event_id).first()
  form = EventForm()
  form.description.data = event.description
  form.start_time.data = event.start_time
  form.end_time.data = event.end_time
  if request.method == "POST":
    if form.validate_on_submit():
      today_date = date.today()
      if form.start_date.data != event.start_date or form.start_date.data > event.start_date or form.end_date.data < today_date or form.end_date.data < event.start_date:
        if form.start_date.data < today_date or form.end_date.data < today_date or form.end_date.data < event.start_date:
          flash("Invalid date", category="danger")
          return redirect(url_for('admin.edit_event', event_id=event.unique_id))
      event.name = form.name.data
      event.tagline = form.tagline.data
      event.description = form.description.data
      event.start_date = form.start_date.data
      if form.start_date.data > form.end_date.data:
        event.end_date = form.start_date.data
      else:
        event.end_date = form.end_date.data
      event.start_time = form.start_time.data
      event.end_time = form.end_time.data
      event.location = form.location.data
      event.price = form.price.data
      event.tickets = form.no_of_tickets.data
      db.session.commit()
      flash(f"Event {event.name} updated successfully", category="success")
      return redirect(url_for('users.home'))
    
    if form.errors != {}:
      for err_msg in form.errors.values():
        flash(f"{err_msg}", category="danger")

  return render_template("edit_event.html", event=event, form=form)

@admin.route("/delete-event/<int:event_id>")
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
  return redirect(url_for('users.home'))