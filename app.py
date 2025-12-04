from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re
import requests
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

api_key = os.getenv('API_KEY')  # Get API key from environment variable

from models import db, User # Import db and models from models.py

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

#========================================================================================================================
#                                         SESSIONS AND ROUTES
#========================================================================================================================
def login_required(f):
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

# Simple manual validation function for email (basic check)
# def is_valid_email(email):
#     return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None  # Checks for basic email format

#=========================================================================================================== 
#                                          WEATHER API
#===========================================================================================================
@app.route('/weather_API')
def weather_API():
    return render_template('weather_API.html')


def get_lan_long(city_name, state_code, country_code, API_key):
    """Get latitude and longitude of a city."""
    resp = requests.get(
        f'http://api.openweathermap.org/geo/1.0/direct?q={city_name},{state_code},{country_code}&appid={API_key}'
    )
    return resp.json()  # returns list of location data


def get_weather_results(lat, lon, api_key):
    """Get weather details using coordinates."""
    api_url = (
        f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"
    )
    r = requests.get(api_url)
    return r.json()


@app.route('/weather_results', methods=['POST'])
def render_weather_results():
    """Process the form and show weather results."""
    city_name = request.form['city'] # get city from form
    state_code = "Region IV-A"  # default state
    country_code = "PH"        # default Country

    if not api_key:
        return render_template('weather_result.html', error="API key not set in environment.")

    latlong = get_lan_long(city_name, state_code, country_code, api_key)

    if not latlong:
        return render_template('weather_result.html', error="City not found or invalid input.")

    lat = latlong[0]['lat']
    lon = latlong[0]['lon']

    data = get_weather_results(lat, lon, api_key)

    # Handle invalid response
    # if invalid data in search result
    if 'main' not in data:
        return render_template('weather_result.html', error="Unable to fetch weather data.")

    temp = "{0:.2f}".format(data["main"]["temp"])
    feels_like = "{0:.2f}".format(data["main"]["feels_like"])
    weather = data["weather"][0]["main"]
    location = data["name"]

    return render_template(
        'weather_result.html',
        location=location,
        temp=temp,
        feels_like=feels_like,
        weather=weather
    )

#===========================================================================================================
#                                           REGISTRATION
# ==========================================================================================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        student_id = request.form.get('student_id')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not student_id or not password or not confirm_password:
            flash('All fields are required.')
        elif password != confirm_password:
            flash('Passwords do not match.')
            
        #-- optional email format validation --#
        # elif not is_valid_email(email):
        #     flash('Invalid email format.')
        else:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already taken.')
                return render_template('register.html')
            existing_student_id = User.query.filter_by(student_id=student_id).first()
            if existing_student_id:
                flash('Email already registered.')
                return render_template('register.html')
            
            hashed_password = generate_password_hash(password)
            user = User(username=username, student_id=student_id, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Account created! Please log in.')
            return redirect(url_for('login'))
    return render_template('register.html')


#===========================================================================================================
#                                           LOGIN/LANDING PAGE
# ==========================================================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier')  # Username or Email
        password = request.form.get('password') # password hashing
        
        if not identifier or not password:
            flash('Both fields are required.')
        else:
            user = User.query.filter_by(username=identifier).first()
            if not user:
                user = User.query.filter_by(student_id=identifier).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['username'] = user.username
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid credentials. Please try again.','error')
    return render_template('login.html')

#===========================================================================================================
#                                           LOGOUT
# ==========================================================================================================
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

#===========================================================================================================
#                                          DASHBOARD/HOME
# ==========================================================================================================
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    return render_template(
        'dashboard.html',
        username=user.username,
        student_id=user.student_id
    )

if __name__ == '__main__':
    with app.app_context():  
        db.create_all()  # database tables

    app.run(host-'0.0.0.0', debug=True)
