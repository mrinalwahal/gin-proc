import os
import yaml
import logging

from datetime import datetime

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


def createVolume(name, path):

    return {'name': name, 'path': path}


def createEnv(name, secret):

    return {name: {'from_secret': secret}}


def createStep(
        name,
        image,
        volumes=None,
        settings=None,
        environment=None,
        commands=None
        ):

    PAYLOAD = {}
    PAYLOAD['name'] = name
    PAYLOAD['image'] = image
    if volumes:
        PAYLOAD['volumes'] = volumes
    if settings:
        PAYLOAD['settings'] = settings
    if environment:
        PAYLOAD['environment'] = environment
    if commands:
        PAYLOAD['commands'] = commands

    return PAYLOAD


def join_files(files, location=''):

    return ' '.join(
        '"{}"'.format(
            os.path.join(location, filename)) for filename in files)


def addBackPush(files, commands):

    if len(files) > 0:
        input_files = join_files(files)

        commands.append('TMPLOC=`mktemp -d`')
        commands.append(('mv {} "$TMPLOC"').format(input_files))

        commands.append('git checkout gin-proc || git checkout -b gin-proc')
        commands.append('git reset --hard')
        commands.append('mkdir "$DRONE_BUILD_NUMBER"')

        input_files = join_files(files, "$TMPLOC")

        commands.append('mv {} "$DRONE_BUILD_NUMBER"/'.format(
            input_files))

        commands.append('git add "$DRONE_BUILD_NUMBER"/')
        commands.append('git commit "$DRONE_BUILD_NUMBER"/ -m "Back-Push"')
        commands.append('git push origin gin-proc')
        commands.append('git annex copy --to=origin --all')

    return commands


def addAnnex(files, commands):

    try:
        if len(files) > 0:
            input_files = join_files(files)

            commands.append('git annex init "$DRONE_REPO_NAME"-drone-annexe')
            commands.append("git annex get {}".format(input_files))

    except Exception as e:
        log('exception', e)

    finally:
        return commands


def createWorkflow(workflow, commands, user_commands=None):

    try:
        if workflow == 'snakemake':
            if user_commands:
                commands.append('snakemake --snakefile {}/snakefile'.format(
                    user_commands[0]))
            else:
                commands.append('snakemake')
        else:
            for command in user_commands:
                commands.append(command)

    except Exception as e:
        log('exception', e)

    finally:
        return commands


def integrateVolumes(volumes):

    PAYLOAD = []

    for volume in volumes:
        PAYLOAD.append(
            {
                'name': volume[0],
                'host': {'path': volume[1]}
            }
        )

    return PAYLOAD


def generateConfig(
        workflow,
        commands,
        annexFiles,
        backPushFiles,
        notifications
        ):

    try:

        log("debug", "Writing fresh configuration.")

        data = {
            'kind': 'pipeline',
            'name': 'gin-proc',

            'clone': {
                'disable': True
            },

            'steps': [
                createStep(
                    name='restore-cache',
                    image='drillster/drone-volume-cache',
                    volumes=[createVolume('cache', '/cache')],
                    settings={
                        'restore': True,
                        'mount': '/drone/src/.snakemake'
                        },
                ),
                createStep(
                    name='execute',
                    image='falconshock/gin-proc:micro-test',
                    volumes=[createVolume('repo', '/repo')],
                    environment=createEnv(
                        'SSH_KEY',
                        'DRONE_PRIVATE_SSH_KEY'
                        ),
                    commands=[
                        'eval $(ssh-agent -s)',
                        'mkdir -p /root/.ssh && echo "$SSH_KEY" > \
/root/.ssh/id_rsa && chmod 0600 /root/.ssh/id_rsa',
                        'mkdir -p /etc/ssh',
                        'echo "StrictHostKeyChecking no" >> \
/etc/ssh/ssh_config',
                        'ssh-add /root/.ssh/id_rsa',
                        'ssh-keyscan -t rsa "$DRONE_GOGS_SERVER" > \
/root/.ssh/authorized_keys',
                        'git clone "$DRONE_GIT_SSH_URL"',
                        'cd "$DRONE_REPO_NAME"/',
                        'pip3 install -r requirements.txt',
                    ]
                ),
                createStep(
                    name='rebuild-cache',
                    image='drillster/drone-volume-cache',
                    volumes=[createVolume('cache', '/cache')],
                    settings={
                        'rebuild': True,
                        'mount': '/drone/src/.snakemake'
                        },
                ),
            ],
            'volumes': integrateVolumes([
                ('cache', '/gin-proc/cache'),
                ('repo', '/gin-proc/repo')
                ]),
            'trigger': {
                'branch': ['master'],
                'event': ['push'],
                'status': ['success']
            }
        }

        data['steps'][0]['commands'] = modifyConfigFiles(
            workflow=workflow,
            annexFiles=annexFiles,
            backPushFiles=backPushFiles,
            commands=commands,
            data=data['steps'][0]['commands']
        )

        data['steps'] = addNotifications(
            notifications=notifications,
            data=data['steps']
        )

        log("debug", "Configuration complete.")

        return data

    except Exception as e:
        log('exception', e)
        return False


def modifyConfigFiles(
        data,
        annexFiles,
        workflow,
        backPushFiles,
        commands
        ):

    try:
        log("debug", "Adding user's files.")

        data = addAnnex(annexFiles, data)

        data = createWorkflow(workflow, data, commands)

        data = addBackPush(backPushFiles, data)

        return data

    except Exception as e:
        log('exception', e)


def addNotifications(notifications, data):

    notifications = [n for n in notifications if n['value']]

    for notification in notifications:
        if notification['name'] == 'Slack':

            log("info", "Adding notification: {}".format(notification['name']))

            data.append(
                createStep(
                    name='notification',
                    image='plugins/slack',
                    settings={
                        'webhook': """
https://hooks.slack.com/services/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
"""
                    }
                )
            )

    return data


def ensureConfig(
        config_path,
        commands,
        workflow='snakemake',
        annexFiles=[],
        backPushFiles=[],
        notifications=[]
        ):

    try:
        __file = os.path.join(config_path, '.drone.yml')
        if not os.path.exists(__file) or os.path.getsize(__file) <= 0:
            log("warning", "CI Config either not found in repo or is corrupt.")

            with open(os.path.join(config_path, '.drone.yml'), 'w') \
                    as new_config:
                __generated_config = generateConfig(
                        workflow=workflow,
                        commands=commands,
                        annexFiles=annexFiles,
                        backPushFiles=backPushFiles,
                        notifications=notifications
                        )

                if not __generated_config:
                    return False
                else:
                    yaml.dump(
                        __generated_config,
                        new_config,
                        default_flow_style=False)

            return True

        else:
            __file = os.path.join(config_path, '.drone.yml')
            print(type(__file))

            log("debug", "Updating already existing CI Configuration.")

            config = []
            with open(__file, 'r') as stream:
                config = yaml.load(stream, Loader=yaml.FullLoader)

            with open(__file, 'w') as stream:

                config['steps'][0]['commands'] = modifyConfigFiles(
                    workflow=workflow,
                    annexFiles=annexFiles,
                    backPushFiles=backPushFiles,
                    commands=commands,
                    data=config['steps'][0]['commands'][:9]
                )

                config['steps'] = addNotifications(
                    notifications=notifications,
                    data=config['steps']
                )

                yaml.dump(
                    config,
                    stream,
                    default_flow_style=False)

            return True

    except Exception as e:
        log('exception', e)
