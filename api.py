from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "super secret key"

db = SQLAlchemy(app)
from routes import *
from models import *
db.create_all()

if __name__ == "__main__":
    app.run(port=5000)
