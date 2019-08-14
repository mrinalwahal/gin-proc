import os
from service import configure, ensureToken, ensureKeys, getRepos, userData, log

from flask import Flask, request, abort, render_template, jsonify, make_response
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


class User(object):

        def __init__(self, *args, **kwargs):
                self.username = None
                self.GIN_TOKEN = None

user = User()


@app.route('/logout', methods=['POST'])
def logMeOut():

    if request.method == "POST":

        user.username = None
        user.GIN_TOKEN = None
        user.DRONE_TOKEN = None

        return ("logged out", 200)


@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    if request.method == "POST":

        user.username = request.json['username']
        password = request.json['password']

        user.GIN_TOKEN = ensureToken(user.username, password)
        log("info", 'GIN token ensured.')

        if ensureKeys(user.GIN_TOKEN):
                return ({'token': user.GIN_TOKEN}, 200)
        else:
                abort(400)
    else:
        abort(400)


@app.route('/user', methods=['GET'])
def getUser():
    if request.method == "GET":
        return (userData(user.GIN_TOKEN), 200)
    else:
        abort(400)


@app.route('/execute', methods=['POST'])
def execute():

        if request.method == "POST":
                if configure(
                        repoName=request.json['repo'],
                        notifications=request.json['notifications'],
                        commitMessage=request.json['commitMessage'],
                        userInputs=list(filter(None, list(
                                request.json['userInputs'].values()))),
                        workflow=request.json['workflow'],
                        annexFiles=list(filter(None, list(
                                request.json['annexFiles'].values()))),
                        backPushFiles=list(filter(None, list(
                                request.json['backpushFiles'].values()))),
                        token=user.GIN_TOKEN,
                        username=user.username
                ):
                        return ("Success: workflow pushed to {}".format(
                                        request.json['repo']), 200)
                else:
                        return ("Workflow failed.", 400)
        else:
                return ("Wrong Method", 501)


@app.route('/repos', methods=['GET'])
@cross_origin()
def repos():
    if request.method == "GET":
        return jsonify([
                {'value': repo['name'], 'text': user.username + '/' + repo['name']}
                for repo in getRepos(user.username, user.GIN_TOKEN)
                ])

if __name__ == '__main__':
    app.run(debug=True, port=8000, host="0.0.0.0")