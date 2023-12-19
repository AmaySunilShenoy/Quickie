import os
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from blueprints import auth, views, profile, customer, ride, driver, chat
from services.sqlite_functions import get_by_id
from classes.user_class import User
from SMTP.mail_setup import init_mail
from blueprints.sockets import socket_bp, socketio

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

load_dotenv()

# Login Manager
login_manager = LoginManager()
login_manager.login_view = 'auth.connection'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    user = get_by_id(user_id)
    if user:
        print(*user)
        return User(*user)
    else:
        pass

# Blueprints
init_mail(app)
app.register_blueprint(auth.auth_blueprint, url_prefix='/')
app.register_blueprint(views.views_blueprint, url_prefix='/')
app.register_blueprint(profile.profile_blueprint, url_prefix='/profile')
app.register_blueprint(socket_bp, url_prefix='/sockets')
app.register_blueprint(customer.customer_blueprint, url_prefix='/customer')
app.register_blueprint(ride.ride_blueprint, url_prefix='/ride')
app.register_blueprint(driver.driver_blueprint, url_prefix='/driver')
app.register_blueprint(chat.chat_blueprint, url_prefix='/chat')

if __name__ == '__main__':
    socketio.init_app(app)
    socketio.run(app, debug=True, port=5000)