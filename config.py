import os

class Config:
  SECRET_KEY = os.environ.get("Hms_Secret_key")
  SQLALCHEMY_DATABASE_URI = "mssql+pyodbc://KEVINKAGWIMA/tickets?driver=ODBC+Driver+11+for+SQL+Server"
  SQLALCHEMY_TRACK_MODIFICATIONS = False