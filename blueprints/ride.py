from datetime import datetime
import os
from dotenv import load_dotenv
from flask_pymongo import ObjectId
from flask import Blueprint, render_template, request, redirect, session
from flask_login import login_required, current_user
from apscheduler.schedulers.background import BackgroundScheduler
from classes.form_templates import OtpForm
from services.mail_services import send_ride_otp, send_payment_invoice
from services.chat_services import create_chat, get_messages
from services.general_functions import distance, average_rating, convert_to_24_hour_format, convert_to_ymd
from services.ride_services import user_cancel_ride, get_ride_by_id,create_ride,driver_cancel_ride, get_ride_otp, generate_ride_otp, schedule_ride_search
from services.car_services import get_specific_car, get_car_types
from services.driver_services import get_driver, driver_accept_ride, update_driver_rating
from services.customer_services import get_customer
from loggers.loggers import performance_logger, action_logger
from cache.cache_setup import cache
from database.MongoDB.mongo import client

ride_blueprint = Blueprint('ride', __name__)
db = client['Quickie']
rides = db['rides']
scheduler = BackgroundScheduler()
load_dotenv()


# Ride Middleware to check ride_id and if user is authorized to access the ride
@ride_blueprint.before_request
def before_request():
    ride_id = request.view_args.get('ride_id')

    if ride_id:
        ride = get_ride_by_id(ride_id)
        if ride:
            if current_user.role == 'customer':
                if ride['user'] != current_user.id:
                    return redirect('/home')
            elif current_user.role == 'driver' and ride['status'] != 'searching':
                if ride['driver'] != current_user.id:
                    return redirect('/home')

            cache.set('ride_id', ride_id)
            cache.set('customer', get_customer(ride['user']))
            cache.set('driver', get_driver(ride['driver']))
                
        else:
            return redirect('/home')
            

# Create a ride

