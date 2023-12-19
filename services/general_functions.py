from random import randint
from math import radians, sin, cos, sqrt, atan2
import hashlib

def generate_user_id(email):
    hashed_email = hashlib.sha256(email.encode('utf-8')).hexdigest()
    return hashed_email

def generate_otp():
    return randint(1000,9999)

def distance(coord1, coord2):
    R = 6371.0

    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    distance += distance * 0.1

    return distance



