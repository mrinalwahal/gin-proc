from flask import Flask, request, abort, render_template
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

import os
from service import configure, authorize, ensureToken, ensureKeys, validUser, getRepos

auth = None
token = None

@app.route('/')
def index(): return render_template('index.html')

@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    if request.method == "POST":
        auth = authorize(username = request.json['username'], password = request.json['password'])
        if not validUser(auth): abort(400)
        print("User {} logged in".format(request.json['username']))
        token = ensureToken(auth = auth)
        print('token ensured: {}'.format(token.name))
        print('key ensured: {}'.format(ensureKeys(token)))
        return ("logged in", 200)
    else:
        abort(400)

@app.route('/hook', methods=['POST', 'GET'])
def hook():
    if request.method == 'POST':
        repo = request.form['repo']
        workflowFile = request.form['workflowFile']
        backPushFile = request.form['backPushFile']
        configure(repoName = repo, workflowFile = workflowFile, backPushFile = backPushFile, token = token, auth = auth)
        return render_template('hook.html', repo = repo, workflowFile = workflowFile, backPushfile = backPushFile, status = "Done")
    else:
        abort(400)    

@app.route('/repos', methods=['GET'])
def repos():
    if request.method == "GET": print(getRepos(auth, auth.username))

if __name__ == '__main__':
    app.run(debug=True, port=8000, host="127.0.0.1")