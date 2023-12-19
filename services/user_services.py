from database.MongoDB.mongo import client
from flask_pymongo import GridFS

# User services
db = client['Quickie']
customer_payment_details = db['payment_methods']
driver_details_db = db['driver_details']
fs = GridFS(db, 'driver_files')

def add_payment_method(user_id, card_number, cvv, expiration_date):
    payment_method = {'user':user_id, 'card_number':card_number, 'cvv':cvv, 'expiration_date':expiration_date}
    result = customer_payment_details.insert_one(payment_method)
    payment_method_id = result.inserted_id
    return payment_method_id

def get_payment_method(user_id):
    payment_method = customer_payment_details.find_one({'user':user_id})
    return payment_method


def add_driver_files(driver_id, car_type ,driver_license, profile_picture, car_registration, bank_details):
    try:

        profile_picture_id = fs.put(profile_picture, driver_id=driver_id, file_type='profile_picture')
        driver_license_id = fs.put(driver_license, driver_id=driver_id, file_type='driver_license')
        car_registration_id = fs.put(car_registration, driver_id=driver_id, file_type='car_registration')
        bank_details_id = fs.put(bank_details, driver_id=driver_id, file_type='bank_details')
        result = driver_details_db.insert_one({'driver_id':driver_id, 'car_type':car_type, 'rating': 0, 'rides': 0, 'profile_picture_id':profile_picture_id, 'driver_license_id':driver_license_id, 'car_registration_id':car_registration_id, 'bank_details_id':bank_details_id})
        return result
    except Exception as e:
        print('Error in add_driver_details:',e)
        return None
    
def get_driver_details(driver_id):
    driver_details = driver_details_db.find({'driver_id':driver_id})
    return list(driver_details)
