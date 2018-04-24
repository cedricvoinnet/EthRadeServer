from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from bson.json_util import dumps

from database import db

app = Flask(__name__)
CORS(app)

@app.route('/')
def root():
    # this route does nothing
    return 'Root route'

@app.route('/register', methods=['POST'])
def register():
    new_user = {
        'username' : request.json.get('username'),
        'password' : request.json.get('password'),
        'key' : request.json.get('key'),
        'contacts' : [],
        'visible' : True
    }
    if new_user['username'] is None or new_user['password'] is None or new_user['key'] is None:
        return make_response(jsonify('missing parameters'), 400)
    u = db.users.find_one({'key': new_user['key']})
    if u is None:
        db.users.insert_one(new_user)
    else:
        return make_response(jsonify('user already exists'), 403)
    return make_response(jsonify({'key': new_user['key']}), 200)

@app.route('/login', methods=['POST'])
def login():
    user = {
        'username' : request.json.get('username'),
        'password' : request.json.get('password')
    }
    if user['username'] is None or user['password'] is None:
        return make_response(jsonify('missing parameters'), 400)
    u = db.users.find_one({'username': user['username']})
    if u is None:
        return make_response(jsonify('user does not exists'), 403)
    if u['password'] != user['password']:
        return make_response(jsonify('not authentified'), 401)
    return make_response(jsonify({'key': new_user['key']}), 200)

@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    user = {
        'username' : request.headers.get('username'),
        'password' : request.headers.get('password')
    }
    print(user)
    u = db.users.find_one({'username': user['username']})
    if u is None:
        return make_response(jsonify('user does not exists'), 403)
    if u['password'] != user['password']:
        return make_response(jsonify('not authentified'), 401)
    if request.method == 'POST':
        new_contact = {
         'surname' : request.json.get('surname'),
         'key': request.json.get('key')
        }
        res = db.users.update_one({'username': user['username']}, {'$addToSet': {'contacts':new_contact}})
        return make_response(jsonify('successfully added'), 200)
    return make_response(jsonify(dumps(u['contacts'])), 200)

@app.route('/users', methods=['GET'])
def users():
    user = {
        'username' : request.headers.get('username'),
        'password' : request.headers.get('password')
    }
    u = db.users.find_one({'username': user['username']})
    if u is None:
        return make_response(jsonify('user does not exists'), 403)
    if u['password'] != user['password']:
        return make_response(jsonify('not authentified'), 401)
    ret = db.users.find({'visible': True}, {'_id': 0, 'password': 0, 'contacts': 0})
    return make_response(jsonify(dumps(ret)), 200)

@app.route('/visible', methods=['POST'])
def visible():
    user = {
        'username' : request.headers.get('username'),
        'password' : request.headers.get('password')
    }
    u = db.users.find_one({'username': user['username']})
    if u is None:
        return make_response(jsonify('user does not exists'), 403)
    if u['password'] != user['password']:
        return make_response(jsonify('not authentified'), 401)
    res = db.users.update_one({'username': user['username']}, {'$set': {'visible':request.json.get('visible')}})
    return make_response(jsonify('successfully changed'), 200)

@app.route('/history', methods=['GET', 'POST'])
def history():
    user = {
        'username' : request.headers.get('username'),
        'password' : request.headers.get('password')
    }
    u = db.users.find_one({'username': user['username']})
    if u is None:
        return make_response(jsonify('user does not exists'), 403)
    if u['password'] != user['password']:
        return make_response(jsonify('not authentified'), 401)

    if request.method == 'POST':
        new_history = {
            'to': request.json.get('to'),
            'from': request.json.get('from'),
            'amount': request.json.get('amount')
        }
        db.histories.insert_one(new_history)
        return make_response(jsonify('successfully added'), 200)

    ret = db.histories.find({'$or': [{'to': u['key']}, {'from': u['key']}]}, {'_id': 0})
    return make_response(jsonify(dumps(ret)), 200)
