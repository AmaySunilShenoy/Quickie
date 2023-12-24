from flask_mail import Message
from flask import render_template
from SMTP.mail_setup import mail
from services.customer_services import get_payment_method
from services.sqlite_functions import get_by_id
from loggers.loggers import action_logger

def send_auth_otp(otp, user_email):
        try:
                msg = Message('Login Attempt', sender='Quickie@noreply.com', recipients=[f'{user_email}'])
                msg.body = f'Your OTP for your Quickie login is'
                msg.html = render_template('otp_template.html', otp=otp,content=msg.body)
                mail.send(msg) 
                action_logger.info(f'OTP sent to {user_email}')
        except Exception as e:
                print(e) 

def send_ride_otp(otp, user_email, ride):
        msg = Message('Ride OTP', sender='Quickie@noreply.com', recipients=[f'{user_email}'])
        driver_id = ride['driver']
        driver = get_by_id(driver_id)
        driver_name = driver[1] + ' ' +  driver[2]
        from_location = ride['from_location']
        to_location = ride['to_location']
        msg.body = f'''Your OTP for your Quickie ride with {driver_name} from {from_location} to {to_location} is 
                \n
                OTP - {otp}
                \n
                '''
        msg.html = render_template('otp_template.html', otp=otp,content=msg.body)
        mail.send(msg)
        action_logger.info(f'Ride OTP sent to {user_email}')
        
        
def send_ride_confirmation(user_email, ride):
        msg = Message('Ride Confirmation',sender='Quickie@noreply.com', recipients=[f'{user_email}'])
        driver_name = ride['firstname'] + ride['lastname']
        from_location = ride['from_location']
        to_location = ride['to_location']
        msg.body = f'''Your Quickie ride with {driver_name} from {from_location} to {to_location} has been confirmed
                \n
                '''
        mail.send(msg)
        action_logger.info(f'Ride confirmation mail sent to {user_email}')
        
        
def send_ride_cancelled(user_email, ride):
        msg = Message('Ride Cancelled',sender='Quickie@noreply.com', recipients=[f'{user_email}'])
        from_location = ride['from_location']
        to_location = ride['to_location']
        msg.body = f'''Your Quickie ride from {from_location} to {to_location} has been cancelled
                \n
                '''
        mail.send(msg)
        action_logger.info(f'Ride cancelled mail sent to {user_email}')
        
        
def send_payment_invoice(user_id,user_email, ride):
        msg = Message('Payment Invoice',sender='Quickie@noreply.com', recipients=[f'{user_email}'])
        driver_id = ride['driver']
        driver = get_by_id(driver_id)
        driver_name = driver[1] + ' ' +  driver[2]
        from_location = ride['from_location']
        to_location = ride['to_location']
        payment_method = get_payment_method(user_id)
        msg.html = render_template('payment_invoice.html', driver_name=driver_name, from_location=from_location, to_location=to_location,price=ride['price'], payment_method=payment_method['card_number'][-4:])
        mail.send(msg)
        action_logger.info(f'Payment invoice mail sent to {user_email}')

        
        
def send_driver_approved(user_email):
        msg = Message('Driver Approved',sender='Quickie@noreply.com', recipients=[f'{user_email}'])
        msg.body = f'''Your Quickie driver account has been approved. You can now start accepting rides.
                \n
                '''
        mail.send(msg)
        action_logger.info(f'Driver approved mail sent to {user_email}')
        
        
def send_driver_rejected(user_email):
        msg = Message('Driver Rejected',sender='Quickie@noreply.com', recipients=[f'{user_email}'])
        msg.body = f'''Your Quickie driver account has been rejected. Please contact Quickie support for more information.
                \n
                '''
        mail.send(msg)
        action_logger.info(f'Driver rejected mail sent to {user_email}')
        
        
        
