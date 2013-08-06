import json

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
    
    def recv_connect(self):
        self.username = None
        self.usercolor = None
        self.sockets[id(self)] = self
        if self.history:
            self.send(json.dumps({ 'type': 'history', 'data': self.history }))
    
    def disconnect(self, *args, **kwargs):
        if id(self) in self.sockets:
            del self.sockets[id(self)]
        super(ChatNamespace, self).disconnect(*args, **kwargs)
    
    @classmethod
    def broadcast(cls, message):
        for ws in cls.sockets.values():
            ws.send(message)
    
    def recv_message(self, data):
        if self.username is None:
            self.username = data
            self.usercolor = 'red'
            self.send(json.dumps( { 'type': 'color', 'data': 'red' } ))
        else:
            obj = {
                'time': 'timetest',
                'text': data,
                'author': self.username,
                'color': self.usercolor
            }
            self.history.append(obj)
            jsonData = json.dumps( { 'type': 'message', 'data': obj } )
            ChatNamespace.broadcast(jsonData)
            
    
    
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
    
