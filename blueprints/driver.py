from flask import Blueprint, request, redirect, flash, session
from flask_login import login_required
import time
from services.sqlite_functions import add_user
from database.MongoDB.mongo import client
from services.driver_services import get_driver, add_driver_files,update_driver, delete_driver
from loggers.loggers import performance_logger, action_logger
from flask_pymongo import ObjectId
driver_blueprint = Blueprint('driver', __name__)
db = client['Quickie']
rides = db['rides']
driver_details = db['driver_details']

# CRUD operations for drivers


# Create
@driver_blueprint.route('/register', methods=['POST'])
def register():
    start_time = time.time()

    # Get data from form and session (due to multi-page form)
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
        # Add user to database (SQLite)
        driver_id = add_user(first_name, last_name, email, password, 'driver')

        # Add driver details to database (MongoDB GridFS and MongoDB driver details collection)
        document_id = add_driver_files(driver_id, car_type ,driver_license, profile_picture, car_registration, bank_details)
        
        
        if driver_id and document_id:
            flash('Thank you for registering as a driver', 'success')
            session.pop('signup_firstname')
            session.pop('signup_lastname')
            session.pop('signup_email')
            session.pop('signup_password')
            session.pop('signup_car')
            end_time = time.time()
            action_logger.info(f'User {driver_id} registered as a driver')
            performance_logger.info(f'Route - /driver/register loaded in {(end_time - start_time) : .3f} seconds')
            return redirect('/connection')
        else:
            flash('Registration not successful', 'error')
            action_logger.error(f'Error in /driver/register: {e}')
            return redirect('/connection')
        
    except Exception as e:
        print("Error in /driver/register:", e)
        return {'status': 'error'}
    

# Read
@driver_blueprint.route('/<driver_id>', methods=['GET'])
@login_required
def read(driver_id):
    start_time = time.time()
    driver = get_driver(driver_id)
    if driver:
        end_time = time.time()
        performance_logger.info(f'Route - /driver/{driver_id} loaded in {(end_time - start_time) : .3f} seconds')
        return {'driver': driver}
    else:
        return {'driver':None}
    

# Update
@driver_blueprint.route('/update/<driver_id>', methods=['POST'])
@login_required
def update(driver_id):
    update = request.get_json()
    driver = get_driver(driver_id)
    if driver:
        return update_driver(driver_id, update)
    else:
        return {'status': 'error', 'error_type': 'Driver not found'}
    

# Delete
@driver_blueprint.route('/delete/<driver_id>', methods=['POST'])
@login_required
def delete(driver_id):
    driver = get_driver(driver_id)
    if driver:
        return delete_driver(driver_id)
    else:
        return {'status': 'error', 'error_type': 'Driver not found'}
    


# Function to initiate ride for driver
@driver_blueprint.route('/ride_start/<ride_id>', methods=['POST'])
@login_required
def ride_start(ride_id):
    try:
        result = rides.update_one({"_id": ObjectId(ride_id)}, {"$set": {"status": "started", "driver_location": request.get_json()['driver_location']}})
        return {'status': 'success'}
    except Exception as e:
        return {'status': 'error', 'error_type': e}
