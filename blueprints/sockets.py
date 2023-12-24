from flask import Blueprint, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from services.ride_services import get_ride_by_id, get_latest_ride, check_driver_ride
from services.driver_services import get_driver_details
from loggers.loggers import action_logger
from flask_login import current_user

socketio = SocketIO()

@socketio.on('connect', namespace='/sockets')
def handle_connect():

    # If user is a driver, join the room of the car type or the ride room if the driver has accepted a ride
    if current_user.role == 'driver':
        driver_car_type = get_driver_details(current_user.id)[0]['car_type']
        ride_id = check_driver_ride(current_user.id)
        if ride_id:
            room = f'ride_{ride_id}'
            join_room(room)
            emit('ride_accepted_by_driver', {'message': 'Ride accepted by driver'}, room=room)
        else:
            join_room(f'drivers_{driver_car_type}')
            emit('driver_connected', {'message': 'Driver connected!'})

        action_logger.info(f'SOCKETS : Driver {current_user.id} connected to sockets')

    # If user is a customer, join the room of the latest ride
    else:
        ride_id = get_latest_ride('user',current_user.id)['_id']
        join_room(f'ride_{ride_id}')
        emit('customer_connected', {'message': f'Customer connected to room {ride_id}'})
        action_logger.info(f'SOCKETS : Customer {current_user.id} connected to sockets')


@socketio.on('broadcast_ride_request', namespace='/sockets')
def handle_broadcast_ride_request(data):
    # Handles sending out ride requests to drivers with the same car type
    ride_id = data['ride_id']
    ride_details = get_ride_by_id(ride_id)
    room_name = f'drivers_{ride_details["car_name"]}'
    emit('ride_request', {'message': 'New ride request','ride_id':ride_id ,'from_location': ride_details["from_location"] , 'to_location': ride_details["to_location"] ,'price': ride_details["price"], 'duration': ride_details['duration'], 'date': ride_details['date'], 'time': ride_details['time'] },room=room_name)
    
    action_logger.info(f'SOCKETS : New ride request sent to drivers of {ride_details["car_name"]} by User {ride_details["user"]}')

@socketio.on('cancel_ride_request', namespace='/sockets')
def handle_cancel_ride_request(data):

    # Handles cancelling ride requests
    ride_id = data['ride_id']
    ride_details = get_ride_by_id(ride_id)
    room_name = f'drivers_{ride_details["car_name"]}'
    emit('ride_request_cancelled', {'message': 'Ride request cancelled', 'ride_id':ride_id}, room=room_name)
    action_logger.info(f'SOCKETS : User {ride_details["user"]} cancelled ride request {ride_id}')

@socketio.on('ride_accepted', namespace='/sockets')
def handle_ride_accepted(data):

    # Handles accepting ride requests
    ride_id = data['ride_id']
    ride_details = get_ride_by_id(ride_id)
    old_room_name = f'drivers_{ride_details["car_name"]}'

    # Join the ride room
    leave_room(old_room_name)
    emit('ride_accepted_by_other_driver', {'message': 'Ride accepted by someone else'}, room=old_room_name)
    action_logger.info(f'SOCKETS : Driver {ride_details["driver"]} accepted ride request {ride_id}')

@socketio.on('ride_started', namespace='/sockets')
def handle_ride_started(data):

    # Handles starting a ride
    room_name = f'ride_{data["ride_id"]}'
    emit('ride_started', {'message': 'Ride started'}, room=room_name)
    action_logger.info(f'SOCKETS : Ride {data["ride_id"]} started')


@socketio.on('ride_ended', namespace='/sockets')
def handle_ride_ended(data):

    # Handles ending a ride
    print('Ending ride:',data['ride_id'])
    room_name = f'ride_{data["ride_id"]}'
    emit('ride_ended', {'message': 'Ride ended'}, room=room_name)

    action_logger.info(f'SOCKETS : Ride {data["ride_id"]} ended')

@socketio.on('ride_cancelled', namespace='/sockets')
def handle_ride_cancelled(data):

    # Handles cancelling a ride
    room_name = f'ride_{data["ride_id"]}'
    if data['cancelled_by'] == 'driver':
        emit('ride_cancelled_by_driver', {'message': 'Ride cancelled by driver'}, room=room_name)
        action_logger.info(f'SOCKETS : Ride {data["ride_id"]} cancelled by driver')
    else:
        emit('ride_cancelled_by_customer', {'message': 'Ride cancelled by customer'}, room=room_name)
        action_logger.info(f'SOCKETS : Ride {data["ride_id"]} cancelled by customer')



@socketio.on('updated_driver_location', namespace='/sockets')
def handle_updated_driver_location(data):

    # Handles updating driver location
    room = f"ride_{data['ride_id']}"
    emit('updated_driver_location', {'location': data['location'], 'status': data['status']}, room=room)
    action_logger.info(f'SOCKETS : Driver  updated location for ride {data["ride_id"]} to {data["location"]}')


@socketio.on('send_message', namespace='/sockets')
def handle_send_message(data):

    # Handles sending chat messages
    print('message received:', data['message'])
    room = f"ride_{data['ride_id']}"
    emit('receive_message', {'message': data['message'], 'sender': data['sender']}, room=room)
    action_logger.info(f'SOCKETS : User {data["sender"]} sent a message to ride {data["ride_id"]}')

@socketio.on('disconnect', namespace='/sockets')
def handle_disconnect():

    # Handles disconnecting from sockets
    action_logger.info(f'SOCKETS : User {current_user.id} disconnected from sockets')
