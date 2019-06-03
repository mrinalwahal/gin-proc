# gin-proc

Automated Continuous Integration (CI) micro-service for *gin* service.

Stage: `prototype` 

## Install Docker

## Installation: Local (Dev)

It's advisable to use all `gin` micro-services inside docker containers and further connect all containers to interact with each other for increased fault tolerance.

[1] In order to allow all docker containers to interact with each other, create a **docker network** and connect all containers to this network.

Command: `docker network create <network-name>`

[2] Create **gin** service container.

Command: ` docker run --name=gin --net gin -p 10022:22 -p 3000:3000 -v /var/gogs:/data gnode/gin-web`

[3] Check and copy IP address of **gin** service container.

Command: `docker network inspect <network-name>`

Copy IP of GIN container from `containers` section.

[4] Create **drone** CI/CD service container.

Command: `docker run  \
 --volume=/var/run/docker.sock:/var/run/docker.sock \
 --env=DRONE_GIT_ALWAYS_AUTH=false \
 --env=DRONE_GOGS_SERVER=http://172.19.0.2:3000  \
 --env=DRONE_RUNNER_CAPACITY=2 \
 --env=DRONE_RUNNER_NETWORKS=gin \ --env=DRONE_SERVER_HOST=172.19.0.3 \  --env=DRONE_SERVER_PROTO=http \
 --env=DRONE_TLS_AUTOCERT=false \
 --publish=80:80 \
 --publish=443:443 \
 --publish=2224:22 \
 --restart=always \
 --detach=true \
 --net gin \
 --name=drone \
 drone/drone:latest  `

## Installation: Remote (Production) 

**remaining**
