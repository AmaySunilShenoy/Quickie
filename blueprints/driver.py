from datetime import datetime
from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from flask_login import login_required, current_user
from services.sqlite_functions import add_user
from services.user_services import add_payment_method, add_driver_files, get_driver_details
from database.MongoDB.mongo import client
from services.ride_services import get_ride_by_id
from services.driver_services import driver_accept_ride
from flask_pymongo import GridFS
driver_blueprint = Blueprint('driver', __name__)
db = client['Quickie']
rides = db['rides']
driver_details = db['driver_details']


@driver_blueprint.route('/register', methods=['POST'])
def register():
    first_name = session['signup_firstname']
    last_name = session['signup_lastname']
    email = session['signup_email']
    password = session['signup_password']
    car_type = session['signup_car']
    profile_picture = request.files['profile_picture']
    car_registration = request.files['car_registration']
    driver_license = request.files['driver_license']
    bank_details = request.files['bank_details']

    try:
        driver_id = add_user(first_name, last_name, email, password, 'driver')
        document_id = add_driver_files(driver_id, car_type ,driver_license, profile_picture, car_registration, bank_details)
        if driver_id and document_id:
            flash('Thank you for registering as a driver', 'success')
            return redirect('/connection')
        else:
            flash('Registration not successful', 'error')
            return redirect('/connection')
    except Exception as e:
        print("Error in /driver/register:", e)
        return {'status': 'error'}
    

@driver_blueprint.route('/ride_accept/<ride_id>', methods=['POST'])
@login_required
def ride_accept(ride_id):
    driver_current_location = request.get_json()['current_location']
    if driver_current_location:
        print('driver_current_location:', driver_current_location)
    else:
        print('could not get driver_current_location')
    result = driver_accept_ride(ride_id, current_user.id, driver_current_location)
    return result
