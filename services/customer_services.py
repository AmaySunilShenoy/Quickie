from .sqlite_functions import get_by_id

def get_customer(customer_id):
    customer_details = get_by_id(customer_id)
    customer = {
        'firstname': customer_details[1],
        'lastname': customer_details[2]
    }

    return customer