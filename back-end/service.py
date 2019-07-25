#-------------------------------#
# Env variables assigned 
# GIN_SERVER=172.19.0.2:3000
# GIT_SSH_COMMAND=ssh -i gin-proc/ssh/gin_id_rsa
#-------------------------------#


import requests
import os
import gogs_client
import tempfile

from subprocess import call, Popen, PIPE

from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend

#print(os.environ['GIT_SSH_COMMAND'])
#print(os.environ['GIN_SERVER'])
path = "http://" + os.environ['GIN_SERVER']
api = gogs_client.GogsApi(path)

def user(auth, username):
	return api.get_user(auth, username)

def authorize(username, password):
    return gogs_client.UsernamePassword(username, password)

def ensureToken(auth):
    return api.ensure_token(auth, 'gin-proc')

def ensureKeys(token, user):
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

	SSH_PATH = "../ssh/" + user
	os.makedirs(SSH_PATH, exist_ok=True)

	with open(SSH_PATH + '/gin_id_rsa', 'w+') as private_key_file: 
		private_key_file.write(private_key.decode('utf-8'))
	with open(SSH_PATH + '/gin_id_rsa.pub', 'w+') as public_key_file: 
		public_key_file.write(public_key.decode('utf-8'))
	os.chmod(SSH_PATH, 0o700)
	os.chmod(SSH_PATH + '/gin_id_rsa', 0o600)
	os.chmod(SSH_PATH + '/gin_id_rsa.pub', 0o600)
	
	#os.environ['GIT_SSH_COMMAND'] = "ssh -i " + SSH_PATH + "/gin_id_rsa"

	response = requests.post(path + "/api/v1/user/keys", 
	headers = {'Authorization': 'token ' + str(token.token)},
	data = {'title': 'gin_id_rsa', 'key': public_key}
	)

	return 'gin_id_rsa'

def validUser(auth):
	return api.valid_authentication(auth)

def designWorkflow(files, repoPath):
	lines = []
	with open('../templates/Snakefile.template', 'r+') as template:
		for line in template.readlines():
			if not '#Add-Files' in line: lines.append(line)
			else:
				lines.append("SAMPLES = [{}]".format(','.join(files.values())))

	template.close()

	with open(repoPath + '/Snakefile', 'w+') as config: config.writelines(lines)
	config.close()

	print("Workflow written at " + repoPath + "/Snakefile")

def getAnnexedFiles(files, repoPath):
	lines = []
	with open('../templates/drone.template', 'r+') as template:
		for line in template.readlines():
			if not '#get-annexed-files' in line: lines.append(line)
			else:
				input_files = ""
				for filename in files.values():
					input_files += "'{}' ".format(filename)
				lines.append(("    #- git annex get {}").format(input_files))

	template.close()

	with open(repoPath + '/.drone.yml', 'w+') as config: config.writelines(lines)
	config.close()

	print("Annexed files pulling configuration added at " + repoPath + "/.drone.yml")

def designBackPush(files, repoPath):
	lines = []
	with open('../templates/drone.template', 'r+') as template:
		for line in template.readlines():
			if '#add-backpush-files' in line:
				input_files = ""
				for filename in files.values():
					input_files += "'{}' ".format(filename)
				lines.append(("    - mv {} '$TMPLOC'").format(input_files))
			elif '#copy-backpush-files' in line:
				input_files = "'$TMPLOC'/"
				for filename in files.values():
					input_files += "'{}' ".format(filename)
				lines.append(("    - mv {} '$DRONE_BUILD_NUMBER'/").format(input_files))
			else:
				 lines.append(line)				

	template.close()

	with open(repoPath + '/.drone.yml', 'w+') as config: config.writelines(lines)
	config.close()

	print("Configuration written at " + repoPath + "/.drone.yml")

def getRepos(auth, user):
	return api.get_user_repos(auth, user)

def getRepoData(auth, user, repo, token):

	"""
	response = requests.get(
		path + "/api/v1/repos/" + str(user) + "/" + str(repo), 
		headers = {'Authorization': 'token ' + str(token.token)}
		).json()
	print(response)
	"""
	return api.get_repo(auth, user, repo)

	print('Repo {} fetched'.format(repo))

def clone(repo, author, path):
	clone_path = path + "/{}-{}".format(author, repo.name)
	os.makedirs(clone_path, exist_ok=True)

	call(['git', 'clone', '--depth=1', repo.urls.clone_url, clone_path])
	#os.system("git clone --depth=1 " + repo.urls.clone_url + " " + clone_path)

	print("Repo cloned at " + clone_path)
	return clone_path

def clean(path):
	call(['rm', '-rf', path])
	#os.system("rm -rf " + path)
	print("Repo cleaned from {}".format(path))

def push(path):
	#call(['cd', path, '&& git add . && git commit -m "Updated workflow" && git push origin master'])
	os.system('cd ' + path + ' && git add . && git commit -m "Updated workflow" && git push origin master')
	print("Updates pushed from {}".format(path))

def configure(repoName, workflowFiles, backPushFiles, annexFiles, token, auth):
	repo = getRepoData(auth, auth.username, repoName, token)

	with tempfile.TemporaryDirectory() as temp_clone_path:
		clone_path = clone(repo, auth.username, temp_clone_path)
		designWorkflow(workflowFiles, clone_path)
		getAnnexedFiles(annexFiles, clone_path)
		designBackPush(backPushFiles, clone_path)
		push(clone_path)
		clean(clone_path)