#-------------------------------#
# Env variables assigned 
# GIN_SERVER=172.19.0.2:3000
# GIT_SSH_COMMAND=ssh -i gin-proc/ssh/gin_id_rsa
#-------------------------------#


import requests
import os
import gogs_client
import tempfile

from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend

#print(os.environ['GIT_SSH_COMMAND'])
#print(os.environ['GIN_SERVER'])

os.environ['GIT_SSH_COMMAND'] = "ssh -i ~/gin-proc/ssh/gin_id_rsa"

path = "http://" + os.environ['GIN_SERVER']
api = gogs_client.GogsApi(path)

def user(auth, username):
	return api.get_user(auth, username)

def authorize(username, password):
    return gogs_client.UsernamePassword(username, password)

def ensureToken(auth):
    return api.ensure_token(auth, 'gin-proc')

def ensureKeys(token):
	response = requests.get(path + "/api/v1/user/keys", headers = {'Authorization': 'token ' + str(token.token)})
	for keys in response.json():
		if keys['title'] == 'gin_id_rsa': return 'gin_id_rsa'
	
	key = rsa.generate_private_key(
    backend=crypto_default_backend(),
    public_exponent=65537,
    key_size=2048
	)
	private_key = key.private_bytes(
    crypto_serialization.Encoding.PEM,
    crypto_serialization.PrivateFormat.PKCS8,
    crypto_serialization.NoEncryption())
	public_key = key.public_key().public_bytes(
    crypto_serialization.Encoding.OpenSSH,
    crypto_serialization.PublicFormat.OpenSSH
	)

	os.makedirs("~/gin-proc/ssh", exist_ok=True)
	with open('~/gin-proc/ssh/gin_id_rsa', 'w+') as private_key_file: 
		private_key_file.write(private_key.decode('utf-8'))
	with open('~/gin-proc/ssh/gin_id_rsa.pub', 'w+') as public_key_file: 
		public_key_file.write(public_key.decode('utf-8'))
	os.chmod('~/gin-proc/ssh', 0o700)
	os.chmod('~/gin-proc/ssh/gin_id_rsa', 0o600)
	os.chmod('~/gin-proc/ssh/gin_id_rsa.pub', 0o600)
	
	response = requests.post(path + "/api/v1/user/keys", 
	headers = {'Authorization': 'token ' + str(token.token)},
	data = {'title': 'gin_id_rsa', 'key': public_key}
	)

	return 'gin_id_rsa'

def validUser(auth):
	return api.valid_authentication(auth)

def designWorkflow(files, repoPath):
	lines = []
	with open('Snakefile.template', 'r+') as template:
		for line in template.readlines():
			if not '#Add-Files' in line: lines.append(line)
			else: lines.append("SAMPLES = {}".format(files.values()))

	template.close()
	print("Files added to workflow: " + files.values())

	with open(repoPath + '/Snakefile', 'w+') as config: config.writelines(lines)
	config.close()

	print("Workflow written at " + repoPath + "/Snakefile")

def designBackPush(files, repoPath):
	lines = []
	with open('drone.template', 'r+') as template:
		for line in template.readlines():
			if not '# Break-Point' in line: lines.append(line)
			else:
				for filename in files.values(): lines.append("    - git checkout master --files {}".format(filename))

	template.close()
	print("Files added for back-push: " + files.values())

	with open(repoPath + '/.drone.yml', 'w+') as config: config.writelines(lines)
	config.close()

	print("Configuration written at " + repoPath + "/.drone.yml")

def getRepos(auth, user):
	return api.get_user_repos(auth, user)

def getRepoData(auth, user, repo):
	return api.get_repo(auth, user, repo)

	print('Repo {} fetched'.format(repo))

def clone(repo, author, path):
	clone_path = path + "/{}-{}".format(author, repo.name)
	os.makedirs(clone_path, exist_ok=True)
	os.system("git clone --depth=1 " + repo.urls.clone_url + " " + clone_path)

	print("Repo cloned at " + clone_path)
	return clone_path

def clean(path):
	os.system("rm -rf " + path)
	print("Repo cleaned from {}".format(path))

def push(path):
	os.system('cd ' + path + ' && git add . && git commit -m "Updated workflow" && git push origin master')
	print("Updates pushed from {}".format(path))

def configure(repoName, commitMessage, workflowFiles, backPushFiles, token, auth):
	repo = getRepoData(auth, auth.username, repoName)

	with tempfile.TemporaryDirectory() as temp_clone_path:
		clone_path = clone(repo, auth.username, temp_clone_path)
		designWorkflow(workflowFiles, clone_path)
		designBackPush(backPushFiles, clone_path)
		push(clone_path)
		clean(clone_path)