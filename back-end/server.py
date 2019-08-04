import os
from service import configure, ensureToken, ensureKeys, getRepos, user

from flask import Flask, request, abort, render_template, jsonify, make_response
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


username = None
token = None


@app.route('/')
def index(): return render_template('index.html')


@app.route('/logout', methods=['POST'])
def logMeOut():

    if request.method == "POST":
            return ("logged out", 200)


@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    if request.method == "POST":

        global username
        username = request.json['username']
        password = request.json['password']

        global token
        token = ensureToken(username, password)
        print('token ensured: {}'.format(token))

        if ensureKeys(token):
                return ({'token': token}, 200)
    else:
        abort(400)


@app.route('/user', methods=['GET'])
@cross_origin()
def getUser():
    if request.method == "GET":
        return (user(token), 200)
    else:
        abort(400)


@app.route('/execute', methods=['POST'])
def execute():

        if request.method == "POST":
                global username
                global token
                configure(
                        repoName=request.json['repo'],
                        notifications=request.json['notifications'],
                        commitMessage=request.json['commitMessage'],
                        userInputs=list(request.json['userInputs'].values()),
                        annexFiles=list(request.json['annexFiles'].values()),
                        backPushFiles=list(request.json['backpushFiles'].values()),
                        workflow=request.json['workflow'],
                        token=token,
                        username=username
                )
                return ("Success: workflow pushed to {}".format(
                                request.json['repo']), 200)
        else:
                return ("Wrong Method", 501)


@app.route('/repos', methods=['GET'])
@cross_origin()
def repos():
    if request.method == "GET":
        global username
        return jsonify([
                {'value': repo['name'], 'text': username + '/' + repo['name']}
                for repo in getRepos(username, token)
                ])

if __name__ == '__main__':
    app.run(debug=True, port=8000, host="0.0.0.0")