import os
from service import configure, ensureToken, ensureKeys, getRepos, user, log

from flask import Flask, request, abort, render_template, jsonify, make_response
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


username = None
GIN_TOKEN = None
DRONE_TOKEN = None


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

        global GIN_TOKEN
        GIN_TOKEN = ensureToken(username, password)
        log("info", 'GIN_TOKEN ensured: {}'.format(GIN_TOKEN))
        
        if ensureKeys(GIN_TOKEN):
                return ({'token': GIN_TOKEN}, 200)
        else:
                abort(400)
    else:
        abort(400)


@app.route('/user', methods=['GET'])
@cross_origin()
def getUser():
    if request.method == "GET":
        return (user(GIN_TOKEN), 200)
    else:
        abort(400)


@app.route('/execute', methods=['POST'])
def execute():

        if request.method == "POST":
                global username
                global GIN_TOKEN
                configure(
                        repoName=request.json['repo'],
                        notifications=request.json['notifications'].values(),
                        commitMessage=request.json['commitMessage'],
                        userInputs=request.json['userInputs'].values(),
                        workflow=request.json['workflow'],
                        annexFiles=request.json['annexFiles'].values(),
                        backPushFiles=request.json['backpushFiles'].values(),
                        token=GIN_TOKEN,
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
                for repo in getRepos(username, GIN_TOKEN)
                ])

if __name__ == '__main__':
    app.run(debug=True, port=8000, host="0.0.0.0")