# -------------------------------#
# Env variables assigned
# export GIN_SERVER=http://172.19.0.2:3000
# export DRONE_SERVER=http://172.19.0.3
# DRONE_TOKEN=AAAAAAAAAA000000000000000XXXXXXXXX
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

    LOG = True
    FILENAME = os.environ['LOG_DIR']
    FORMAT = "%(asctime)s:%(levelname)s:%(message)s"

    if 'DEBUG' in os.environ and os.environ['DEBUG']:
        LEVEL = logging.DEBUG
    else:
        LEVEL = logging.INFO

    logging.basicConfig(
        filename=FILENAME,
        format=FORMAT,
        level=LEVEL
        )

else:
    LOG = False


def log(function, message):

    if LOG:
        if function == 'warning':
            logging.warning(message)
        elif function == 'error':
            logging.error(message)
        elif function == 'critical':
            logging.critical(message)
        elif function == 'info':
            logging.info(message)
        elif function == 'exception':
            logging.exception(message)
    else:
        print("{1}: [{0}] {2}".format(
            function.upper(),
            datetime.now(),
            message)
            )


def userData(token):

    return requests.get(
        GIN_ADDR + "/api/v1/user",
        headers={'Authorization': 'token {}'.format(token)}
        ).json()


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

    res = requests.post(
        DRONE_ADDR + "/api/repos/{0}/{1}/secrets".format(user, repo),
        headers={
            'Authorization': 'Bearer {}'.format(os.environ['DRONE_TOKEN']),
            'Content-Type': "application/json"
            },
        json={
            "name": "DRONE_PRIVATE_SSH_KEY",
            "data": key,
            "pull_request": False
            }
    )

    if res.status_code == 200:
        log('debug', 'Secret installed in `{}`'.format(repo))
        return True
    else:
        log('warning', 'Secret could not be installed in `{}`'.format(repo))
        log('critical', res.json()['message'])
        return False


def updateSecret(secret, data, user, repo):

    res = requests.patch(
        DRONE_ADDR + "/api/repos/{user}/{repo}/secrets/{secret}".format(
            user=user,
            repo=repo,
            secret=secret),
        headers={'Authorization': 'Bearer ' + os.environ['DRONE_TOKEN']},
        json={
            "data": data,
            "pull_request": False
        })

    if res.status_code == 200:
        log('debug', 'Secret updated in `{}`'.format(repo))
        return True
    else:
        log('warning', 'Secret could not be updated in `{}`'.format(repo))
        log('critical', 'Execution may not work properly from here.')
        return False


def ensureSecrets(user):

    repos = requests.get(
        DRONE_ADDR + "/api/user/repos",
        headers={
            'Authorization': 'Bearer {}'.format(os.environ['DRONE_TOKEN'])
            }).json()

    for repo in repos:
        if not repo['active']:

            log('debug', 'Repo {} is not activated in Drone.'.format(repo))

            install_request = requests.post(
                DRONE_ADDR + "/api/repos/{owner}/{name}".format(
                    owner=user, name=repo),
                headers={
                    'Authorization': 'Bearer {}'.format(
                        os.environ['DRONE_TOKEN'])
                    })

            if install_request.status_code == 200:
                log('info', "Activated `{}`".format(repo))
            else:
                log('critical',
                    "Drone didn't respond for activation of `{}`".format(
                        repo))

        secrets = requests.get(
            DRONE_ADDR + "/api/repos/{0}/{1}/secrets".format(user, repo),
            headers={'Authorization': 'Bearer {}'.format(
                os.environ['DRONE_TOKEN'])}
            ).json()

        with open(os.path.join(SSH_PATH, PRIV_KEY), 'r') as key:

            for secret in secrets:
                if secret['name'] == 'DRONE_PRIVATE_SSH_KEY':
                    log('debug', 'Secret found in repo `{}`'.format(
                        repo))

                    return updateSecret(
                        secret=secret['name'],
                        data=key.read(),
                        repo=repo,
                        user=user
                    )
                else:
                    return(writeSecret(key.read(), repo, user))

            log('debug', 'Secret not found in `{}`'.format(repo))
            return(writeSecret(key.read(), repo, user))


def getKeysFromServer(token):

    return requests.get(
        GIN_ADDR + "/api/v1/user/keys",
        headers={'Authorization': 'token {}'.format(token)}
        ).json()


def ensureKeysOnServer(token):

    for key in getKeysFromServer(token):
        if key['title'] == PRIV_KEY:
            return True


def deleteKeysOnServer(token):

    for key in getKeysFromServer(token):
        if key['title'] == PRIV_KEY:
            response = requests.delete(
                key['url'],
                headers={'Authorization': 'token {}'.format(token)}
                )

            if response.status_code == 204:
                log('warning', 'Deleted keys from server.')
            else:
                log('error', response.text)
                log('critical',
                    "You'll have to manually delete the keys from the server.")

    return


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

    try:
        if ensureKeysOnServer(token) and ensureKeysOnLocal(SSH_PATH):
            log("debug", "Keys ensured both on server and locally.")

        elif ensureKeysOnServer(token) and not ensureKeysOnLocal(SSH_PATH):
            log("debug", "Key is installed on the server but not locally.")

            deleteKeysOnServer(token)
            installFreshKeys(SSH_PATH, token)

        elif not ensureKeysOnServer(token) and ensureKeysOnLocal(SSH_PATH):
            log("debug", "Key is installed locally but not on the server.")

            os.remove(os.path.join(SSH_PATH, PRIV_KEY))
            os.remove(os.path.join(SSH_PATH, PUB_KEY))
            log("warning", "Removed local keys.")

            installFreshKeys(SSH_PATH, token)

        else:
            installFreshKeys(SSH_PATH, token)

        return True

    except Exception as e:
        log('exception', e)
        return False


def getRepos(user, token):

    return requests.get(
        GIN_ADDR + "/api/v1/users/{}/repos".format(user),
        headers={'Authorization': 'token {}'.format(token)},
        ).json()


def getRepoData(user, repo, token):

    return requests.get(
        GIN_ADDR + "/api/v1/repos/{0}/{1}".format(user, repo),
        headers={'Authorization': 'token {}'.format(token)}
        ).json()


def clone(repo, author, path):
    clone_path = os.path.join(path, author, repo['name'])
    os.makedirs(clone_path, exist_ok=True)

    call(['git', 'clone', '--depth=1', repo['clone_url'], clone_path])

    log("debug", "Repo cloned at " + clone_path)
    return clone_path


def push(path, commitMessage):

    try:
        call(['git', 'add', '.'], cwd=path)
        call(['git', 'commit', '-m', commitMessage], cwd=path)
        call(['git', 'push'], cwd=path)

        log("info", "Updates pushed from {}".format(path))
        return True

    except Exception as e:
        log('critical', e)
        return False


def clean(path):

    try:
        rmtree(path)
        log("debug", "Repo cleaned from {}".format(path))
        return True

    except Exception as e:
        log('critical', e)
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

    os.environ['GIT_SSH_COMMAND'] = "ssh -i {}".format(
       os.path.join(SSH_PATH, PRIV_KEY))

    STATUS = False

    with tempfile.TemporaryDirectory() as temp_clone_path:
        clone_path = clone(repo, username, temp_clone_path)

        try:
            if ensureConfig(
                config_path=clone_path,
                workflow=workflow,
                commands=userInputs,
                annexFiles=annexFiles,
                backPushFiles=backPushFiles,
                notifications=notifications
            ):
                STATUS = True

        except Exception as e:
            log('exception', e)

        finally:
            push(clone_path, commitMessage)
            clean(clone_path)

    return STATUS