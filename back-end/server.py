from flask import Flask, request, abort, render_template, jsonify, make_response
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

import os
from service import configure, authorize, ensureToken, ensureKeys, validUser, getRepos, user

auth = None
token = None

@app.route('/')
def index(): return render_template('index.html')

@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    if request.method == "POST":
        global auth
        auth = authorize(username = request.json['username'], password = request.json['password'])
        if not validUser(auth): abort(400)
        print("User {} logged in".format(request.json['username']))
        global token
        token = ensureToken(auth = auth)
        print('token ensured: {}'.format(token.name))
        print('key ensured: {}'.format(ensureKeys(token)))
        return ({'token': token.token}, 200)
    else:
        abort(400)

"""@app.route('/user', methods=['GET'])
def user():
    if request.method == "GET":
        print (user(auth, auth.username))
"""
"""@app.route('/token', methods=['GET'])
def token():
    if request.method == "GET": 
        global token
        return (token.token)
"""
@app.route('/execute', methods=['POST'])
def execute():
        try:
                if request.method == "POST":
                        global auth
                        global token
                        configure(
                        repoName = request.json['repo'], 
                        commitMessage = request.json['commitMessage'], 
                        workflowFiles = request.json['workflowFiles'], 
                        backPushFiles = request.json['backpushFiles'], 
                        token = token, 
                        auth = auth
                        )
                        return ("Success: workflow pushed to {}".format(request.json['repo']), 200)
                else: return ("Wrong Method", 501)
        except: return ("Aborted", 500)

@app.route('/repos', methods=['GET'])
def repos():
    if request.method == "GET":
        return jsonify([repo.name for repo in getRepos(auth, auth.username)])

if __name__ == '__main__':
    app.run(debug=True, port=8000, host="127.0.0.1")