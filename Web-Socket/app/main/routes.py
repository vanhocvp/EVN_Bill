from flask import session, redirect, url_for, render_template, request
from . import *
from .forms import LoginForm
import requests, json
@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')
@main.route('/chat')
def chat():
    if request.method == 'GET':
        room = requests.get(api['API_INIT']).content
        room = eval(room)
        session['room'] = room['sender_id']
    name = 'vanhocvp'
    room = session.get('room', '')
    if name == '' or room == '':
        return redirect(url_for('.index'))
    return render_template('chat.html', name=name, room=room)
