# -*- encoding: utf-8 -*-
import json, random, time

from flask import Flask
from flask import render_template, request, Response
from flask import session, redirect, url_for, escape
from flask import flash, get_flashed_messages

from socketio import socketio_manage
from socketio.namespace import BaseNamespace


app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {'DB': "ichat"}
app.secret_key = 'fspichatfspichatfspichat'
app.debug = True


class ChatNamespace(BaseNamespace):
    sockets = {}
    history = []
    colors = ('gray', 'purple', 'blue', 'cyan', 'green', 'yellow', 'pink', 'greenyellow', 'salmon')
    
    def recv_connect(self):
        self.username = None
        self.usercolor = None
        self.sockets[id(self)] = self
        if self.history:
            self.send({ 'type': 'history', 'data': self.history }, json=True)
    
    def disconnect(self, *args, **kwargs):
        if id(self) in self.sockets:
            del self.sockets[id(self)]
        super(ChatNamespace, self).disconnect(*args, **kwargs)
    
    def broadcast(self, message):
        for ws in self.sockets.values():
            if ws is self:
                message['data']['type'] = 'in'
            else:
                message['data']['type'] = 'out'
            ws.send(message, json=True)

    @classmethod
    def spam(cls):
        obj = {
            'time': time.strftime('%H:%M'),
            'text': '<script type="text/javascript">alert("注意！");</script>',
            'author': '垃圾信息',
            'color': 'red',
            'type': 'out'
        }
        message = { 'type': 'message', 'data': obj }
        for ws in cls.sockets.values():
            ws.send(message, json=True)
    
    def recv_message(self, data):
        data = escape(data)
        if self.username is None:
            self.username = data
            self.usercolor = random.choice(self.colors)
            self.send({ 'type': 'color', 'data': self.usercolor }, json=True)
        else:
            obj = {
                'time': time.strftime('%H:%M'),
                'text': data,
                'author': self.username,
                'color': self.usercolor,
                'type': 'out'
            }
            self.history.append(obj.copy())
            message = { 'type': 'message', 'data': obj }
            self.broadcast(message)
            
    
    
@app.route('/')
def index():
    return render_template('index.html')
    

@app.route('/socket.io/<path:rest>')
def chat(rest):
    try:
        socketio_manage(request.environ, {'/chat': ChatNamespace}, request)
    except:
        app.logger.error("Exception while handling socketio connection", exc_info=True)
    return Response()

@app.route('/spam')
def spam():
    ChatNamespace.spam()
    return Response("Message sent!")
