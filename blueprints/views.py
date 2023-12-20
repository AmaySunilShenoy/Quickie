from datetime import datetime
import base64
from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from services.sqlite_functions import auth, add_user, existing_data, get_by_id
from services.general_functions import distance
from flask_login import login_user, logout_user, login_required, LoginManager, current_user
from classes.user_class import User
from database.MongoDB.mongo import client
from services.user_services import get_driver_details, fs
from services.ride_services import get_rides, create_ride, get_ride_by_id, get_latest_ride
from services.car_services import get_car_types, get_specific_car

views_blueprint = Blueprint('views', __name__)
db = client['Quickie']

@views_blueprint.route('/')
def welcome():
    return render_template('index.html')

@views_blueprint.route('/home', methods=["GET"])
@login_required
def home():
    if current_user.role == 'customer':
        cars = get_car_types(db)
        # To check if user has a ride in progress
        latest_ride = get_latest_ride('user',current_user.id)
        if latest_ride and (latest_ride['status'] != 'cancelled'):
            return redirect(f'/ride/{latest_ride["_id"]}')
        
        return render_template('homecustomer.html',user=current_user, cars=cars, step=1)
    elif current_user.role == 'driver':
        latest_ride = get_latest_ride('driver',current_user.id)
        if latest_ride and (latest_ride['status'] != 'cancelled'):
            return redirect(f'/ride/accepted/{latest_ride["_id"]}')
        driver_details = get_driver_details(current_user.id)[0]
        driver_car = get_specific_car(db,driver_details['car_type'])
        profile_picture = fs.get(driver_details['profile_picture_id']).read()
        encoded_profile_picture = base64.b64encode(profile_picture).decode('utf-8')
        current_user.profile_picture = encoded_profile_picture
        return render_template('homedriver.html',user=current_user,driver_details=driver_details, driver_car=driver_car)
    else:
        return redirect('/')