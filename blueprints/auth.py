from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from flask_mail import Message
from classes.form_templates import SignUpFormDriver, SignUpFormUser, LogInForm, OtpForm
from services.sqlite_functions import auth, add_user, existing_data, get_by_id, check_user
from flask_login import login_user, logout_user, login_required, LoginManager, current_user
from classes.user_class import User
from services.general_functions import generate_otp
from services.car_services import get_car_types
from services.mail_services import send_auth_otp
from SMTP.mail_setup import mail
from dotenv import load_dotenv
from database.MongoDB.mongo import client
import os

load_dotenv()


auth_blueprint = Blueprint('auth', __name__)
db = client['Quickie']


@auth_blueprint.route('/connection', methods=["GET"])
def connection():
    driver_form=SignUpFormDriver
    user_form=SignUpFormUser

    if not current_user.is_anonymous:
        return redirect('/home')
    elif session.get('authenticated_user'):
        print('it is auth, sending to otp')
        return redirect('/otp')
    return render_template('connection.html',user_form=user_form, driver_form=driver_form)

@auth_blueprint.route('/check', methods=["POST"])
def check():
    email = request.form['email']
    print('email is',email)
    if email:
        user = check_user(email)
        if user:
            return {'user':user}
        else:
            return {'user':None}
    else:
        print('no email found in /check')
        return {'user':None}
    
@auth_blueprint.route('/otp', methods=["GET", "POST"])
def otp():
    form = OtpForm()
    user_email = session.get('authenticated_user')[3]
    otp = session.get('otp')
    if request.method == 'POST':
        if form.is_submitted() and form.validate():
            number1 = form.number1.data
            number2 = form.number2.data
            number3 = form.number3.data
            number4 = form.number4.data
            user_input_otp = number1 + number2 + number3 + number4
            print('user inputted:',user_input_otp, 'and correct is',otp)
            if user_input_otp == f'{otp}':
                user = session.get('authenticated_user')
                login_user(User(*user))
                session.pop('authenticated_user')
                session.pop('otp')
                return redirect('/home')
            else:
                print('incorrect otp')
                flash('incorrect otp', 'danger')

    if request.method == 'GET':
        if not otp:
            otp = generate_otp()
            print('otp is',otp)
            session['otp'] = otp
            try:
                send_auth_otp(otp, user_email)
                print('email sent without any error')
            except Exception as e:
                print("Error while sending email: ",e)

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
    logout_user()
    return redirect('/')

@auth_blueprint.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        print('step is', request.form['step'])
        if request.form['step'] == '1':
            return render_template("signup.html", step=2)
        elif request.form['step'] == '2':
            return render_template("signup.html", step=3)
        elif request.form['step'] == 'skip':
            return render_template("signup.html", step='skip')
        elif request.form['step'] == 'driver':
            return render_template("signup.html", step='driver1')
        elif request.form['step'] == 'driver1':
            cars = get_car_types(db)
            return render_template("signup.html", step='driver2',cars=cars)
        elif request.form['step'] == 'driver2':
            return render_template("signup.html", step='driver3')
        elif request.form['step'] == 'driver3':
            return render_template("signup.html", step='driver4')
    return render_template("signup.html", step=1)