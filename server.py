from flask import Flask, request, abort, render_template
import os
from main import configure

app = Flask(__name__)

@app.route('/')
def index(): return render_template('index.html')

@app.route('/hook', methods=['POST', 'GET'])
def hook():
    if request.method == 'POST':
        path = request.form['path']
        repo = request.form['repo']
        workflowFile = request.form['workflowFile']
        backPushFile = request.form['backPushFile']
        configure(path = path, repoName = repo, workflowFile = workflowFile, backPushFile = backPushFile)
        status = "done"
        return render_template('hook.html', repo = repo, workflowFile = workflowFile, backPushfile = backPushFile, status = status)
    else:
        abort(400)    

if __name__ == '__main__':
    app.run(debug=True)