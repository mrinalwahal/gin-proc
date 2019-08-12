# -------------------------------#
# Env variables assigned
# GIN_SERVER=http://172.19.0.2:3000
# DRONE_SERVER=http://172.19.0.3
# GIT_SSH_COMMAND=ssh -i gin-proc/ssh/gin_id_rsa
# -------------------------------#


import requests
import os
from shutil import rmtree
from datetime import datetime
import tempfile
import logging

from config import ensureConfig

from subprocess import call

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

GIN_ADDR = os.environ['GIN_SERVER']
DRONE_ADDR = os.environ['DRONE_SERVER']

PRIV_KEY = 'gin_id_rsa'
PUB_KEY = '{}.pub'.format(PRIV_KEY)
SSH_PATH = os.path.join(os.environ['HOME'], 'gin-proc', 'ssh')

if 'LOG_DIR' in os.environ:
    logging.basicConfig(
        filename=os.environ['LOG_DIR'],
        format="%(asctime)s:%(levelname)s:%(message)s",
        level=logging.DEBUG
        )


def log(function, message):

    if 'LOG_DIR' in os.environ:
        if function == 'warning':
            logging.warning(message)
        elif function == 'error':
            logging.error(message)
        elif function == 'critical':
            logging.critical(message)
        elif function == 'info':
            logging.info(message)
    else:
        print("{0}:{1}: {2}".format(function.upper(), datetime.now(), message))


def user(token):
    response = requests.get(
        GIN_ADDR + "/api/v1/user",
        headers={'Authorization': 'token ' + str(token)}
        ).json()

    return response


def ensureToken(username, password):

    res = requests.get(
        GIN_ADDR + "/api/v1/users/{}/tokens".format(username),
        auth=(username, password)).json()

    for token in res:
        if token['name'] == 'gin-proc':
            return token['sha1']

    res = requests.post(
        GIN_ADDR + "/api/v1/users/{}/tokens".format(username),
        auth=(username, password),
        data={'name': 'gin-proc'}
    ).json()

    return res['sha1']


def writeSecret(key, repo, user):

    requests.post(
        DRONE_ADDR + "/api/repos/{0}/{1}/secrets".format(user, repo),
        headers={'Authorization': 'Bearer ' + os.environ['DRONE_TOKEN']},
        data={
            'name': 'DRONE_PRIVATE_SSH_KEY',
            'data': key,
            'pull_request': False
            }
    )

    log('info', 'Key installed as secret in repo: {}'.format(repo))
    return True


def ensureSecret(user, repo):

    repos = requests.get(
        DRONE_ADDR + "/api/repos/{0}/{1}/secrets".format(user, repo),
        headers={'Authorization': 'Bearer ' + os.environ['DRONE_TOKEN']}
        )

    if repo not in [x['name'] for x in repos if x['active'] == 'true']:
        log('error', 'Repo {} not activated in Drone.'.format(repo))
        return False

    secrets = requests.get(
        DRONE_ADDR + "/api/repos/{0}/{1}/secrets".format(user, repo),
        headers={'Authorization': 'Bearer ' + os.environ['DRONE_TOKEN']}
        )

    for secret in secrets:
        if secret['name'] == 'DRONE_PRIVATE_SSH_KEY':
            log('info', 'Secret ensured in Drone for repo: {}'.format(repo))
            return True

    with open(os.path.join(SSH_PATH, PRIV_KEY), 'r') as key:
        if writeSecret(key, repo, user):
            return True
        else:
            return False


def ensureKeysOnServer(token):

    response = requests.get(
        GIN_ADDR + "/api/v1/user/keys",
        headers={'Authorization': 'token ' + token}
        )

    for keys in response.json():
        if keys['title'] == PRIV_KEY:
            return True


def ensureKeysOnLocal(path):

    return os.path.exists(os.path.join(path, PRIV_KEY))


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
            os.path.join(SSH_PATH, PRIV_KEY),
                'w+') as private_key_file:

            private_key_file.write(private_key.decode('utf-8'))

        with open(
            os.path.join(SSH_PATH, PUB_KEY),
                'w+') as public_key_file:

            public_key_file.write(public_key.decode('utf-8'))

        os.chmod(SSH_PATH, 0o700)
        os.chmod(os.path.join(SSH_PATH, PRIV_KEY), 0o600)
        os.chmod(os.path.join(SSH_PATH, PUB_KEY), 0o600)

        requests.post(
            GIN_ADDR + "/api/v1/user/keys",
            headers={'Authorization': 'token ' + token},
            data={'title': PRIV_KEY, 'key': public_key}
        )

        log('info', 'Fresh key pair installed with pub key {}'.format(PUB_KEY))
        return PUB_KEY


def ensureKeys(token):

    if ensureKeysOnServer(token) and ensureKeysOnLocal(SSH_PATH):
        log("info", "Keys ensured both on server and locally.")
        return True

    elif ensureKeysOnServer(token) and not ensureKeysOnLocal(SSH_PATH):
        log("info", "Key is installed on the server but not locally.")
        log(
            "critical",
            "Kindly delete your key online and try again."
            )

        return False

    elif not ensureKeysOnServer(token) and ensureKeysOnLocal(SSH_PATH):
        log("error", "Key is installed locally but not on the server.")
        log("warning", "Deleting key from local.")

        os.remove(os.path.join(SSH_PATH, PRIV_KEY))
        os.remove(os.path.join(SSH_PATH, PUB_KEY))
        log("info", "Removed local keys.")

        installFreshKeys(SSH_PATH, token)

        return True

    else:
        installFreshKeys(SSH_PATH, token)

        return True


def getRepos(user, token):
    res = requests.get(
        GIN_ADDR + "/api/v1/users/{}/repos".format(user),
        headers={'Authorization': 'token ' + token},
        ).json()

    return res


def getRepoData(user, repo, token):

    response = requests.get(
        GIN_ADDR + "/api/v1/repos/{0}/{1}".format(user, repo),
        headers={'Authorization': 'token ' + token}
        ).json()

    return response


def clone(repo, author, path):
    clone_path = os.path.join(path, author, repo['name'])
    os.makedirs(clone_path, exist_ok=True)

    call(['git', 'clone', '--depth=1', repo['clone_url'], clone_path])

    log("info", "Repo cloned at " + clone_path)
    return clone_path


def push(path, commitMessage):
    call(['git', 'add', '.'], cwd=path)
    call(['git', 'commit', '-m', commitMessage], cwd=path)
    call(['git', 'push'], cwd=path)

    log("info", "Updates pushed from {}".format(path))


def clean(path):

    try:
        rmtree(path)
        log("info", "Repo cleaned from {}".format(path))
        return True

    except Exception as e:
        log('error', e)
        log('critical', 'Exiting with errors.')
        return False


def configure(
        repoName,
        userInputs,
        backPushFiles,
        annexFiles,
        commitMessage,
        notifications,
        token,
        username,
        workflow
        ):

    repo = getRepoData(username, repoName, token)

    os.environ['GIT_SSH_COMMAND'] = "ssh -i " + \
        os.path.join(SSH_PATH, PRIV_KEY)

    if not ensureSecret(username, repoName):
        log('critical', "Couldn't ensure keys in Drone. Exiting.")
        return False

    with tempfile.TemporaryDirectory() as temp_clone_path:
        clone_path = clone(repo, username, temp_clone_path)
        ensureConfig(
            config_path=clone_path,
            workflow=workflow,
            commands=userInputs,
            annexFiles=annexFiles,
            backPushFiles=backPushFiles,
            notifications=notifications
            )
        push(clone_path, commitMessage)
        clean(clone_path)

        return True
