import os

class Config:
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1)
  # SQLALCHEMY_DATABASE_URI = "mssql+pyodbc://KEVINKAGWIMA/tickets?driver=ODBC+Driver+11+for+SQL+Server"
  SECRET_KEY = os.environ.get("SECRET_KEY")
  SQLALCHEMY_TRACK_MODIFICATIONS = False