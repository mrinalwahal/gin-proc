# -------------------------------#
# Env variables assigned
# GIN_SERVER=172.19.0.2:3000
# GIT_SSH_COMMAND=ssh -i gin-proc/ssh/gin_id_rsa
# -------------------------------#


import requests
import os
import tempfile

from subprocess import call

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

# print(os.environ['GIT_SSH_COMMAND'])
# print(os.environ['GIN_SERVER'])
path = "http://" + os.environ['GIN_SERVER']


def user(token):
    response = requests.get(
        path + "/api/v1/user",
        headers={'Authorization': 'token ' + str(token)}
        ).json()

    return response


def ensureToken(username, password):

    res = requests.get(
        path + "/api/v1/users/{}/tokens".format(username),
        auth=(username, password)).json()

    for token in res:
        if token['name'] == 'gin-proc':
            return token['sha1']

    res = requests.post(
        path + "/api/v1/users/{}/tokens".format(username),
        auth=(username, password),
        data={'name': 'gin-proc'}
    ).json()

    return res['sha1'] 


def ensureKeysOnServer(token):

    response = requests.get(
        path + "/api/v1/user/keys",
        headers={'Authorization': 'token ' + str(token.token)}
        )

    for keys in response.json():
        if keys['title'] == 'gin_id_rsa':

            print('Key {} installed on the server'.format('gin_id_rsa'))
            return (True)


def ensureKeysOnLocal(path):

    KEY_PATH = os.path.join(path, 'gin_id_rsa')
    EXISTS = os.path.exists(KEY_PATH)
    print('Key {} installed locally'.format('gin_id_rsa') is EXISTS)
    return EXISTS


def installFreshKeys(SSH_PATH, token):

        key = rsa.generate_private_key(
            backend=default_backend(),
            public_exponent=65537,
            key_size=2048
        )
        private_key = key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()
            )
        public_key = key.public_key().public_bytes(
            serialization.Encoding.OpenSSH,
            serialization.PublicFormat.OpenSSH
        )

        os.makedirs(SSH_PATH, exist_ok=True)

        with open(
            os.path.join(SSH_PATH, '/gin_id_rsa'),
                'w+') as private_key_file:

            private_key_file.write(private_key.decode('utf-8'))

        with open(
            os.path.join(SSH_PATH, '/gin_id_rsa.pub'),
                'w+') as public_key_file:

            public_key_file.write(public_key.decode('utf-8'))

        os.chmod(SSH_PATH, 0o700)
        os.chmod(SSH_PATH + '/gin_id_rsa', 0o600)
        os.chmod(SSH_PATH + '/gin_id_rsa.pub', 0o600)

        # os.environ['GIT_SSH_COMMAND'] = "ssh -i " + SSH_PATH + "/gin_id_rsa"

        requests.post(
            path + "/api/v1/user/keys",
            headers={'Authorization': 'token ' + str(token.token)},
            data={'title': 'gin_id_rsa', 'key': public_key}
        )

        print('Fresh Key pair installed with pub key {}'.format('gin_id_rsa'))
        return 'gin_id_rsa'


def ensureKeys(token):

    SSH_PATH = os.path.join('/gin-proc', 'ssh')

    if ensureKeysOnServer(token) and ensureKeysOnLocal(SSH_PATH):
        return True

    elif ensureKeysOnServer(token) and not ensureKeysOnLocal(SSH_PATH):
        print("Key {} is installed on the server but not locally. \
        Kindly delete your key online so we can install a fresh key pair.")

        return False

    elif not ensureKeysOnServer(token) and ensureKeysOnLocal(SSH_PATH):
        print("Key {} is installed locally but not on the server.")

        os.remove(os.path.join(SSH_PATH, 'gin_id_rsa'))
        os.remove(os.path.join(SSH_PATH, 'gin_id_rsa.pub'))
        print('Removed local keys.')

        installFreshKeys(SSH_PATH, token)

        print('Fresh keys installed both locally and on the server.')
        return True

    else:
        installFreshKeys(SSH_PATH, token)


