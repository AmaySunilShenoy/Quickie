from flask import session
from flask_pymongo import ObjectId
from database.MongoDB.mongo import client
from .general_functions import generate_otp
from loggers.loggers import action_logger
# from app import socketio
db = client['Quickie']

# Ride Database Functions

# Create Ride
def create_ride(ride):
    rides = db['rides']
    result = rides.insert_one(ride)
    ride_id = result.inserted_id
    action_logger.info(f'Ride {ride_id} created')
    return ride_id

# Get Rides
def get_rides():
    rides = db['rides']
    rides_list = []
    for ride in rides.find():
        rides_list.append(ride)
    return rides_list

def get_ride_by_id(ride_id, user_id=None):
    rides = db['rides']
    if user_id:
        ride = rides.find_one({"_id": ObjectId(ride_id), "user":user_id})
    else:
        ride = rides.find_one({"_id": ObjectId(ride_id)})
    return ride

def get_latest_ride(col,id):
    rides = db['rides']
    if col == 'customer':
        col = 'user'
    ride = rides.find_one({col:id}, sort=[('created_at', -1)])
    return ride


# Generate Ride OTP
def generate_ride_otp(ride_id):
    rides = db['rides']
    ride_otp = generate_otp()
    rides.update_one({"_id": ObjectId(ride_id)}, {"$set": {"ride_otp": f"{ride_otp}"}})
    return ride_otp

def get_ride_otp(ride_id):
    rides = db['rides']
    ride = rides.find_one({"_id": ObjectId(ride_id)})
    return ride['ride_otp']

# Cancel Ride
def user_cancel_ride(ride_id):
    rides = db['rides']
    session.pop('ride_otp', None)
    result = rides.update_one({"_id": ObjectId(ride_id)}, {"$set": {"status": "cancelled"}})
    action_logger.info(f'Ride {ride_id} cancelled by user')
    return result

def driver_cancel_ride(ride_id):
    rides = db['rides']
    result = rides.update_one({"_id": ObjectId(ride_id)}, {"$set": {"driver": None, "status": "searching", "ride_otp": None, "chat_id":None}})
    action_logger.info(f'Ride {ride_id} cancelled by driver')
    return result

# Check for ride in progress for driver
def check_driver_ride(driver_id):
    rides = db['rides']
    ride = rides.find_one({"driver":driver_id, "status":"accepted"})
    if ride:
        return ride['_id']
    else:
        return None
    
# Scheduling ride function, runs using ap-scheduler
def schedule_ride_search(ride_id):
    rides = db['rides']
    rides.update_one({"_id": ObjectId(ride_id)}, {"$set": {"status": "searching"}})
    # socketio.emit('scheduled_ride_searching', {'message': 'Ride started'}, room=f'ride_{ride_id}')
    action_logger.info(f'Ride {ride_id} scheduled has started searching for driver')
    return True
