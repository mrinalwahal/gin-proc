from flask import Flask, request, abort, render_template
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

import os
from main import configure
import gogs_client

path = "http://172.19.0.2:3000"
api = gogs_client.GogsApi(path)

auth = None
token = None

def authorize(username, password):
    return gogs_client.UsernamePassword(username, password)

def ensureToken(auth):
    return api.ensure_token(auth, 'gin-proc')

@app.route('/')
def index(): return render_template('index.html')

@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    if request.method == "POST":
        auth = authorize(username = request.json['username'], password = request.json['password'])
        if not api.valid_authentication(auth): abort(400)
        print("User {} logged in".format(request.json['username']))
        token = ensureToken(auth = auth)
        print('token ensured: {}'.format(token.name))
        return ("logged in", 200)
    else:
        abort(400)

@app.route('/hook', methods=['POST', 'GET'])
def hook():
    if request.method == 'POST':
        repo = request.form['repo']
        workflowFile = request.form['workflowFile']
        backPushFile = request.form['backPushFile']
        configure(path = path, repoName = repo, workflowFile = workflowFile, backPushFile = backPushFile, token = token, user = auth.username)
        return render_template('hook.html', repo = repo, workflowFile = workflowFile, backPushfile = backPushFile, status = "Done")
    else:
        abort(400)    

@app.route('/repos', methods=['GET'])
def repos():
    if request.method == "GET": print(api.get_user_repos(auth, auth.username))

if __name__ == '__main__':
    app.run(debug=True, port=8000, host="127.0.0.1")