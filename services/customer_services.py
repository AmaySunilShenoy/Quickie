from .sqlite_functions import get_by_id
from database.MongoDB.mongo import client
from loggers.loggers import action_logger
db = client['Quickie']
customer_payment_details = db['payment_methods']

def get_customer(customer_id):
    customer_details = get_by_id(customer_id)
    customer = {
        'firstname': customer_details[1],
        'lastname': customer_details[2]
    }

    return customer

# Create payment method
def add_payment_method(user_id, card_number, cvv, expiration_date):
    payment_method = {'user':user_id, 'card_number':card_number, 'cvv':cvv, 'expiration_date':expiration_date}
    result = customer_payment_details.insert_one(payment_method)
    payment_method_id = result.inserted_id
    action_logger.info(f'Payment method added for user {user_id}')
    return payment_method_id

# Read payment method
def get_payment_method(user_id):
    payment_method = customer_payment_details.find_one({'user':user_id})
    return payment_method

# Update Payment Method
def update_payment_method(user_id, card_number, cvv, expiration_date):
    payment_method = {'user':user_id, 'card_number':card_number, 'cvv':cvv, 'expiration_date':expiration_date}
    result = customer_payment_details.update_one({'user':user_id}, {'$set':payment_method})
    action_logger.info(f'Payment method updated for user {user_id}')
    return result

# Delete Payment Method
def delete_payment_method(user_id, card_number):
    result = customer_payment_details.delete_one({'user':user_id, 'card_number':card_number})
    action_logger.info(f'Payment method deleted for user {user_id}')
    return result


