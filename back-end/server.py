from service import configure, ensureToken, ensureKeys, getRepos, userData
from service import log, ensureSecrets
<<<<<<< HEAD
from flask import Flask, request, abort, jsonify, Blueprint

import errors

from flask_docs import ApiDoc
=======
from flask import Flask, request, abort, jsonify
>>>>>>> 46fa67413a76faef0722c635a6736ff918733d58

from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

<<<<<<< HEAD
app.config['API_DOC_MEMBER'] = ['api', 'platform', 'auth']

ApiDoc(app)

api = Blueprint('api', __name__)
auth = Blueprint('auth', __name__)
platform = Blueprint('platform', __name__)

=======
>>>>>>> 46fa67413a76faef0722c635a6736ff918733d58

class User(object):

    def __init__(self, *args, **kwargs):
        self.username = None
        self.GIN_TOKEN = None

    def login(self):

        self.username = request.json['username']
        password = request.json['password']

<<<<<<< HEAD
        try:
            self.GIN_TOKEN = ensureToken(user.username, password)
            log("debug", 'GIN token ensured.')

        except errors.ServerError as e:
            log('error', e)
            return (e, 500)

        if (
            ensureKeys(self.GIN_TOKEN) and ensureSecrets(self.username)
                ):
=======
        self.GIN_TOKEN = ensureToken(user.username, password)
        log("debug", 'GIN token ensured.')

        if ensureKeys(self.GIN_TOKEN) and ensureSecrets(self.username):
>>>>>>> 46fa67413a76faef0722c635a6736ff918733d58
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

<<<<<<< HEAD
        try:
            configure(
=======
        if configure(
>>>>>>> 46fa67413a76faef0722c635a6736ff918733d58
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
<<<<<<< HEAD
            )
            return ("Success: workflow pushed to {}".format(
                            request.json['repo']), 200)

        except errors.ServiceError as e:
            return (e, 400)
=======
        ):
            return ("Success: workflow pushed to {}".format(
                            request.json['repo']), 200)
        else:
            return ("Workflow failed.", 400)
>>>>>>> 46fa67413a76faef0722c635a6736ff918733d58

    def repos(self):

        return jsonify([
            {
                    'value': repo['name'],
                    'text': self.username + '/' + repo['name']
            }
            for repo in getRepos(self.username, self.GIN_TOKEN)
            ])

user = User()


<<<<<<< HEAD
@auth.route('/logout', methods=['POST'])
def logout():

    """
    Clears user's credentials including auth token for the session.
    """

=======
@app.route('/logout', methods=['POST'])
def logMeOut():
>>>>>>> 46fa67413a76faef0722c635a6736ff918733d58
    if request.method == "POST":
        return user.logout()


<<<<<<< HEAD
@auth.route('/login', methods=['POST'])
@cross_origin()
def login():

    """
    Authenticates user with their GIN credentials.

    @@@
    Ensures following checks in chronological order are passed for succesfull
    authentication:

     - #### Ensure Token
        Runs a check whether GIN already has a `personal access token (PAT)`
        installed on your account specifically for `gin-proc`.
        In case it doesnt (which is highly likely if you are logging in to
        `gin-proc` for the first time), it shall automatically create
        and install a fresh token for you.

     - #### Ensure SSH Keys
        Ensures whether a specific SSH key pair is already installed for use
        by `gin-proc` in GIN. In case it doesn't (which is highly likely if
        you are logging in to `gin-proc` for the first time),
        it shall create a fresh key pair for you and install the appropriate
        key `public key` in GIN so that gin-proc has read/write access to your GIN repos.

     - #### Ensure Drone Secrets
        Runs a check to ensure that all of your Drone repositories are
        activated and that they have your subsequent `private-key` installed
        in them as a **secret**. This secret is used by Drone for cloning and
        pushing operations on your GIN repos whilst its running your
        build jobs inside its runners.
    @@@
    """

=======
@app.route('/login', methods=['POST'])
@cross_origin()
def logMeIn():
>>>>>>> 46fa67413a76faef0722c635a6736ff918733d58
    if request.method == "POST":
        return user.login()
    else:
        abort(500)


<<<<<<< HEAD
@auth.route('/user', methods=['GET'])
def Get_User():

    """
    Returns logged-in user's data from GIN.
    """

=======
@app.route('/user', methods=['GET'])
def getUser():
>>>>>>> 46fa67413a76faef0722c635a6736ff918733d58
    if request.method == "GET":
        return user.details()
    else:
        abort(500)


<<<<<<< HEAD
@api.route('/execute', methods=['POST'])
@cross_origin()
def Execute_Workflow():

    """
    Runs the workflow post user's submission from front-end UI.

    @@@
    For complete documentation of execution steps, read
    [operations doc](https://github.com/G-Node/gin-proc/blob/master/docs/operations.md).
    @@@
    """
=======
@app.route('/execute', methods=['POST'])
def execute():
>>>>>>> 46fa67413a76faef0722c635a6736ff918733d58

    if request.method == "POST":
        return user.run(request)
    else:
        abort(500)


<<<<<<< HEAD
@api.route('/repos', methods=['GET'])
@cross_origin()
def repositories():

    """
    Returns list of user's repositories from GIN.
    """

    if request.method == "GET":
        return user.repos()


app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(platform, url_prefix='/platform')


=======
@app.route('/repos', methods=['GET'])
@cross_origin()
def repos():
    if request.method == "GET":
        return user.repos()

>>>>>>> 46fa67413a76faef0722c635a6736ff918733d58
if __name__ == '__main__':
    app.run(debug=True, port=8000, host="0.0.0.0")