@ride_blueprint.route('/create', methods=['POST'])
@login_required
def create():

    # Getting form data
    from_location = request.form['from-location']
    to_location = request.form['to-location']
    car_name = request.form['car-name']
    price = request.form['price']
    duration = request.form['duration']
    time = request.form['time']
    date = request.form['date']

    action_logger.info(f'User {current_user.id} created a ride from {from_location} to {to_location} at {time} on {date}')

    status = 'searching' if time == 'Now' else 'scheduled'
    ride = {'user':current_user.id,'from_location':from_location, 'to_location':to_location,'date':date ,'time':time,'car_name':car_name, 'price':price,'duration':duration, 'status':status, 'driver':None,'driver_location':None ,'ride_otp': None, 'rating':None, 'review':None,'chat_id':None, 'created_at':datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 'updated_at':datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
    ride_id = create_ride(ride)

    if time != 'Now':
        # Scheduling ride search using APScheduler
        year,month,day = convert_to_ymd(date)
        hour,minute = convert_to_24_hour_format(time)
        ride_datetime = datetime(year,month,day,hour,minute)
        scheduler.add_job(schedule_ride_search, 'date', run_date=ride_datetime, args=[ride_id], id=f'ride_{ride_id}')
        
    return redirect(f'/ride/{ride_id}')


# Getting a ride
@ride_blueprint.route('/<ride_id>', methods=["GET", "POST"])
@login_required
def start(ride_id):
    try:
        
        ride = get_ride_by_id(ride_id,current_user.id)
        action_logger.info(f'User {current_user.id} accessed ride {ride_id}. Status of the ride is {ride["status"]}')
        # If ride is already completed, redirect to review page
        if ride['status'] == 'completed':
            return redirect(f'/ride/review/{ride_id}')
        # If ride is accepted, redirect to in progress page
        elif ride['status'] == 'accepted':
            return redirect(f'/ride/progress/{ride_id}')
        # If ride is cancelled, redirect to home page
        elif ride['status'] == 'cancelled':
            return redirect('/home')
        # If ride is still searching, redirect to ride page
        
        return render_template('ride.html',user=current_user,car=get_specific_car(db,ride['car_name']), ride=ride, MAP_API_KEY=os.getenv('MAP_API_KEY'))
        
    except Exception as e:
        print(e)
        return redirect('/home')
        
    

# Ride in progress
@ride_blueprint.route('/progress/<ride_id>', methods=['GET'])
@login_required
def accepted(ride_id):
    form = OtpForm()
    ride = get_ride_by_id(ride_id)

    # If ride is already completed, redirect to review page
    if ride['status'] == 'completed':
            return redirect(f'/ride/review/{ride_id}')
    # If ride is still searching, redirect to ride page
    elif ride['status'] == 'searching':
        return redirect(f'/ride/{ride_id}')
    
    # If ride is cancelled, redirect to home page
    elif ride['status'] == 'cancelled':
            return redirect('/home')
    
    #  IF USER IS CUSTOMER
    if current_user.role == 'customer':

        # Ride OTP is generated only once and stored in session
        if not session.get('ride_otp'):

            # Generating ride OTP, creating a chat between the customer and driver and sending the OTP to the customer by email (but also viewable on the page)
            ride_otp = generate_ride_otp(ride_id)
            create_chat(current_user.id, ride['driver'], ride_id)
            send_ride_otp(ride_otp, current_user.email, ride)

        updated_ride = get_ride_by_id(ride_id)

        # Getting already sent messages from the database and driver details
        messages = get_messages(updated_ride['chat_id'])
        driver = get_driver(updated_ride['driver'])

        return render_template('ridestarted.html',user=current_user,driver=driver ,ride=updated_ride, form=form, messages=messages,MAP_API_KEY=os.getenv('MAP_API_KEY'))
    
    # IF USER IS DRIVER
    elif current_user.role == 'driver':
        ride = get_ride_by_id(ride_id)
        driver = get_driver(ride['driver'])
        messages = get_messages(ride['chat_id'])
        customer = get_customer(ride['user'])

        if not driver:
            return redirect('/home')

        return render_template('ridestarted.html',user=current_user,ride=ride,driver=driver, form=form, messages=messages, customer = customer,MAP_API_KEY=os.getenv('MAP_API_KEY'))


# Ride review
@ride_blueprint.route('/review/<ride_id>', methods=["GET", "POST"])
@login_required
def review(ride_id):

    if current_user.role == 'customer':
        ride = get_ride_by_id(ride_id)

        # If ride is already reviewed, redirect to home page
        if ride['rating'] != None:
            return redirect('/home')

        # If ride is already completed, redirect to review page
        if ride['status'] == 'accepted':
            return redirect(f'/ride/progress/{ride_id}')
        # If ride is still searching, redirect to ride page
        elif ride['status'] == 'searching':
            return redirect(f'/ride/{ride_id}')
        
    # Handling review form submission (rating of the driver from the user)
    if request.method == 'POST':
        try:
            data = request.get_json()
            ratings = [int(data['comfortRating']), int(data['safetyRating']), int(data['quickRating'])]
            rating = average_rating(ratings)
            rides.update_one({"_id": ObjectId(ride_id)}, {"$set": {"rating": rating, "updated_at":datetime.now().strftime("%d/%m/%Y %H:%M:%S")}})
            update_driver_rating(data['driver_id'])
            return {'status': 'success'}
        except Exception as e:
            print(e)
            return {'status': 'error'}
            
    
    ride = get_ride_by_id(ride_id)
    customer = get_customer(ride['user'])
    driver = get_driver(ride['driver'])
    if ride['status'] == 'completed':
        if current_user.role == 'customer' and not session.get('payment_invoice'):
            send_payment_invoice(ride['user'], customer['email'], ride)
            session['payment_invoice'] = True
        return render_template('review.html',user=current_user,ride=ride, customer=customer, driver=driver,MAP_API_KEY=os.getenv('MAP_API_KEY'))
    else:
        return redirect('/home')
    

# Ride OTP
@ride_blueprint.route('/otp', methods=["POST"])
@login_required
def otp():
    if request.method == 'POST':
        data = request.json
        user_ride_otp = data['otp']
        ride_id = data['ride_id']
        ride_otp = get_ride_otp(ride_id)
        print('ride otp entered is ',ride_otp, ' and user entered is ',user_ride_otp)
        if ride_otp == user_ride_otp:
            return {'status':'success'}
        else:
            return {'status':'failed'}


# Calculating ride price, distance and duration
@ride_blueprint.route('/calculate', methods=['POST'])
@login_required
def calculate():
    cars = get_car_types(db)

    coordinates = request.get_json()
    action_logger.info(f'User {current_user.id} calculated ride price from {coordinates["from"]} to {coordinates["to"]}')
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
    

# Accepting a ride
@ride_blueprint.route('/accept/<ride_id>', methods=['POST'])
@login_required
def accept(ride_id):
    try:
        result = driver_accept_ride(ride_id, current_user.id, request.get_json()['current_location'])
        return result
    except Exception as e:
        print(e)
        return {'status': 'failure'}
    

# Starting a ride
@ride_blueprint.route('/end/<ride_id>', methods=['POST'])
@login_required
def end(ride_id):
    try:
        result = rides.update_one({"_id": ObjectId(ride_id)}, {"$set": {"status": "completed", "updated_at":datetime.now().strftime("%d/%m/%Y %H:%M:%S")}})
        return {'status': 'success'}
    except Exception as e:
        return {'status': 'error', 'error_type': e}


# Cancelling a ride
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
