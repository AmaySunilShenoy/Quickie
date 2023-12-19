from datetime import datetime
import base64
from .ride_services import get_ride_by_id
from .user_services import get_driver_details, fs
from flask_pymongo import ObjectId
from database.MongoDB.mongo import client
from .sqlite_functions import get_by_id
db = client['Quickie']
rides = db['rides']


def driver_accept_ride(ride_id, driver_id, current_location):
    ride = get_ride_by_id(ride_id)
    print('ride:', ride)
    if ride['status'] == 'searching':
        update = {'status':'accepted', 'driver':driver_id,'driver_location': current_location, 'updated_at':datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
        rides.update_one({'_id':ObjectId(ride_id)}, {'$set':update})
        return {'status':'success'}
    else:
        return {'status':'error'}
    
def get_driver_profile_picture(driver_id):
    driver_details = get_driver_details(driver_id)[0]
    profile_picture = fs.get(driver_details['profile_picture_id']).read()
    encoded_profile_picture = base64.b64encode(profile_picture).decode('utf-8')
    return encoded_profile_picture


def get_driver(driver_id):
    driver_details = get_driver_details(driver_id)[0]
    driver_sql = get_by_id(driver_id)
    driver = {
        'firstname': driver_sql[1],
        'lastname': driver_sql[2],
        'rating': driver_details['rating'],
        'profile_picture': get_driver_profile_picture(driver_id)
    }

    return driver