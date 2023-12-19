from flask import Blueprint, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from services.user_services import get_driver_details
from services.ride_services import get_ride_by_id, get_latest_ride, check_driver_ride
from flask_login import current_user
import json

socket_bp = Blueprint('sockets', __name__)  # Use URL prefix instead of namespace
socketio = SocketIO()

@socket_bp.route('/socket_test')
def socket_test():
    return render_template('connection.html')

@socketio.on('connect', namespace='/sockets')
def handle_connect():
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
    else:
        ride_id = get_latest_ride('user',current_user.id)['_id']
        join_room(f'ride_{ride_id}')
        emit('customer_connected', {'message': f'Customer connected to room {ride_id}'})

@socketio.on('broadcast_ride_request', namespace='/sockets')
def handle_broadcast_ride_request(data):
    ride_id = data['ride_id']
    print('ride_id:', ride_id)
    ride_details = get_ride_by_id(ride_id)
    print('ride_details:', ride_details)
    room_name = f'drivers_{ride_details["car_name"]}'
    print('broadcasting ride request to', room_name)
    print('price of ride is', ride_details["price"])
    emit('ride_request', {'message': 'New ride request','ride_id':ride_id ,'from_location': ride_details["from_location"] , 'to_location': ride_details["to_location"] ,'price': ride_details["price"], 'duration': ride_details['duration']},room=room_name)

@socketio.on('cancel_ride_request', namespace='/sockets')
def handle_cancel_ride_request(data):
    ride_id = data['ride_id']
    ride_details = get_ride_by_id(ride_id)
    room_name = f'drivers_{ride_details["car_name"]}'
    emit('ride_request_cancelled', {'message': 'Ride request cancelled', 'ride_id':ride_id}, room=room_name)

@socketio.on('ride_accepted', namespace='/sockets')
def handle_ride_accepted(data):
    print(data['message'])
    ride_id = data['ride_id']
    ride_details = get_ride_by_id(ride_id)
    old_room_name = f'drivers_{ride_details["car_name"]}'
    leave_room(old_room_name)
    emit('ride_accepted_by_other_driver', {'message': 'Ride accepted by someone else'}, room=old_room_name)

@socketio.on('ride_cancelled', namespace='/sockets')
def handle_ride_cancelled(data):
    room_name = f'ride_{data["ride_id"]}'
    if data['cancelled_by'] == 'driver':
        leave_room(room_name)
        emit('ride_cancelled_by_driver', {'message': 'Ride cancelled by driver'}, room=room_name)
    else:
        leave_room(room_name)
        emit('ride_cancelled_by_customer', {'message': 'Ride cancelled by customer'}, room=room_name)



@socketio.on('updated_driver_location', namespace='/sockets')
def handle_updated_driver_location(data):
    room = f"ride_{data['ride_id']}"
    emit('updated_driver_location', {'location': data['location']}, room=room)


@socketio.on('send_message', namespace='/sockets')
def handle_send_message(data):
    print('message received:', data['message'])
    room = f"ride_{data['ride_id']}"
    emit('receive_message', {'message': data['message'], 'sender': data['sender']}, room=room)

@socketio.on('disconnect', namespace='/sockets')
def handle_disconnect():
    print('Client disconnected')
