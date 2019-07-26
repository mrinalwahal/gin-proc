import os
from service import configure, authorize, ensureToken, ensureKeys, validUser, getRepos, user

from flask import Flask, request, abort, render_template, jsonify, make_response
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


auth = None
token = None


@app.route('/')
def index(): return render_template('index.html')


@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    if request.method == "POST":
        global auth
        auth = authorize(username=request.json['username'], password=request.json['password'])
        if not validUser(auth): abort(400)
        print("User {} logged in".format(request.json['username']))
        global token
        token = ensureToken(auth=auth)
        print('token ensured: {}'.format(token.name))
        # print('key ensured: {}'.format(ensureKeys(token, auth.username)))
        return ({'token': token.token}, 200)
    else:
        abort(400)


@app.route('/execute', methods=['POST'])
def execute():
                if request.method == "POST":
                        global auth
                        global token
                        configure(
                                repoName=request.json['repo'], 
                                commitMessage=request.json['commitMessage'],
                                workflowFiles=request.json['workflowFiles'],
                                annexFiles=request.json['annexFiles'],
                                backPushFiles=request.json['backpushFiles'],
                                token=token,
                                auth=auth
                        )
                        return ("Success: workflow pushed to {}".format(
                                        request.json['repo']), 200)
                else:
                        return ("Wrong Method", 501)


@app.route('/repos', methods=['GET'])
def repos():
    if request.method == "GET":
        return jsonify([repo.name for repo in getRepos(auth, auth.username)])

if __name__ == '__main__':
    app.run(debug=True, port=8000, host="0.0.0.0")