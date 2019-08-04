# [GIN](https://gin.g-node.org) gin-proc Microservice

<br>

[![G-Node](./images/favicon.png)](https://gin.g-node.org)

This repository contains documentation for using the **gin-proc** microservice for **[GIN](https://gin.g-node.org)** s as well as its setup and support scripts.

Please file an issue if you are experiencing a problem or would like to discuss something related to the microservice.

Pull requests are encouraged if you have changes you believe would improve the setup process or increase compatibility across deployment environments.

<br>

## Table of Contents
* **[Introduction](#introduction)**
  - [Problem statement](#problem)
  - [Rationale and Significance](#rationale)
* **[Installation](#install)**
  - [GIN's hosted cloud](#cloud)
  - [Local environment](#local)
* **[Usage](#usage)**
* **[Tests](#tests)**
* **[FAQ](#questions)**
* **[License](#project-license)**

<br>

<a name="introduction"></a>
## Introduction

**gin--proc** is a GIN micro-service which allows the users to design efficient workflows for their work - by automating Snakemake, and build the workflows with open-source version of Continuous Integration (CI) service [Drone](https://drone.io/).

<br>

<a name="problem"></a>
### Problem Statement

INCF is hosting a GIN service designed above GOGS with Git to serve as a repository management utility categorically for the Neuroinformatics data. The users (from non-tech backgrounds) find it tough to automate their workflows - precisely going from the input phase to the output phase. A lot of data makes writing workflows a repetitive and redundant task for them. Even if they are using tools like Snakemake. If they are past this stage, still testing all their workflows for potential errors and/or bugs for exorbitant amount of data and their workflows, consumes even more amount of time and reduces their efficiency.

<br>

<a name="rationale"></a>
### Rationale and Significance

This tool/micro-service is required since, given the GIN user base of neuroscientists and other pro-fessionals from the related fields, shouldn’t be involved in writing thousands of repeated workflows for their data, and then testing it manually. This tool will increase their efficiency by almost exponential levels by eradicating redundancy from their work.

<br>

<a name="install"></a>
## Installation

NOTE: We are currently writing the microservice, therefore, we haven't freezed a particular *Dockerfile* for our image. Will release it soon. Until then, you can only set up the service from source.

<a name="cloud"></a>
### GIN's Hosted Cloud

We are currently deploying the utility for our cloud environment. Please check back after some time.

<a name="local"></a>
### Local Environment (D-I-Y)

<br>

**Prerequisites**

* [Docker](https://docs.docker.com/)
* [g-node/gin-web](https://hub.docker.com/r/gnode/gin-web) node running in a docker container. If you don't have this then folow steps until [#install-gin](#install-gin)

It's advisable to use all the **gin micro-services** inside docker containers and further connect all containers to interact with each other for increased fault tolerance.

<br>

**Prepare Environment**

Ignore the following step if you already have a key pair set-up for your use with GIN and skip to [#create-network](#create-network).
Generate new SSH key pair using specifically with gin-proc.

**Remember to leave the password empty for the keypair. Otherwise you'll have to hardcode your sudo password in all your future repositories.**

`ssh-keygen`

Save the keys as `gin_id_rsa.pub` and `gin_id_rsa`.

**Steps**

<a name="create-network"></a>
**[1]** In order to allow all gin containers to interact with each other, create a **docker network** and connect all containers to this network.

`docker network create <docker-network-name>`

**[2]** If you already have a **gin** service container running, then attach it stop it. And attach it to the new network.

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

Now go to your terminal and copy your `gin_id_rsa.pub` key and install it in gin by accessing repository *settings/SSH Keys*.


**[5]** Create **drone** CI/CD service container.

```
    docker run --volume=/var/run/docker.sock:/var/run/docker.sock --volume=/gin-proc/repo:/repo --volume=/gin-proc/cache:/cache --env=DRONE_GIT_ALWAYS_AUTH=false --env=DRONE_GOGS_SERVER=http://<GIN_SERVER_IP>:3000  --env=DRONE_RUNNER_CAPACITY=2 --env=DRONE_RUNNER_NETWORKS=gin --env=DRONE_SERVER_HOST=172.19.0.3  --env=DRONE_SERVER_PROTO=http --env=DRONE_TLS_AUTOCERT=false --env=DRONE_USER_CREATE=username:<GIN_USERNAME>,admin:true --publish=80:80 --publish=443:443 --publish=2224:22 --restart=always --detach=true --net gin --name=drone drone/drone:latest
 ```
Access drone at `172.19.0.3:80` in your browser. You will get a list of your repositories. Click on **ACTIVATE** for which your want to enable **gin-proc** microservice.

**[6]** Install Drone secrets.

On your Drone dashboard, access the settings for your repository.

Now Add a new secret with the name `**DRONE_PRIVATE_SSH_KEY**`. And the value of this secret should be the private key `gin_id_rsa` contents. For that, simply copy paste the key content from your terminal.

<a name="run-proc"></a>
## Run gin-proc microservice

Make sure your keys are installed with the GIN container. Micro-service, for now, skips ensuring/installing new keys on the GIN server (Its still in testing).

From project's root...
```export GIN_SERVER=<GIN_IP>:<GIN_PORT>```

```cd back-end && python server.py```

On a new console, go back to project's root and..
```cd front-end && npm run dev```

Log in at your front-end app's SERVER IP displayed in console on endpoint `/login`. 
Only log in with your GIN credentials.

<br>

<a name="usage"></a>
## Usage

In every repository that you create on gin, you have to mandatorily add a **.drone.yml** file which contains the pipelines and build jobs for drone to run.

Use the sample `.drone.yml` file [attached](./samples/.drone.yml) in this repository. Or copy the contents from below.

```
kind: pipeline
name: default

clone:
  disable: true

steps:
- name: clone
  image: docker:git
  environment:
    REPO: test
    GIN_USER: "<YOUR-GIN-USERNAME>" 
    GIN_SERVER: "172.19.0.2"
    SSH_KEY:
      from_secret: DRONE_PRIVATE_SSH_KEY  
  commands:
    - echo "[+] Starting SSH Agent"
    - eval $(ssh-agent -s)

    - echo "[+] Installing SSH Keys"
    - mkdir /root/.ssh && echo "$SSH_KEY" > /root/.ssh/id_rsa && chmod 0600 /root/.ssh/id_rsa
    - echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config
    - ssh-keyscan -H "$GIN_SERVER" >> /root/.ssh/known_hosts
    - ssh-add /root/.ssh/id_rsa

    # Uncomment the next line if you want to debug SSH Connection failures.
    # - ssh -Tv git@"$GIN_SERVER" -p 22 -i /root/.ssh/id_rsa

    - git clone git@"$GIN_SERVER":/"$GIN_USER"/"$REPO".git
    - echo "[+] Clone complete"

# You can replace the following pipeline step and write your own beyond this point.

- name: proc
  image: ubuntu
  environment:
    REPO: test
  commands:
    - apt-get update
    - apt-get install python -y
    - which python
```

<br>

<a name="tests"></a>
## Tests

The attached sample **.drone.yml** file can be simply used to test whether things are working fine.

We are writing more scripts to perform testing. If anyone wishes to contribute test scripts, a pull request is more than welcome.

<br>

<a name="questions"></a>
## FAQ

Q: Drone throws `permission denied (publickey)` error. How do I resolve this?

A: Add the line `- ssh -Tv git@172.19.0.2 -p 22 -i /root/.ssh/id_rsa` in your clone job in .drone.yml file before running `git clone`. It will present you with complete debug logs of the SSH connection drone tries to make from its container to your GIN container. Errors presented there can help you resolve the issue faster.

---

Q: I get a `Host Key authenticated failed` error during `git clone` in drone pipeline.

A: Either your SSH keys that you have added to GIN and to Drone as a secret don't match, or you can also check if the key pairs you installed needed your sudo password to unlock the keys. If that's the case, create new key pairs without passphrases. And install them.

<br>

<a name="authors-contributors"></a>
## Authors and Contributors

<table><tbody>
<tr><th align="left">Achilleas Koutsou</th><td><a href="https://github.com/achilleas-k">GitHub/achilleas-k</a></td><td></td></tr>
<tr><th align="left">Michael Sonntag</th><td><a href="https://github.com/mpsonntag">GitHub/mpsonntag</a></td><td></td></tr>
<tr><th align="left">Mrinal Wahal</th><td><a href="https://gitlab.com/wahal">GitLab/wahal</a></td><td><a href="https://mrinalwahal.com/rvagg">MrinalWahal.com</a></td></tr>
</tbody></table>

Contributions are welcomed from anyone wanting to improve this project!

<br>

<a name="project-license"></a>
## License

This microservice is licensed under the BSD 3-Clause license. All rights not explicitly granted in the MIT license are reserved. See the included [LICENSE.md](./LICENSE.md) file for more details.

------------------------------------------------------------------

*Supported with :heart: by [Achilleas Koutsou](https://github.com/achilleas-k), [Michael Sonntag](https://github.com/mpsonntag) and the [G-Node](https://github.com/orgs/G-Node/people) team.*

*This project is affiliated with [G-Node](http://www.g-node.org/) and [GIN](https://gin.g-node.org).*

<br>

*Neither G-Node nor GIN owns the trademark for Drone.*
