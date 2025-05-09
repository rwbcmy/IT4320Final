from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import random
import string

app = Flask(__name__)
app.secret_key = "super-secret"

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

'''
Function to generate cost matrix for flights
Input: none
Output: Returns a 12 x 4 matrix of prices
'''
def get_cost_matrix():
    cost_matrix = [[100, 75, 50, 100] for row in range(12)]
    return cost_matrix    

def generate_ticket():
    """Return e.g. 'TRIP-A4B9K2'."""
    return "TRIP-" + "".join(
        random.choices(string.ascii_uppercase + string.digits, k=6)
    )

##### Routes #####
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reserve', methods=['GET','POST'])
def reserve():
    if request.method == 'POST':
        first = request.form.get('first_name','').strip()
        last  = request.form.get('last_name','').strip()
        try:
            row = int(request.form['seat_row'])
            col = int(request.form['seat_col'])
        except (KeyError, ValueError):
            flash('Please select a valid seat.', 'error')
            return redirect(url_for('reserve'))

        if not (0 <= row < 12 and 0 <= col < 4):
            flash('Seat must be row 0–11, column 0–3.', 'error')
            return redirect(url_for('reserve'))

        # check availability
        if Reservation.query.filter_by(seatRow=row, seatColumn=col).first():
            flash('Seat already taken.', 'error')
            return redirect(url_for('reserve'))

        # create reservation
        code = generate_ticket()
        res = Reservation(
          passengerName=f"{first} {last}",
          seatRow=row, seatColumn=col,
          eTicketNumber=code
        )
        db.session.add(res)
        db.session.commit()

        flash(f'Reservation confirmed! Your code: {code}', 'success')
        return redirect(url_for('reserve'))

    taken  = {(r.seatRow, r.seatColumn) for r in Reservation.query.all()}
    prices = get_cost_matrix()
    return render_template('reserve.html', taken=taken, prices=prices)


@app.route('/admin')
def admin():
    # TODO: add admin dashboard
    return "Admin page under construction"

if __name__ == '__main__':
    # create tables if not exist
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
