import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Initialize Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pharmacy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# --- Database Models ---

class User(db.Model):
    """User model for authentication."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Medicine(db.Model):
    """Medicine model for inventory."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    manufacturer = db.Column(db.String(100), nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @property
    def is_expired(self):
        return self.expiry_date < datetime.now().date()

# --- Routes ---

@app.route('/')
def home():
    """Redirects to login page if not logged in, otherwise to the dashboard."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handles user registration."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another one.', 'danger')
            return redirect(url_for('signup'))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Handles user logout."""
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def index():
    """Displays the main dashboard with medicine inventory."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    search_query = request.args.get('search', '')
    if search_query:
        medicines = Medicine.query.filter(Medicine.name.ilike(f'%{search_query}%')).all()
    else:
        medicines = Medicine.query.all()
        
    return render_template('index.html', medicines=medicines, search_query=search_query)

@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicine():
    """Handles adding a new medicine to the inventory."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        manufacturer = request.form['manufacturer']
        expiry_date_str = request.form['expiry_date']
        quantity = request.form['quantity']
        price = request.form['price']
        
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()

        new_medicine = Medicine(
            name=name,
            manufacturer=manufacturer,
            expiry_date=expiry_date,
            quantity=int(quantity),
            price=float(price),
            added_by=session['user_id']
        )
        db.session.add(new_medicine)
        db.session.commit()
        flash('Medicine added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add_medicine.html')

@app.route('/edit_medicine/<int:medicine_id>', methods=['GET', 'POST'])
def edit_medicine(medicine_id):
    """Handles editing an existing medicine."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    medicine = Medicine.query.get_or_404(medicine_id)

    if request.method == 'POST':
        medicine.name = request.form['name']
        medicine.manufacturer = request.form['manufacturer']
        medicine.expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date()
        medicine.quantity = int(request.form['quantity'])
        medicine.price = float(request.form['price'])
        db.session.commit()
        flash('Medicine updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('edit_medicine.html', medicine=medicine)

@app.route('/delete_medicine/<int:medicine_id>', methods=['POST'])
def delete_medicine(medicine_id):
    """Handles deleting a medicine."""
    if 'user_id' not in session:
        flash('Please log in to perform this action.', 'danger')
        return redirect(url_for('login'))

    medicine = Medicine.query.get_or_404(medicine_id)
    db.session.delete(medicine)
    db.session.commit()
    flash('Medicine deleted successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
