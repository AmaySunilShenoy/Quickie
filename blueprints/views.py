import base64
import os
from flask import Blueprint, render_template, redirect, request, session
from flask_login import login_required, current_user
from database.MongoDB.mongo import client
from services.ride_services import get_latest_ride
from services.car_services import get_car_types, get_specific_car
from services.driver_services import is_driver_verified,  get_driver_details, fs
from dotenv import load_dotenv
views_blueprint = Blueprint('views', __name__)
db = client['Quickie']
load_dotenv()

@views_blueprint.route('/', methods=["GET", "POST"])
def welcome():
    MAP_API_KEY = os.getenv('MAP_API_KEY')
    if request.method == 'POST':
        from_location = request.form.get('from-location')
        to_location = request.form.get('to-location')
        if from_location and to_location:
            session['init_from_location'] = from_location
            session['init_to_location'] = to_location
            return redirect('/home')
    return render_template('index.html', MAP_API_KEY=MAP_API_KEY)

@views_blueprint.route('/home', methods=["GET"])
@login_required
def home():
    # Admin User is redirected to admin page
    if current_user.role == 'admin':
        return redirect('/admin')
    
    # Customer User is redirected to customer home page
    if current_user.role == 'customer':
        cars = get_car_types(db)

        # To check if user has a ride in progress
        latest_ride = get_latest_ride('user',current_user.id)
        if latest_ride and (latest_ride['status'] != 'cancelled' and latest_ride['status'] != 'completed'):
            return redirect(f'/ride/{latest_ride["_id"]}')
        
        # else return customer home page
        init_from_location = session.get('init_from_location')
        init_to_location = session.get('init_to_location')

        if init_from_location and init_to_location:
            session.pop('init_from_location')
            session.pop('init_to_location')
            return render_template('homecustomer.html',user=current_user, cars=cars, step=2, init_from_location=init_from_location, init_to_location=init_to_location, MAP_API_KEY=os.getenv('MAP_API_KEY'))
        return render_template('homecustomer.html',user=current_user, cars=cars, step=1,  MAP_API_KEY=os.getenv('MAP_API_KEY'))
    
    # Driver User is redirected to driver home page
    elif current_user.role == 'driver':

        # To check if driver is verified
        driver_status =  is_driver_verified(current_user.id)

        # If driver is not verified, redirect to waiting page
        if driver_status != 'yes':
            return render_template('waiting.html', user=current_user, driver_status=driver_status)
        

        # To check if driver has a ride in progress
        latest_ride = get_latest_ride('driver',current_user.id)
        if latest_ride and (latest_ride['status'] != 'cancelled' and latest_ride['status'] != 'completed'):
            return redirect(f'/ride/progress/{latest_ride["_id"]}')
       
        # else return driver home page
        driver_details = get_driver_details(current_user.id)[0]
        driver_car = get_specific_car(db,driver_details['car_type'])
        profile_picture = fs.get(driver_details['profile_picture_id']).read()
        encoded_profile_picture = base64.b64encode(profile_picture).decode('utf-8')
        current_user.set_profile_picture(encoded_profile_picture)
        return render_template('homedriver.html',user=current_user,driver_details=driver_details, driver_car=driver_car, MAP_API_KEY=os.getenv('MAP_API_KEY'))
    else:
        return redirect('/')
    