def designWorkflow(files, repoPath):
    lines = []

    with open(
        os.path.join('templates', 'Snakefile.template'),
            'r+') as template:

        for line in template.readlines():
            if '#Add-Files' not in line: 
                lines.append(line)
            else:
                input_str = ""
                for filename in files.values():
                    input_str += "'{}',".format(filename)

                input_str = input_str[:-1]
                lines.append("SAMPLES = [{}]".format(input_str))

    template.close()

    with open(os.path.join(repoPath, 'Snakefile'), 'w+') as config: 
        config.writelines(lines)

    config.close()

    print("Workflow written at " + repoPath + "/Snakefile")


def addNotifications(lines, notifications):

    for notif in notifications:
        if notif['value']:
            if notif['name'] == "slack":
                print("notification detected: {}".format("slack"))
                with open(
                    os.path.join('templates', 'slack.template'),
                        'r+') as slack:

                        for notif_lines in slack:
                            lines.append(notif_lines)


def designCIConfig(notifications, backPushfiles, annexFiles, repoPath):
    lines = []

    with open(
        os.path.join('templates', 'drone.template'),
            'r+') as template:

        for line in template.readlines():

            if '#add-backpush-files' in line:
                if len(backPushfiles) > 0:
                    input_files = ""
                    for filename in backPushfiles.values():
                        input_files += "'{}' ".format(filename)
                    lines.append(('    - mv {} "$TMPLOC"').format(input_files))

            elif '#copy-backpush-files' in line:
                if len(backPushfiles) > 0:
                    input_files = ''
                    for filename in backPushfiles.values():
                        input_files += '"$TMPLOC"/"{}" '.format(filename)
                    lines.append('    - mv {} "$DRONE_BUILD_NUMBER"/'.format(
                        input_files))

            elif '#get-annexed-files' in line:
                if len(annexFiles.values()) == 0:
                    lines.append("    - git annex sync --content")
                else:
                    input_files = ""
                    for filename in annexFiles.values():
                        input_files += "'{}' ".format(filename)
                    lines.append('    - git annex get {}'.format(input_files))

            elif '#add-notifications' in line:
                addNotifications(lines, notifications)

            else:
                lines.append(line)

    template.close()

    with open(repoPath + '/.drone.yml', 'w+') as config:
        config.writelines(lines)

    config.close()

    print("Configuration written at " + repoPath + "/.drone.yml")


def getRepos(user, token):
    res = requests.get(
        path + "/api/v1/users/{}/repos".format(user),
        headers={'Authorization': 'token ' + str(token)},
        ).json()

    return res


def getRepoData(user, repo, token):

    response = requests.get(
        path + "/api/v1/repos/{0}/{1}".format(user, repo),
        headers={'Authorization': 'token ' + str(token)}
        ).json()

    return response


def clone(repo, author, path):
    clone_path = os.path.join(path, author, repo['name'])
    os.makedirs(clone_path, exist_ok=True)

    call(['git', 'clone', '--depth=1', repo['clone_url'], clone_path])

    print("Repo cloned at " + clone_path)
    return clone_path


def push(path, commitMessage):
    call(['git', 'add', '.'], cwd=path)
    call(['git', 'commit', '-m', commitMessage], cwd=path)
    call(['git', 'push'], cwd=path)

    print("Updates pushed from {}".format(path))


def clean(path):
    call(['rm', '-rf', path])

    print("Repo cleaned from {}".format(path))


def configure(
        repoName,
        workflowFiles,
        backPushFiles,
        annexFiles,
        commitMessage,
        notifications,
        token,
        username
        ):

    repo = getRepoData(username, repoName, token)

    with tempfile.TemporaryDirectory() as temp_clone_path:
        clone_path = clone(repo, username, temp_clone_path)
        designWorkflow(workflowFiles, clone_path)
        designCIConfig(notifications, backPushFiles, annexFiles, clone_path)
        push(clone_path, commitMessage)
        clean(clone_path)