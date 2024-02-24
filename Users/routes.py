from flask import Blueprint, flash, redirect, render_template, url_for, request
from flask_login import login_required, current_user
from models import *
from form import *
from datetime import datetime, date
from modules import send_email
import stripe, os

users = Blueprint("users", __name__)
stripe.api_key = os.environ['Stripe_api_key']

@users.before_request
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

@users.route("/")
@users.route("/home")
@login_required
def home():
  events = Event.query.all()
  today = date.today()
  current_time = datetime.now()
  return render_template("index.html", events=events, today=today, current_time=current_time)

@users.route("/tickets/<int:event_id>", methods=["POST", "GET"])
@login_required
def tickets(event_id):
  event = Event.query.get(event_id)
  form = TicketForm()
  if event:
    if form.validate_on_submit():
      if int(request.form.get("tickets")) > event.tickets:
        flash(f"Only {event.tickets} tickets are available", category="info")
        return redirect(url_for('users.tickets', event_id=event.id))
      if current_user.is_authenticated:
        new_booking = Bookings(
          user = current_user.id,
          event = event.id,
          tickets = form.tickets.data
        )
        db.session.add(new_booking)
        event.tickets = event.tickets - int(new_booking.tickets)
        db.session.commit()
        for i in range(new_booking.tickets):
          qrcode = Qrcodes.query.filter_by(event=event.id, status="Active").first()
          qrcode.booking = new_booking.id
          qrcode.status = "Assigned"
          db.session.commit()
        # return redirect(url_for('users.payment', booking_id=new_booking.id))
        flash("Your tickets are ready", category="success")
        return redirect(url_for('users.home'))
      else:
        new_user = Users(
          first_name = form.first_name.data,
          surname = form.last_name.data,
          email = form.email.data,
          phone = form.phone_number.data,
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
        return redirect(url_for('users.home'))

    if form.errors != {}:
      for err_msg in form.errors.values():
        flash(f"{err_msg}", category="danger")
  else:
    flash("Event could not be found", category="danger")
    return redirect(url_for('users.home'))
  return render_template("book.html", event=event, form=form)

@users.route("/payment/<int:booking_id>")
@login_required
def payment(booking_id):
  booking = Bookings.query.get(booking_id)
  event = Event.query.get(booking.event)
  total = event.price * booking.tickets
  try:
    checkout_session = stripe.checkout.Session.create(
      line_items = [
        {
          'price_data': {
            'currency': 'KES',
            'product_data': {
              'name': f"{event.name}'s tickets",
            },
            'unit_amount': (total*100),
          },
          'quantity': 1,
        }
      ],
      payment_method_types=["card"],
      mode='payment',
      success_url=request.host_url + f'payment-complete/{booking.id}',
      cancel_url=request.host_url + f'payment-failed/{booking.id}',
    )
    return redirect(checkout_session.url)
  
  except:
    event.tickets = event.tickets + booking.tickets
    db.session.delete(booking)
    db.session.commit()
    flash(f"Failed to initialize connection to the stripe server", category="warning")
    return redirect(url_for('users.home'))

@users.route("/payment-complete/<int:booking_id>")
@login_required
def payment_complete(booking_id):
  booking = Bookings.query.get(booking_id)
  event = Event.query.get(booking.event)
  booking.status = "Complete"
  db.session.commit()
  flash("Payment successfull, your tickets are ready", category="success")
  message = {
    'receiver': current_user.email,
    'subject': f"{event.name}'s tickets",
    'body': f"You have successfully purchased {booking.tickets} tickets for {event.name}. \nWe thank you for your support."
  }
  send_email(**message)
  return redirect(url_for('users.home'))

@users.route("/payment-failed/<int:booking_id>")
@login_required
def payment_failed(booking_id):
  booking = Bookings.query.get(booking_id)
  event = Event.query.get(booking.event)
  event.tickets = event.tickets + booking.tickets
  db.session.delete(booking)
  db.session.commit()
  message = {
    'receiver': current_user.email,
    'subject': f"{event.name}'s tickets",
    'body': f"Your payment for {event.name} has not been received. Try again later."
  }
  send_email(**message)
  flash("Payment failed", category="danger")
  return redirect(url_for('users.home'))

@users.route("/orders")
def orders():
  bookings = Bookings.query.filter_by(user=current_user.id).all()
  qrcodes = Qrcodes.query.filter_by(status="Assigned").all()
  return render_template("orders.html", bookings=bookings, qrcodes=qrcodes)
