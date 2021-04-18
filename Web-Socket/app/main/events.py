from flask import session
from flask_socketio import emit, join_room, leave_room
from .. import socketio
import requests, json
from . import api
@socketio.on('joined', namespace='/chat')
def joined(message):

    room = session.get('room')
    join_room(room)
    emit('status', {'msg': 'vanhocvp' + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room')
    # call API
    data={
            "sender_id":room,
            "message": message['msg']
        }
    res = requests.post(url= api['API_CONVERSATION'], json = data).content
    res = eval(res)
    emit('message_client', {'msg': message['msg']}, room=room)
    # print (res['message'])
    emit('message_bot', {'msg': res['text']}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': 'vanhocvp' + ' has left the room.'}, room=room)

