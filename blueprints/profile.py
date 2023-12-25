from flask import Blueprint, render_template, redirect
from flask_login import login_required, current_user
from services.customer_services import get_payment_method
import os
from dotenv import load_dotenv
from loggers.loggers import performance_logger
from database.MongoDB.mongo import client

profile_blueprint = Blueprint('profile', __name__)
db = client['Quickie']
rides = db['rides']

load_dotenv()

@profile_blueprint.route('/', methods=['GET'])
@login_required
def index():
    return redirect('/profile/trips')

@profile_blueprint.route('/<section>', methods=['GET'])
@login_required
def profile_info(section):
    
    if section == 'trips':
        user_rides = rides.find({'user': current_user.id})
        user_rides = list(user_rides)
        for ride in user_rides:
            print(ride)
        
        return render_template('profile.html', user=current_user, section=section, user_rides=user_rides, MAP_API_KEY=os.getenv('MAP_API_KEY'))
    elif section == 'wallet':
        user_payment = get_payment_method(current_user.id)
        
        return render_template('profile.html', user=current_user, section=section, user_payment=user_payment)
    elif section == 'settings':
        
        return render_template('profile.html', user=current_user, section=section)
    else:
        return redirect('/profile/trips')
