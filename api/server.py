import time
from flask import Flask

server = Flask(__name__, static_folder='../build', static_url_path='/')


@server.route('/')
def index():
	return "Hello, World!"


@server.route('/api/time')
def get_current_time():
	return {'time':time.time()}