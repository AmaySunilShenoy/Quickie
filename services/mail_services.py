from flask_mail import Mail, Message

def send_auth_otp(otp, user_email):
    if type == 'auth':
        msg = Message('Login Attempt', sender='Quickie@noreply.com', recipients=[f'{user_email}'])
        msg.body = f'''Your OTP for Quickie is 
                \n
                OTP - {otp}
                \n
                '''

def send_ride_otp(otp, user_email, ride):
        msg = Message('Ride OTP', sender='Quickie@noreply.com', recipients=[f'{user_email}'])
        driver_name = ride['firstname'] + ride['lastname']
        from_location = ride['from_location']
        to_location = ride['to_location']
        msg.body = f'''Your OTP for your Quickie ride with {driver_name} from {from_location} to {to_location} is 
                \n
                OTP - {otp}
                \n
                '''