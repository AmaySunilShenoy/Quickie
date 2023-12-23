import base64
from flask import Blueprint, render_template, redirect
from flask_login import login_required, current_user
from database.MongoDB.mongo import client
from services.ride_services import get_latest_ride
from services.car_services import get_car_types, get_specific_car
from services.driver_services import is_driver_verified,  get_driver_details, fs

views_blueprint = Blueprint('views', __name__)
db = client['Quickie']

@views_blueprint.route('/')
def welcome():
    return render_template('index.html')

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
        return render_template('homecustomer.html',user=current_user, cars=cars, step=1)
    
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
        return render_template('homedriver.html',user=current_user,driver_details=driver_details, driver_car=driver_car)
    else:
        return redirect('/')
    

