from service import configure, ensureToken, ensureKeys, getRepos, userData
from service import log, ensureSecrets
from flask import Flask, request, abort, jsonify

from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


class User(object):

        def __init__(self, *args, **kwargs):
                self.username = None
                self.GIN_TOKEN = None

        def login(self):

                self.username = request.json['username']
                password = request.json['password']

                self.GIN_TOKEN = ensureToken(user.username, password)
                log("debug", 'GIN token ensured.')

                if ensureKeys(self.GIN_TOKEN) and ensureSecrets(self.username):
                        return ({'token': self.GIN_TOKEN}, 200)
                else:
                        return ('login failed', 400)

        def logout(self):
                user.username = None
                user.GIN_TOKEN = None
                user.DRONE_TOKEN = None

                return ("logged out", 200)

        def details(self):
                return (userData(self.GIN_TOKEN), 200)

        def run(self, request):

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
                        token=self.GIN_TOKEN,
                        username=self.username
                ):
                        return ("Success: workflow pushed to {}".format(
                                        request.json['repo']), 200)
                else:
                        return ("Workflow failed.", 400)

        def repos(self):

                return jsonify([
                        {
                                'value': repo['name'],
                                'text': self.username + '/' + repo['name']
                        }
                        for repo in getRepos(self.username, self.GIN_TOKEN)
                        ])

user = User()


@app.route('/logout', methods=['POST'])
def logMeOut():
    if request.method == "POST":
            return user.logout()


@app.route('/login', methods=['POST'])
@cross_origin()
def logMeIn():
        if request.method == "POST":
                return user.login()
        else:
                abort(500)


@app.route('/user', methods=['GET'])
def getUser():
    if request.method == "GET":
            return user.details()
    else:
        abort(500)


@app.route('/execute', methods=['POST'])
def execute():

        if request.method == "POST":
                return user.run(request)
        else:
                abort(500)


@app.route('/repos', methods=['GET'])
@cross_origin()
def repos():
    if request.method == "GET":
        return user.repos()

if __name__ == '__main__':
    app.run(debug=True, port=8000, host="0.0.0.0")