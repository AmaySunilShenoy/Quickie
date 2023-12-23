from datetime import datetime
import base64
from flask_pymongo import GridFS
from .ride_services import get_ride_by_id
from flask_pymongo import ObjectId
from database.MongoDB.mongo import client
from .sqlite_functions import get_by_id
from .mail_services import send_driver_approved, send_driver_rejected
from .general_functions import average_rating
from loggers.loggers import action_logger
from io import BytesIO
db = client['Quickie']
rides = db['rides']
drivers = db['driver_details']
fs = GridFS(db, 'driver_files')


def driver_accept_ride(ride_id, driver_id, current_location):
    ride = get_ride_by_id(ride_id)
    print('ride:', ride)
    if ride['status'] == 'searching':
        update = {'status':'accepted', 'driver':driver_id,'driver_location': current_location, 'updated_at':datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
        rides.update_one({'_id':ObjectId(ride_id)}, {'$set':update})
        action_logger.info(f'Ride {ride_id} accepted by driver {driver_id}')
        return {'status':'success'}
    else:
        return {'status':'error'}

def get_driver_document(driver_id, document_name):
    driver_details = get_driver_details(driver_id)[0]
    if document_name == 'driver_license':
        driver_license = fs.get(driver_details['driver_license_id']).read()
        encoded_driver_license = BytesIO(driver_license)
        return encoded_driver_license

    elif document_name == 'car_registration':
        car_registration = fs.get(driver_details['car_registration_id']).read()
        encoded_car_registration = BytesIO(car_registration)
        return encoded_car_registration

    elif document_name == 'bank_details':
        bank_details = fs.get(driver_details['bank_details_id']).read()
        encoded_bank_details = BytesIO(bank_details)
        return encoded_bank_details
    elif document_name == 'profile_picture':
        profile_picture = fs.get(driver_details['profile_picture_id']).read()
        encoded_profile_picture = base64.b64encode(profile_picture).decode('utf-8')
        return encoded_profile_picture


def get_driver(driver_id):
    driver_details = get_driver_details(driver_id)
    if not driver_details:
        return None
    else:
        driver_details = driver_details[0]
    driver_sql = get_by_id(driver_id)
    driver = {
        'id': driver_id,
        'email': driver_sql[3],
        'firstname': driver_sql[1],
        'lastname': driver_sql[2],
        'rating': driver_details['rating'],
        'car_type': driver_details['car_type'],
        'profile_picture': get_driver_document(driver_id, 'profile_picture')
    }

    return driver

def get_rides_by_driver(driver_id):
    rides = list(db.rides.find({'driver':driver_id}))
    return rides

def update_driver_details(driver_id,driver_details):
    result = drivers.update_one({'driver_id':driver_id}, {'$set':driver_details})
    action_logger.info(f'Driver {driver_id} details updated')
    return result

def update_driver_rating(driver_id):
    driver_details = get_driver_details(driver_id)
    if not driver_details:
        return None
    else:
        driver_details = driver_details[0]
    rides = get_rides_by_driver(driver_id)
    ratings = [ride['rating'] for ride in rides if ride['rating'] != None]
    print('ratings:', ratings)
    average = average_rating(ratings)
    print(average)
    driver_details['rating'] = average
    update_driver_details(driver_id,driver_details)
    action_logger.info(f'Driver {driver_id} rating updated')
    return average_rating

# Add driver details
def add_driver_files(driver_id, car_type ,driver_license, profile_picture, car_registration, bank_details):
    try:
        # Upload the files to the file storage system
        profile_picture_id = fs.put(profile_picture, driver_id=driver_id, file_type='profile_picture')
        driver_license_id = fs.put(driver_license, driver_id=driver_id, file_type='driver_license')
        car_registration_id = fs.put(car_registration, driver_id=driver_id, file_type='car_registration')
        bank_details_id = fs.put(bank_details, driver_id=driver_id, file_type='bank_details')

        # Insert the driver details into the database
        result = drivers.insert_one({
            'driver_id': driver_id,
            'car_type': car_type,
            'verified': 'no',
            'rating': 0,
            'rides': 0,
            'profile_picture_id': profile_picture_id,
            'driver_license_id': driver_license_id,
            'car_registration_id': car_registration_id,
            'bank_details_id': bank_details_id,
            'created_at': datetime.now()
        })

        action_logger.info(f'Driver {driver_id} details and files added')
        return result
    except Exception as e:
        print('Error in add_driver_details:', e)
        return None
    

# Get driver details by driver_id
def get_driver_details(driver_id):
    driver_details = drivers.find({'driver_id':driver_id})
    return list(driver_details)

# Update driver details
def update_driver(driver_id, update):
    try:
        result = drivers.update_one({'driver_id':driver_id}, {'$set':update})
        action_logger.info(f'Driver {driver_id} updated')
        return {'status':'success'}
    except Exception as e:
        action_logger.error(f'Error in updating driver {driver_id}: {e}')
        return {'status':'error', 'error_type':e}

# Delete driver by driver_id
def delete_driver(driver_id):
    try:
        result = drivers.delete_one({'driver_id':driver_id})
        files = fs.find({'driver_id':driver_id})
        for file in files:
            fs.delete(file._id)
        action_logger.info(f'Driver {driver_id} deleted')
        return {'status':'success'}
    except Exception as e:
        action_logger.error(f'Error in deleting driver {driver_id}: {e}')
        return {'status':'error', 'error_type':e}




# Admin Functions

# Check if driver is verified
def is_driver_verified(driver_id):
    driver_details = get_driver_details(driver_id)
    if not driver_details:
        return None
    else:
        driver_details = driver_details[0]
    if driver_details['verified'] == 'yes':
        return 'yes'
    elif driver_details['verified'] == 'rejected':
        return 'rejected'
    else:
        return 'no'
    

# Get all drivers which are unverified
def get_unverified_drivers():
    unverified_drivers = drivers.find({'verified':'no'})
    unverified_drivers = list(unverified_drivers)
    driver_list = []
    for unverified in unverified_drivers:
        driver = get_driver(unverified['driver_id'])
        driver_list.append(driver)

    return driver_list


# Approve driver
def approve_driver(driver_id):
    try:
        result = drivers.update_one({'driver_id':driver_id}, {'$set':{'verified':'yes'}})
        driver = get_driver(driver_id)
        send_driver_approved(driver['email'])
        action_logger.info(f'Driver {driver_id} approved by Admin')
        return {'status':'success'}
    except Exception as e:
        return {'status':'error', 'error_type':e}

# Reject driver
def reject_driver(driver_id):
    try:
        result = drivers.update_one({'driver_id':driver_id}, {'$set':{'verified':'rejected'}})
        driver = get_driver(driver_id)
        send_driver_rejected(driver['email'])
        action_logger.info(f'Driver {driver_id} rejected by Admin')
        return {'status':'success'}
    except Exception as e:
        return {'status':'error', 'error_type':e}