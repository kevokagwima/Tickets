from flask import Flask, flash
from flask_login import login_manager, LoginManager
from flask_migrate import Migrate
from Users.routes import users
from Admin.routes import admin
from Auth.routes import auth
from Errors.handlers import errors
from models import *
from form import *
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
csrf.init_app(app)
migrate = Migrate(app, db)
app.register_blueprint(users)
app.register_blueprint(admin)
app.register_blueprint(auth)
app.register_blueprint(errors)
login_manager = LoginManager()
login_manager.blueprint_login_views = {
  'users': '/signin',
  'admin': '/signin',
}
login_manager.login_message = "Please login to access this page"
login_manager.login_message_category = "danger"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
  try:
    return Users.query.filter_by(unique_id=user_id).first()
  except:
    flash("Unable to load user", category="danger")

if __name__ == "__main__":
  app.run(debug=True)
