from flask import Blueprint, render_template, request, redirect, flash, session, g
from classes.form_templates import SignUpFormDriver, SignUpFormUser, OtpForm
from services.sqlite_functions import auth, check_user
from flask_login import login_user, logout_user, current_user
from classes.user_class import User
from services.general_functions import generate_otp
from services.car_services import get_car_types
from services.mail_services import send_auth_otp
from services.ride_services import get_ride_otp
from services.ride_services import get_latest_ride
from loggers.loggers import performance_logger, action_logger
from dotenv import load_dotenv
from database.MongoDB.mongo import client
import time

load_dotenv()
auth_blueprint = Blueprint('auth', __name__)
db = client['Quickie']




# Connection page to login or signup
@auth_blueprint.route('/connection', methods=["GET"])
def connection():

    # Flask WTF forms
    driver_form=SignUpFormDriver
    user_form=SignUpFormUser

    # If user is already logged in, redirect to home
    if not current_user.is_anonymous:
        return redirect('/home')
    
    # If user is not logged in, check if user has only otp vefication left
    elif session.get('authenticated_user'):
        return redirect('/otp')
    
    # else return connection page
    return render_template('connection.html',user_form=user_form, driver_form=driver_form)


# JSON return for checking if user exists
@auth_blueprint.route('/check', methods=["POST"])
def check():
    email = request.form['email']
    print('email is',email)
    if email:
        user = check_user(email)
        if user:
            return {'user':'exists'}
        else:
            session['signup_email'] = email
            return {'user':None}
    else:
        return {'user':None}
    

# OTP verification page
@auth_blueprint.route('/otp', methods=["GET", "POST"])
def otp():

    # Flask WTF form
    form = OtpForm()

    # Getting user email from session
    user_email = session.get('authenticated_user')[3] if session.get('authenticated_user') else session.get('signup_email') 
    otp = session.get('otp')

    # If method is POST, check if OTP is correct
    if request.method == 'POST':
        if form.is_submitted() and form.validate():
            number1 = form.number1.data
            number2 = form.number2.data
            number3 = form.number3.data
            number4 = form.number4.data
            user_input_otp = number1 + number2 + number3 + number4

            action_logger.info(f'User {user_email} entered otp {user_input_otp}')

            # If OTP is correct, log user in
            if user_input_otp == f'{otp}':
                user = session.get('authenticated_user')
                login_user(User(*user))        
                session.pop('authenticated_user')
                session.pop('otp')

                # Logging user action and performance
                action_logger.info(f'User {user[0]} logged in after otp verification')
                return redirect('/home')
            else:
                flash('The OTP is incorrect', 'danger')

    if request.method == 'GET':

        # If OTP is not generated, generate OTP and send email (this is to prevent many emails being sent on every GET request)
        if not otp:
            otp = generate_otp()
            print('otp is',otp)
            session['otp'] = otp
            try:
                send_auth_otp(otp, user_email)
            except Exception as e:
                print("Error while sending email: ",e)
    print('otp is s', otp)
    return render_template('otp.html', form=form, user_email=user_email)
    

@auth_blueprint.route('/login', methods=["POST"])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    print('email and password is', email, password)
    if email and password:
        user = auth(email,password)
        if user:
            session['authenticated_user'] = user
            return {'user':user}
        else:
            print('user not found')
            return {'user':None}
    else:
        print('no email found in /check')
        return {'user':None}


@auth_blueprint.route('/logout', methods=['POST','GET'])
def logout():
    latest_ride = get_latest_ride(current_user.role,current_user.id)
    print('latest ride during logout is', latest_ride)
    if latest_ride and latest_ride['status'] not in ['completed', 'cancelled', 'scheduled']:
        flash('You cannot logout while you have an ongoing ride. Please cancel the ride before you logout!', 'danger')
        return redirect('/home')

    if not current_user.is_anonymous:
        action_logger.info(f'User {current_user.id} logged out')
    else:
        action_logger.info(f'User logged out')
    logout_user()
    return redirect('/')


# Multipage signup and storing data in session
@auth_blueprint.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        if request.form['step'] == '1':
            session['signup_firstname'] = request.form['first_name']
            session['signup_lastname'] = request.form['last_name']
            return render_template("signup.html", step=2)
        elif request.form['step'] == '2':
            session['signup_password'] = request.form['password']
            return render_template("signup.html", step=3)
        elif request.form['step'] == 'skip':
            return render_template("signup.html", step='skip')
        elif request.form['step'] == 'driver':
            return render_template("signup.html", step='driver1')
        elif request.form['step'] == 'driver1':
            cars = get_car_types(db)
            return render_template("signup.html", step='driver2',cars=cars)
        elif request.form['step'] == 'driver2':
            session['signup_car'] = request.form['car_name']
            return render_template("signup.html", step='driver3')
        elif request.form['step'] == 'driver3':
            return render_template("signup.html", step='driver4')
    return render_template("signup.html", step=1)