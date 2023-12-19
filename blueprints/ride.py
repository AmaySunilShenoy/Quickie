from datetime import datetime
from flask_pymongo import ObjectId
from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from services.sqlite_functions import auth, add_user, existing_data, get_by_id
from flask_login import login_user, logout_user, login_required, LoginManager, current_user
from classes.user_class import User
from classes.form_templates import OtpForm
from services.mail_services import send_ride_otp
from services.chat_services import create_chat, get_messages
from services.general_functions import distance, generate_otp
from services.ride_services import user_cancel_ride, get_ride_by_id,create_ride,driver_cancel_ride
from services.car_services import get_specific_car, get_car_types
from services.driver_services import get_driver_profile_picture, get_driver_details, get_driver
from database.MongoDB.mongo import client

ride_blueprint = Blueprint('ride', __name__)
db = client['Quickie']
rides = db['rides']

@ride_blueprint.route('/<ride_id>', methods=["GET", "POST"])
@login_required
def start(ride_id):
    try:
        ride = get_ride_by_id(ride_id,current_user.id)
        print('ride status:', ride['status'])
        if ride['status'] == 'accepted':
            return redirect(f'/ride/accepted/{ride_id}')
        elif ride['status'] != 'cancelled':
            return render_template('ride.html',user=current_user,car=get_specific_car(db,ride['car_name']), ride=ride)
        else:
            return redirect('/home')
    except Exception as e:
        print(e)
        return redirect('/home')
    
@ride_blueprint.route('/accepted/<ride_id>', methods=['GET'])
@login_required
def accepted(ride_id):
    form = OtpForm()
    print('role of user in accepted ride is ',current_user.role, current_user.email, current_user.firstname, current_user.lastname)
    if current_user.role == 'customer':
        if not session.get('ride_otp'):
            print('generating ride otp')
            ride_otp = generate_otp()
            session['ride_otp'] = ride_otp
            ride = get_ride_by_id(ride_id)
            chat_id = create_chat(current_user.id, ride['driver'], ride_id)

            # TODO implement send_ride_otp(ride_otp, current_user.email, ride)
            # send_ride_otp(ride_otp, current_user.email, ride)
            rides.update_one({'_id':ObjectId(ride_id)}, {'$set':{'ride_otp':f'{ride_otp}','chat_id':f'{chat_id}', 'updated_at':datetime.now().strftime("%d/%m/%Y %H:%M:%S")}})
        else:
            print('ride-otp is',session.get('ride_otp'))

        updated_ride = get_ride_by_id(ride_id)
        messages = get_messages(updated_ride['chat_id'])
        print('driver', updated_ride['driver'] )
        driver = get_driver(updated_ride['driver'])

        return render_template('ridestarted.html',user=current_user,driver=driver ,ride=updated_ride, form=form, messages=messages)
    elif current_user.role == 'driver':
        print('in driver')
        ride = get_ride_by_id(ride_id)
        driver = get_driver(ride['driver'])
        messages = get_messages(ride['chat_id'])
        return render_template('ridestarted.html',user=current_user,ride=ride,driver=driver, form=form, messages=messages)

@ride_blueprint.route('/create', methods=['POST'])
@login_required
def create():
    from_location = request.form['from-location']
    to_location = request.form['to-location']
    car_name = request.form['car-name']
    price = request.form['price']
    duration = request.form['duration']

    ride = {'user':current_user.id,'from_location':from_location, 'to_location':to_location, 'car_name':car_name, 'price':price,'duration':duration, 'status':'searching', 'driver':None,'driver_location':None ,'ride_otp': None, 'rating':None, 'review':None,'chat_id':None, 'created_at':datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 'updated_at':datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
    ride_id = create_ride(ride)
    return redirect(f'/ride/{ride_id}')

@ride_blueprint.route('/calculate', methods=['POST'])
@login_required
def calculate():
    cars = get_car_types(db)

    coordinates = request.get_json()
    print(coordinates)
    dist = distance(coordinates['from'], coordinates['to'])

    # 3.5 euros per km
    base_price = round(3.5 * dist,2)

    car_prices = [base_price * car['price_multiplier'] for car in cars]

    # 2 minutes per km
    duration = round(2 * dist)

    if dist > 40:
        status = 'unlikely'
    else:
        status = 'success'

    return {'status': status,'distance':dist, 'car_prices': car_prices, 'duration':duration}
    

@ride_blueprint.route('/cancel/<ride_id>', methods=['POST'])
@login_required
def cancel(ride_id):
    try:
        if current_user.role == 'customer':
            result = user_cancel_ride(ride_id)
        elif current_user.role == 'driver':
            result = driver_cancel_ride(ride_id)
        print('cancel result', result)
        return {'status': 'success'}
    except Exception as e:
        print(e)
        return {'status': 'failure'}
