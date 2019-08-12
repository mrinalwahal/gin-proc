import os, sys
import yaml

from service import log


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


def join_files(files, location=None):

    s = ''
    for filename in files:
        if location:
            s += "'{0}'/'{1}'".format(location, filename)
        else:
            s += "'{}'".format(filename)

    return s


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

    return commands


def addAnnex(files, commands):

    if len(files) > 0:
        input_files = join_files(files)

        commands.append('git annex init "$DRONE_REPO_NAME"-drone-annexe')
        commands.append("git annex get {}".format(input_files))

    return commands


def createWorkflow(workflow, commands, user_commands=None):

    if workflow == 'snakemake':
        if user_commands:
            commands.append('cd ' + user_commands + ' && snakemake')
        else:
            commands.append('snakemake')
    else:
        for command in user_commands:
            commands.append(command)

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

        log("info", "Writing fresh configuration.")

        data = {
            'kind': 'pipeline',
            'name': 'gin-proc',

            'clone': {
                'disable': 'true'
            },

            'steps': [
                createStep(
                    name='execute',
                    image='falconshock/gin-proc:micro-test',
                    volumes=[createVolume('repo', '/repo')],
                    environment=[createEnv('SSH_KEY', 'DRONE_PRIVATE_SSH_KEY')],
                    commands=[
                        'eval $(ssh-agent -s)',
                        'mkdir -p /root/.ssh && echo "$SSH_KEY" > \
/root/.ssh/id_rsa && chmod 0600 /root/.ssh/id_rsa',
                        'mkdir -p /etc/ssh',
                        'echo "StrictHostKeyChecking no" >> \
/etc/ssh/ssh_config',
                        'ssh-add /root/.ssh/id_rsa',
                        'ssh-keyscan -t rsa "$DRONE_GOGS_SERVER" > \
/root/.ssh/authorized_keys'
                        'git clone "$DRONE_GIT_SSH_URL"',
                        'cd "$DRONE_REPO_NAME"/',
                        'pip3 install -r requirements.txt',
                    ]
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

        log("info", "Configuration complete.")

        return data

    except Exception as e:
        log('error', e)
        log('info', 'Make a re-attempt.')


def modifyConfigFiles(
        data,
        annexFiles,
        workflow,
        backPushFiles,
        commands
        ):

    try:
        log("info", "Adding user's files.")

        data = addAnnex(annexFiles, data)

        data = createWorkflow(workflow, data, commands)

        data = addBackPush(backPushFiles, data)

        return data

    except Exception as e:
        log('error', e)
        log('info', 'Make a re-attempt.')


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
        if not os.path.exists(os.path.join(config_path, '.drone.yml')):
            log("warning", "CI Configuration file not found in repo.")

            with open(os.path.join(config_path, '.drone.yml'), 'w') \
                    as new_config:

                yaml.dump(
                    generateConfig(
                        workflow=workflow,
                        commands=commands,
                        annexFiles=annexFiles,
                        backPushFiles=backPushFiles,
                        notifications=notifications
                        ),
                    new_config,
                    default_flow_style=False)

            return True

        else:
            log("info", "CI Configuration exists in repo.")

            config = []

            with open(os.path.join(config_path, '.drone.yml'), 'r') as stream:
                config = yaml.load(stream, Loader=yaml.FullLoader)

            with open(os.path.join(config_path, '.drone.yml'), 'w') as stream:
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
        print(str(e))