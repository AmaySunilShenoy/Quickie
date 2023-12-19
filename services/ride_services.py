from flask import session
from flask_pymongo import ObjectId
from database.MongoDB.mongo import client

db = client['Quickie']

# Ride Database Functions
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
    ride = rides.find_one({col:id}, sort=[('created_at', -1)])
    return ride
def create_ride(ride):
    rides = db['rides']
    result = rides.insert_one(ride)
    ride_id = result.inserted_id
    return ride_id

def user_cancel_ride(ride_id):
    rides = db['rides']
    session.pop('ride_otp', None)
    result = rides.update_one({"_id": ObjectId(ride_id)}, {"$set": {"status": "cancelled"}})
    return result

def driver_cancel_ride(ride_id):
    rides = db['rides']
    result = rides.update_one({"_id": ObjectId(ride_id)}, {"$set": {"driver": None, "status": "searching"}})
    return result

def check_driver_ride(driver_id):
    rides = db['rides']
    ride = rides.find_one({"driver":driver_id, "status":"accepted"})
    if ride:
        return ride['_id']
    else:
        return None