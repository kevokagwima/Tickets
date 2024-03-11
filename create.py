from flask import Flask
from models import *
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def main():
  db.create_all()

def add_role():
  new_role = Role(
    role_name = "Seller"
  )
  db.session.add(new_role)
  db.session.commit()
  print(f"Added role {new_role.role_name}")

if __name__ == '__main__':
  with app.app_context():
    main()
