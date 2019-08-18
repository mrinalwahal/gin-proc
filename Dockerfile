<<<<<<< HEAD
FROM ubuntu
RUN apt-get update && apt-get install git-annex python3.6 python3-pip -y
=======
FROM python:3

RUN mkdir -p /app/backend
RUN mkdir -p /app/frontend

COPY back-end/. /app/backend
COPY front-end/. /app/frontend
COPY images /app/images

COPY requirements.txt /app
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update
RUN apt-get install -y npm

WORKDIR /app/frontend
RUN npm install npm@latest -g
RUN npm install nuxt -g

RUN npm install
RUN nuxt build

WORKDIR /app

COPY docker/entrypoint.sh /app/
ENTRYPOINT ["/app/entrypoint.sh"]
>>>>>>> 24d88e2e250480cc18f94c3a7024a2af3200a06f
