import os
<<<<<<< HEAD
from service import configure, ensureToken, ensureKeys, getRepos, user
=======
from service import configure, authorize, ensureToken, ensureKeys, validUser, getRepos, user
>>>>>>> 2e79cf169fdc3345ce863ac2426f531b4d28c04c

from flask import Flask, request, abort, render_template, jsonify, make_response
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


<<<<<<< HEAD
username = None
=======
auth = None
>>>>>>> 2e79cf169fdc3345ce863ac2426f531b4d28c04c
token = None


@app.route('/')
def index(): return render_template('index.html')


<<<<<<< HEAD
@app.route('/logout', methods=['POST'])
def logMeOut():

        if request.method == "POST":
                return ("logged out", 200)


=======
>>>>>>> 2e79cf169fdc3345ce863ac2426f531b4d28c04c
@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    if request.method == "POST":
<<<<<<< HEAD

        global username
        username = request.json['username']
        password = request.json['password']

        global token
        token = ensureToken(username, password)
        print('token ensured: {}'.format(token))
        # print('key ensured: {}'.format(ensureKeys(token, auth.username)))
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

=======
        global auth
        auth = authorize(username=request.json['username'], password=request.json['password'])
        if not validUser(auth): abort(400)
        print("User {} logged in".format(request.json['username']))
        global token
        token = ensureToken(auth=auth)
        print('token ensured: {}'.format(token.name))
        #print('key ensured: {}'.format(ensureKeys(token, auth.username)))
        return ({'token': token.token}, 200)
    else:
        abort(400)

"""@app.route('/user', methods=['GET'])
def user():
    if request.method == "GET":
        print (user(auth, auth.username))
"""
>>>>>>> 2e79cf169fdc3345ce863ac2426f531b4d28c04c

@app.route('/execute', methods=['POST'])
def execute():
                if request.method == "POST":
<<<<<<< HEAD
                        global username
                        global token
                        configure(
                                repoName=request.json['repo'],
                                notifications=request.json['notifications'],
                                commitMessage=request.json['commitMessage'],
=======
                        global auth
                        global token
                        configure(
                                repoName=request.json['repo'], 
                                commitMessage = request.json['commitMessage'],
>>>>>>> 2e79cf169fdc3345ce863ac2426f531b4d28c04c
                                workflowFiles=request.json['workflowFiles'],
                                annexFiles=request.json['annexFiles'],
                                backPushFiles=request.json['backpushFiles'],
                                token=token,
<<<<<<< HEAD
                                username=username
                        )
                        return ("Success: workflow pushed to {}".format(
                                        request.json['repo']), 200)
=======
                                auth=auth
                        )
                        return ("Success: workflow pushed to {}".format(request.json['repo']), 200)
>>>>>>> 2e79cf169fdc3345ce863ac2426f531b4d28c04c
                else:
                        return ("Wrong Method", 501)


@app.route('/repos', methods=['GET'])
<<<<<<< HEAD
@cross_origin()
def repos():
    if request.method == "GET":
        global username
        return jsonify([
                {'value': repo['name'], 'text': username + '/' + repo['name']}
                for repo in getRepos(username, token)
                ])
=======
def repos():
    if request.method == "GET":
        return jsonify([repo.name for repo in getRepos(auth, auth.username)])
>>>>>>> 2e79cf169fdc3345ce863ac2426f531b4d28c04c

if __name__ == '__main__':
    app.run(debug=True, port=8000, host="0.0.0.0")