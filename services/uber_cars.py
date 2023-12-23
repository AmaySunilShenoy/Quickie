import sys
from database.MongoDB.mongo import client
db = client["Quickie"]

car_types = db["car_types"]


car_list = [
    {
        "car_name": "QuickieX",
        "category" : "Recommended",
        "car_description" : "Affordable, everyday rides",
        "car_image_path": "/images/cars/QuickieX.png",
        "price_multiplier": 1.0,
        "passenger_capacity": 4
    },
    {
        "car_name": "Taxi",
        "category" : "Recommended",
        "car_description" : "Taxi trips at regulated fare as indicated by the taxi meter",
        "car_image_path": "/images/cars/Taxi.png",
        "price_multiplier": 1.2,
        "passenger_capacity": 4
    },
    {
        "car_name": "Van",
        "category" : "Popular",
        "car_description" : "High-capacity vehicles for groups of up to 6",
        "car_image_path": "/images/cars/Van.png",
        "price_multiplier": 1.5,
        "passenger_capacity": 6
    },
    {
        "car_name": "Quickie Pet",
        "category" : "More",
        "car_description" : "Ride with your pet",
        "car_image_path": "/images/cars/QuickiePet.png",
        "price_multiplier": 1.1,
        "passenger_capacity": 4
    },
    {
        "car_name": "Quickie Moto",
        "category" : "More",
        "car_description" : "Professional drivers on high-end motorbikes and maxi-scooters",
        "car_image_path": "/images/cars/QuickieMoto.png",
        "price_multiplier": 0.8,
        "passenger_capacity": 1
    },
    {
        "car_name": "Quickie Black",
        "category" : "Popular",
        "car_description" : "Premium rides in high-end cars",
        "car_image_path": "/images/cars/QuickieBlack.png",
        "price_multiplier": 1.8,
        "passenger_capacity": 4
    }
]

def create_car_types_db(db,car_list):
    result = db.insert_many(car_list)
    return result


create_car_types_db(car_types,car_list)