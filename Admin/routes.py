from flask import Blueprint, flash, redirect, render_template, url_for, request
from flask_login import login_required, current_user
from models import *
from form import *
from datetime import date
from io import BytesIO
import qrcode, boto3, os

admin = Blueprint("admin", __name__)
s3 = boto3.resource(
  "s3",
  aws_access_key_id = os.environ.get("AWS_ACCESS_KEY"),
  aws_secret_access_key = os.environ.get("AWS_SECRET_KEY")
)
client = boto3.client(
  "s3",
  aws_access_key_id = os.environ.get("AWS_ACCESS_KEY"),
  aws_secret_access_key = os.environ.get("AWS_SECRET_KEY")
)
bucket_name = os.environ.get("BUCKET_NAME")
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

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
        location = form.location.data,
        tickets = form.no_of_tickets.data,
        user = current_user.id
      )
      db.session.add(new_event)
      db.session.commit()
      generate_qrcode(event.id, new_event.tickets)
      flash(f"Event '{new_event.name}' created successfully", category="success")
      return redirect(url_for('admin.pricing', event_id=new_event.id))
  return render_template("create_event.html", form=form)

@admin.route("/pricing/<int:event_id>", methods=["POST", "GET"])
def pricing(event_id):
  try:
    event = Event.query.get(event_id)
    pricing = Pricing.query.filter_by(event=event.id).all()
    form = PricingForm()
    if request.method == "POST":
      if form.validate_on_submit():
        new_pricing = Pricing(
          name = form.name.data,
          amount = form.price.data,
          event = event.id
        )
        db.session.add(new_pricing)
        db.session.commit()
        flash(f"Ticket added for {event.name}", category="success")
        return redirect(url_for('admin.pricing', event_id=event.id))
    return render_template("pricing.html", event=event, form=form, pricing=pricing)
  except:
    flash("An error occurred", category="danger")
    return redirect(url_for('users.home'))

@admin.route("/remove-pricing/<int:event_id>/<int:pricing_id>")
def remove_pricing(event_id, pricing_id):
  try:
    event = Event.query.get(event_id)
    if event:
      pricing = Pricing.query.get(pricing_id)
      if pricing:
        db.session.delete(pricing)
        db.session.commit()
        flash("Ticket removed successfully", category="success")
        return redirect(url_for('admin.pricing', event_id=event.id))
    else:
      flash("Event not found", category="danger")
      return redirect(url_for('admin.pricing', event_id=event.id))
  except:
    flash("An error occurred", category="danger")
    return redirect(url_for('users.home'))

def generate_qrcode(event_id, tickets):
  event = Event.query.get(event_id)
  if event:
    folder_name = event.name
    for i in range(tickets):
      new_qrcode = Qrcodes(
        event = event_id,
        unique_id = random.randint(100000000,999999999),
        bucket = bucket_name,
        region = os.environ.get("REGION")
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

@admin.route("/edit-event/<int:event_id>", methods=["POST", "GET"])
@login_required
def edit_event(event_id):
  event = Event.query.filter_by(unique_id=event_id).first()
  if event:
    form = EventForm()
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
        event.tickets = form.no_of_tickets.data
        db.session.commit()
        flash(f"Event {event.name} updated successfully", category="success")
        return redirect(url_for('users.home'))
      
      if form.errors != {}:
        for err_msg in form.errors.values():
          flash(f"{err_msg}", category="danger")
  else:
    flash("Event not found", category="danger")
    return redirect(url_for('users.home'))
  return render_template("edit_event.html", event=event, form=form)

@admin.route("/delete-event/<int:event_id>")
@login_required
def delete_event(event_id):
  try:
    event = Event.query.filter_by(unique_id=event_id).first()
    qrcodes = Qrcodes.query.filter_by(event=event.id).all()
    pricing = Pricing.query.filter_by(event=event.id).all()
    bookings = Bookings.query.filter_by(event=event.id).all()
    for qrcode in qrcodes:
      db.session.delete(qrcode)
    for ticket in pricing:
      db.session.delete(ticket)
    for booking in bookings:
      db.session.delete(booking)
    db.session.delete(event)
    db.session.commit()
    flash(f"Event {event.name} has been removed successfully", category="success")
  except:
    flash("An error occured", category="danger")
  return redirect(url_for('users.home'))
