from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"sqlite:///{os.path.join(basedir, 'db', 'reservations.db')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

##### Models #####
class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    passengerName = db.Column(db.String(120), nullable=False)
    seatRow = db.Column(db.Integer, nullable=False)
    seatColumn = db.Column(db.Integer, nullable=False)
    eTicketNumber = db.Column(db.String(16), nullable=False)

class Admin(db.Model):
    __tablename__ = 'admins'
    username = db.Column(db.String(80), primary_key=True)
    password = db.Column(db.String(256), nullable=False)

##### Routes #####
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reserve')
def reserve():
    # TODO: add reservation page
    return "Reserve page under construction"

@app.route('/admin')
def admin():
    # TODO: add admin dashboard
    return "Admin page under construction"

if __name__ == '__main__':
    # create tables if not exist
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
