from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from flask_login import login_required, current_user
from services.sqlite_functions import add_user
from services.user_services import add_payment_method
from database.MongoDB.mongo import client

customer_blueprint = Blueprint('customer', __name__)
db = client['Quickie']
rides = db['rides']

@customer_blueprint.route('/register', methods=['POST'])
def register():
    first_name = session.get('signup_firstname')
    last_name = session['signup_lastname']
    email = session['signup_email']
    password = session['signup_password']
    card_number = request.form['card_number']
    cvv = request.form['cvv']
    expiry_month = request.form['expiry_month']
    expiry_year = request.form['expiry_year']
    expiration_date = f'{expiry_month}/{expiry_year}'

    try:
        user_id = add_user(first_name, last_name, email, password, 'customer')
        add_payment_method(user_id, card_number, cvv, expiration_date)
        flash('Thank you for registering as a customer', 'success')
        return redirect('/connection')
    except Exception as e:
        print("Error in /customer/register:", e)
        return {'status': 'error'}


