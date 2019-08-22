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
