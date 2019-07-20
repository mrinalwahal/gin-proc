import requests
import os

def getToken():
	with open(".env", "r+") as env:
		for line in env.readlines():
			words = line.split("=")
			if words[0] == "token": token = words[1]

	env.close()
	print('Prepared for operation')
	return token

def designWorkflow(filename, repoPath):
	lines = []
	with open('Snakefile.template', 'r+') as template:
		for line in template.readlines():
			if not '#Add-Files' in line: lines.append(line)
			else:lines.append("SAMPLES = ['%s']" % filename)

	template.close()
	print("Files added to workflow: " + filename)

	with open(repoPath + '/Snakefile', 'w+') as config: config.writelines(lines)
	config.close()

	print("Workflow written at " + repoPath + "/Snakefile")

def designBackPush(filename, repoPath):
	lines = []
	with open('drone.template', 'r+') as template:
		for line in template.readlines():
			if not '# Break-Point' in line: lines.append(line)
			else :lines.append("    - git checkout master %s" % filename)

	template.close()
	print("Files added for back-push: " + filename)

	with open(repoPath + '/.drone.yml', 'w+') as config: config.writelines(lines)
	config.close()

	print("Configuration written at " + repoPath + "/.drone.yml")

def getRepo(name, API, token):
	data = requests.get(
		API + "/users/wahal/repos",
		headers = {
			'Authorization': 'token ' + token
		}
	).json()
	
	for repo in data:
		if repo['name'] == name: return repo

	print('Repo data fetched')

def clone(repo):
	clone_path = "clones/wahal-" + repo['name']
	if not os.path.exists(clone_path): os.makedirs(clone_path)
	os.system("git clone --depth=1 " + repo['clone_url'] + " " + clone_path)

	print("Repo cloned at " + clone_path)
	return clone_path

def clean(path):
	os.system("rm -rf " + path)
	print("Repo cleaned")

def push(repoPath):
	os.system('cd ' + repoPath + ' && git add . && git commit -m "Updated workflow" && git push origin master')
	print("Updates pushed")

def configure(path, repoName, workflowFile, backPushFile):
	API = "http://" + path + "/api/v1"

	token = getToken()
	repo = getRepo(repoName, API, token)
	clone_path = clone(repo)
	designWorkflow(workflowFile, clone_path)
	designBackPush(backPushFile, clone_path)
	push(clone_path)
	#clean(clone_path)
	print('\n[-] Ability to push the new CI config is yet to be added.')