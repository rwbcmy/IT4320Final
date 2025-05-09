from flask import Flask, render_template, request, flash, redirect, url_for, session
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

# Ensure the db folder exists
os.makedirs(os.path.join(basedir, 'db'), exist_ok=True)

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

##### Utility Functions #####
def get_cost_matrix():
    return [[100, 75, 50, 100] for _ in range(12)]

def generate_ticket():
    return "TRIP-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

##### Routes #####
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if request.method == 'POST':
        first = request.form.get('first_name', '').strip()
        last = request.form.get('last_name', '').strip()
        try:
            row = int(request.form['row'])
            col = int(request.form['column'])
        except (KeyError, ValueError):
            flash('Please select a valid seat.', 'error')
            return redirect(url_for('reserve'))

        if not (1 <= row <= 12 and 1 <= col <= 4):
            flash('Seat must be row 1–12, column 1–4.', 'error')
            return redirect(url_for('reserve'))

        if Reservation.query.filter_by(seatRow=row, seatColumn=col).first():
            flash('Seat already taken.', 'error')
            return redirect(url_for('reserve'))

        code = generate_ticket()
        res = Reservation(
            passengerName=f"{first} {last}",
            seatRow=row,
            seatColumn=col,
            eTicketNumber=code
        )
        db.session.add(res)
        db.session.commit()

        flash(f'Reservation confirmed! Your code: {code}', 'success')
        return redirect(url_for('reserve'))

    taken = {(r.seatRow, r.seatColumn) for r in Reservation.query.all()}
    prices = get_cost_matrix()
    return render_template('reserve.html', taken=taken, prices=prices)

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get("username") 
        password = request.form.get("password")

        admin_record = Admin.query.filter_by(username=username, password=password).first()
        if admin_record:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    reservations = Reservation.query.all()
    total_sales = sum(get_cost_matrix()[r.seatRow - 1][r.seatColumn - 1] for r in reservations)
    seating_chart = [['Available' for _ in range(4)] for _ in range(12)]
    for r in reservations:
        seating_chart[r.seatRow - 1][r.seatColumn - 1] = r.passengerName

    return render_template('admin_dashboard.html', reservations=reservations,
                           chart=seating_chart, total_sales=total_sales)

@app.route('/delete/<int:res_id>')
def delete_reservation(res_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    reservation = Reservation.query.get(res_id)
    if reservation:
        db.session.delete(reservation)
        db.session.commit()
        flash('Reservation deleted.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

##### Run Server #####
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Add default admin if not exists
        if not Admin.query.filter_by(username='admin').first():
            default_admin = Admin(username='admin', password='password')
            db.session.add(default_admin)
            db.session.commit()
            print("Default admin created: admin / password")

    app.run(host='0.0.0.0', port=5000, debug=True)
