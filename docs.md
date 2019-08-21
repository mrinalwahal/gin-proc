### Documentation

[Initial work similar to README]

## Table of Contents
* **[Introduction]()**
  - [Problem statement](#problem)
  - [Rationale and Significance](#rationale)
* **[Installation](#install)**
  - [GIN's hosted cloud](#cloud)
  - [Local environment](#local)
    - [Docker Compose](#docker-compose)
    - [Manual](#manual)
* **[Usage](#usage)**
  - [Workflows](#workflows)
  - [User's Files](#files)
* **[Operations](#operations)**
  - [After Login](#after-login)
  - [API](#api)
  - [Inside Pipeline](#pipeline)
* **[FAQ](#questions)**
* **[License](#project-license)**

<br>

<a name="install"></a>
## Installation

<a name="cloud"></a>
### GIN's Hosted Cloud

We are currently deploying the utility for our cloud environment. Please check back after some time.

<a name="local"></a>
### Local Environment (D-I-Y)

<br>

<a name="docker-compose"></a>
#### Docker Compose

You can simply run `the docker-compose` file included in the repositoy which is configured to run all the 3 services := GIN, Drone and gin-proc for you.

<a name="manual"></a>
#### Manual Set-Up

Use the following tutorial to st up all 3 containers separately.

**Prerequisites**

* [Docker](https://docs.docker.com/)
* [g-node/gin-web](https://hub.docker.com/r/gnode/gin-web) node running in a docker container. If you don't have this then folow steps until [#install-gin](#install-gin)

It's advisable to use all the **gin micro-services** inside docker containers and further connect all containers to interact with each other for increased fault tolerance.

<br>

**Steps**

<a name="create-network"></a>
**[1]** In order to allow all gin containers to interact with each other, create a **docker network** and connect all containers to this network.

`docker network create <docker-network-name>`

**[2]** If you already have a **gin** service container running, then attach it to the new network.

`docker network connect <docker-network-name> <gin-container-name>`

<a name="install-gin"></a>
**Or** if you do not have a **gin** service container running already, then start a new one with the following command.
To keep things easier, we'll attach a static IP `172.19.0.2` to this container so that we don't have to inspect the docker network for changes in IP later.

`docker run --name=gin --net <network-name> --ip 172.19.0.2 -p 10022:22 -p 3000:3000 -v /var/gogs:/data gnode/gin-web:rebased`

If you already had a gin container running, then run the following command to check and copy IP address of **gin** service container.

`docker network inspect <network-name>`

Copy the IP of your GIN container from `containers` section.

**[3]** Set-up GIN Service.

If you have already set-up a gin container previuosly, then create a custom configuration file ([check GOGS docs for custom config](https://gogs.io/docs/features/custom_template)) with the following details.

<a name="config"></a>
```
DOMAIN           = 172.19.0.2
HTTP_PORT        = 3000
ROOT_URL         = http://172.19.0.2:3000/
```

Keep everything else the same.

If you have set-up the gin service for the first time through this tutorial, then access `172.19.0.2:3000` in your browser. You will be treated with the configuration page.

Mention the same config details as [above](#config) and leave everything else the same.

Save the details. Register for a new account and login.

**[4]** Create your first repository on the gin service. Clone the repository anywhere on your machine.

**[5]** Create **drone** CI/CD service container.

```
docker run --volume=/var/run/docker.sock:/var/run/docker.sock --volume=/gin-proc/cache:/cache --volume=/gin-proc/ssh:/ssh --env=DRONE_GIT_ALWAYS_AUTH=false  --env=DRONE_GOGS_SERVER=http://172.19.0.2:3000 --env=DRONE_RUNNER_CAPACITY=2 --env=DRONE_RUNNER_NETWORKS=gin --env=DRONE_SERVER_HOST=172.19.0.3 --env=DRONE_SERVER_PROTO=http --env=DRONE_TLS_AUTOCERT=false --publish=80:80 --publish=443:443 --publish=2224:22 --restart=always  --detach=true --net gin --name=drone drone/drone:latest
 ```

Access drone at `172.19.0.3:80` in your browser.

**[6]** Create **gin-proc** service.

```
docker run --net gin --name=gin-proc gnode/proc:<version>
```

**Additional Environment Variables**

`DEBUG=True` - Serves log messages from the lowest DEBUG level i.e. DEBUG, INFO, WARNING, ERROR, EXCEPTION.

`DEBUG=False` or simply, not assigning the var - Servers log messages from and above INFO level i.e. INFO, WARNING, ERROR, EXCEPTION.

`LOG_DIR=/path/to/your/log/dir` - Specific location to store your logs in. Otherwise, the logs are simply printed on your console in real time.

<br>

<a name="usage"></a>
## Usage

Go to your `gin-proc` address on port 3000 to access the service UI. Only use your GIN credentials to login. Users are not required to signup separately for `gin-proc`.

<a name="workflows"></a>
### Types of Workflows

**Snakemake** - If you choose this workflow, you can enter the location of your Snakefile in your repo. If nothing is mentioned in location on during submission, then default location will be assumed to be the root of the repository.

**Custom** - Users can enter the exact commands they want to run inside containers post cloning of the repository. Commands will be executed in the same exact order they are added to the workflow in.

<a name="files"></a>
### User's files

**Annex Files** - Users can mention whether any files have to be especially `git-annex`ed before executing the workflow.

**BackPush Files** - Users can mention the output files produced post execution of the workflow to be pushed back to user's GIN repository. Files will be pushed to a separate `gin-proc` branch in the repository.

<br>

<a name="operations"></a>
## Operations

<a name="after-login"></a>
#### What happens just after you Log-In

`gin-proc` does following operations for you in the background, in chronological order.

**+** When you first log into the front-end, the microservice automatically logs into your GIN account whith your specified credentials.

**+** It then runs a check whether GIN already has a `personal access token (PAT)` installed on your account specifically for `gin-proc`. In case it doesnt (which is highly likely if you are logging in to `gin-proc` for the first time), it shall automatically create and install a fresh token for you.

**+** Immediately after that it ensures whether a specific SSH key pair is already installed for use by `gin-proc` in GIN. In case it doesn't (which is highly likely if you are logging in to `gin-proc` for the first time), it shall create a fresh key pair for you and install the appropriate key `public key` in GIN so that gin-proc has read/write access to your GIN repos.

**+** Then `gin-proc` runs a check to ensure that all of your Drone repositories are activated and that they have your subsequent `private-key` installed in them as a **secret**. This secret is used by Drone for cloning and pushing operations on your GIN repos whilst its running your build jobs inside its runners.

In case your repositories aren't activated in Drone, `gin-proc` activates them and installs the required secret(s) by itself.

<br>

<a name="after-workflow"></a>
#### What happens after you run the workflow from front-end

Your input data from the front-end is sent to the REST API running on port `8000` on the same address. And the API takes over the job from there.

<a name="API"></a>
### API

[Will be hyperlinked to Flask's Auto-Generated Documentations]

<br>

<a name="pipeline"></a>
### Inside the Pipeline

The Drone config `gin-proc` service writes for you essentially does the following inside Drone containers (/runners) in chronological order:

**+** Run a check whether you have run any previous builds on the repository in question, and if yes - then restore the repo from cache in order to speed up the clone process afterwards.

**+** Starts the SSH agent.

**+** Creates an SSH direcotory and writes your `priv-key` from Drone secrets of that repository to that directory, for Drone's use to clone your repository from GIN afterwards.

**+** Disables `Strict Host Checking` for all authorized keys.

**+** Adds your newly written `priv-key` to the SSH agent.

**+** Runs a keyscan on your GIN container and writes the returned SSH fingerprint to `authorized_keys`

**+** Clones your repository from GIN.

**+** Installs Python dependencies if a `requirements.txt` file exists in your repo.

**+** Annex your files if you had mentioned any files to be annexed - after initialising an annex repo in the working directory.

**+** Attaches the commands or runs the Snakefile depending on your workflow chosen.

**+** Add the backpush files, if you added any, and push them back to your repository in a separate `gin-proc` branch after completion of build job.

**+** Pushes the produced output files back finally.

**+** Rebuilds the latest cache of the repo after final operations.

**+** Integrates the required volumes := `/cache` and `/repo`

**+** Tells Drone to only run the build job in the event if you **pushed** to the **master** branch of your repository. Not in any otherwise case.

 **+** Attaches Slack or Email notification plugin if you had selected it from the front-end.