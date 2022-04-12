import time
from api.api import *
from flask import Flask, request, jsonify
from pprint import pprint

server = Flask(__name__, static_folder='../build', static_url_path='/')


@server.route('/')
def index():
	return "Hello, World!"


@server.route('/api/list_files', methods=['POST'])
def post_list_files():
	content = request.json
	file_list = list_files(content['sub_dir'])
	return jsonify(file_list)


@server.route('/api/time')
def get_current_time():
	return {'time':time.time()}