from flask import Flask
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mssql+pyodbc://KEVINKAGWIMA/tickets?driver=ODBC+Driver+11+for+SQL+Server"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db.init_app(app)

def main():
  db.create_all()

if __name__ == '__main__':
  with app.app_context():
    main()
