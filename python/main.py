from flask import Flask, request, make_response, redirect, send_from_directory
from setup import *
from pickle import dump, load
app = Flask(__name__)
app.config['SESSION_COOKIE_SECURE'] = True


@app.route('/python/get')
def get():
    net = load(open('net.dmp', 'rb'))
    code = int(request.args.get('room_id'))
    return net.games[code].get() if (code and code in net.games) else ('Game Not Found', 404)

@app.route('/python/join')
def join():
    net = load(open('net.dmp', 'rb'))
    code = int(request.args.get('room_id'))
    query = request.args.get('query')
    if query == 'status':
        return str(net.status(code))
    elif query == 'connect':
        x = net.join(code)
        dump(net, open('net.dmp', 'wb'))
        return x
    else:
        return 'bad request', 400

@app.route('/python/summon')
def summon():
    net = load(open('net.dmp', 'rb'))
    code = int(request.args.get('room_id'))
    pid = request.args.get('id')
    net.games[code].summon(pid, color=True, coords=[1, 1])
    dump(net, open('net.dmp', 'wb'))
    return 'OK'

@app.route('/python/console')
def console():
    net = load(open('net.dmp', 'rb'))
    code = int(request.args.get('room_id'))
    execute(net.games[code], request.args.get('query'))
    dump(net, open('net.dmp', 'wb'))
    return 'OK'

@app.route('/python/check')
def check():
    net = load(open('net.dmp', 'rb'))
    return net.piece_types
