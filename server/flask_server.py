#!/usr/bin/env python3

from flask import Flask, jsonify, request, send_from_directory, make_response, redirect
from functools import wraps, update_wrapper
from datetime import datetime
import threading
import time

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
        
    return update_wrapper(no_cache, view)

# Freeboard:
# access with http://localhost:5000/freeboard/index.html#source=dashboard.json or http://localhost:5000/freeboard/
# all dashboard conf in freeboard/dashboard.json file

# Data store:
# Set key "field1": http://localhost:5000/data/set/field1?value=42
# Get key "field1": http://localhost:5000/data/get/field1
# Get all :         http://localhost:5000/data/get
# Clear all :       http://localhost:5000/data/clear

app = Flask(__name__, static_url_path='')
lock = threading.Lock()

d = {}
d['data'] = {}


# data store part
def update_thread():
    global d
    while True:
        with lock:
            d['uptime'] = d.get('uptime', 0) + 1
        time.sleep(1.0)

@app.route('/data/clear', methods=['GET'])
def clear():
    global d
    with lock:
        d['data'] = {}
        return jsonify(d)

@app.route('/data/get', methods=['GET'])
def get():
    with lock:
        return jsonify(d)

@app.route('/data/get/<name>', methods=['GET'])
def get_name(name):
    with lock:
        return jsonify(d['data'].get(name, {}))

@app.route('/data/set/<name>', methods=['GET', 'POST'])
def set(name):
    global d
    with lock:
        d['data'][name] = d['data'].get(name, {})
        d['data'][name]['value'] = request.args.get('value') or float('nan')
        d['data'][name]['time'] = time.time()
        return jsonify(d)

# freeboard part
@app.route('/')
@app.route('/freeboard/')
def freeboard_redir():
    return redirect("/freeboard/index.html#source=dashboard.json", code=302)

@app.route('/freeboard/<path:path>')
@nocache
def freeboard_dir(path):
    return send_from_directory('freeboard', path)

@app.route('/pub/<path:path>')
@nocache
def pub_dir(path):
    return send_from_directory('pub', path)

if __name__ == '__main__':
    threading.Thread(target=update_thread).start()
    app.run(threaded=True, debug=True, host='0.0.0.0')
