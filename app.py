import os
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from blueprints import auth, views, profile, customer, ride, driver, chat, admin
from services.sqlite_functions import get_by_id
from classes.user_class import User
from SMTP.mail_setup import init_mail
from blueprints.sockets import socketio
from blueprints.ride import scheduler
import logging
from logging.handlers import RotatingFileHandler 
from cache.cache_setup import init_cache
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')




load_dotenv()
init_mail(app)
init_cache(app)

file_handler = RotatingFileHandler('app_logs.log')
file_handler.setLevel(logging.INFO)
# Create a formatter and set it for the FileHandler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the FileHandler to the general logger
app.logger.addHandler(file_handler)

@app.before_request
def log_request_info():
    if request.path != '/favicon.ico' and not request.path.startswith('/static'):
        app.logger.info('Request Method : %s', request.method)
        app.logger.info('Request url : %s', request.url)
        app.logger.info('Request Headers : %s', dict(request.headers))
        app.logger.info('Request Data : %s', request.data)

@app.after_request
def log_response_info(response):
    if request.path != '/favicon.ico' and not request.path.startswith('/static'):
        app.logger.info('Response Status: %s', response.status)
        app.logger.info('Request Headers : %s', dict(request.headers))
    return response

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
app.register_blueprint(auth.auth_blueprint, url_prefix='/')
app.register_blueprint(views.views_blueprint, url_prefix='/')
app.register_blueprint(profile.profile_blueprint, url_prefix='/profile')
app.register_blueprint(customer.customer_blueprint, url_prefix='/customer')
app.register_blueprint(ride.ride_blueprint, url_prefix='/ride')
app.register_blueprint(driver.driver_blueprint, url_prefix='/driver')
app.register_blueprint(chat.chat_blueprint, url_prefix='/chat')
app.register_blueprint(admin.admin_blueprint, url_prefix='/admin')

if __name__ == '__main__':
    scheduler.start()
    socketio.init_app(app)
    socketio.run(app, debug=True, port=5000)