from flask_pymongo import ObjectId

# Car Database Functions
def get_car_types(db):
    car_types = db['car_types']
    car_types_list = []
    for car_type in car_types.find():
        car_types_list.append(car_type)
    return car_types_list

def get_specific_car(db, car_name):
    car_types = db['car_types']
    car = car_types.find_one({"car_name": car_name})
    return car

