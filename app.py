from flask import Flask, render_template, flash, redirect, url_for
from flask_login import login_manager, LoginManager, login_user, logout_user, current_user
from models import * 
from form import *

app = Flask(__name__)
app.config["SECRET_KEY"] = "fvjdnjkdsnsnd"
app.config["SQLALCHEMY_DATABASE_URI"] = "mssql+pyodbc://KEVINKAGWIMA/tickets?driver=ODBC+Driver+11+for+SQL+Server"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = '/register' 
login_manager.login_message_category = "danger"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
  try:
    return Seller.query.filter_by(username=user_id).first() or Buyer.query.filter_by(username=user_id).first()
  except:
    flash("Failed to login the user", category="danger")

@app.route("/register")
def register():
  form = Registration()
  return render_template("register.html", form=form)

@app.route("/")
@app.route("/home")
def home():
  return render_template("index.html")

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0")
