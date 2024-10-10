# Build a Docker image for a Python backend and React frontend web app
# Use a Debian base image
FROM node:18-bookworm-slim as node-build
# Set the working directory
WORKDIR /workdir

# Copy your React frontend code
COPY web-ui web-ui/

# Install React App dependencies and build static files
RUN npm install npm@9.8.1 -g
RUN cd /workdir/web-ui && npm install --legacy-peer-deps && npm run build && rm -rf node_modules && npm cache clean --force


FROM python:3.11-slim as python-build
# Set the working directory
WORKDIR /workdir

# Install specific versions of Python and Nginx and other dependencies
RUN apt update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

COPY web-server/requirements.txt  .

# Install Python dependencies
RUN python3 -m venv /venv && \
    . /venv/bin/activate && \
    pip install -r requirements.txt

FROM python:3.11-slim
WORKDIR /workdir
RUN apt update \
 && apt-get install -y --no-install-recommends nginx vim\
 && rm -rf /var/lib/apt/lists/*

COPY --from=node-build /workdir/web-ui/build /usr/share/nginx/html

# Copy Nginx configuration
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=python-build /venv /venv

# Copy your Python backend code
COPY web-server/src/paig_securechat  .

# Create directories
RUN mkdir -p securechat && mkdir -p /workdir/securechat/sales/data && mkdir -p /workdir/securechat/sales/index && \
    mkdir -p /workdir/securechat/db && mkdir -p /workdir/securechat/logs && mkdir -p /workdir/custom-configs

# COPY base app data
COPY data /workdir/securechat/sales/data/

# Start Gunicorn servers
WORKDIR /workdir
COPY docker/start_securechat.sh /workdir/start_securechat.sh
COPY web-server/src/paig_securechat/run_gunicorn.sh /workdir/run_gunicorn.sh
COPY web-server/src/paig_securechat/run_db_setup.sh /workdir/run_db_setup.sh

RUN chmod +x /workdir/start_securechat.sh
RUN chmod +x /workdir/run_gunicorn.sh
RUN chmod +x /workdir/run_db_setup.sh

RUN groupadd --gid 1000 paig_user \
  && useradd --home-dir /home/paig_user --create-home --uid 1000 \
  --gid 1000 --shell /bin/sh --skel /dev/null paig_user

RUN chown -R paig_user:paig_user /workdir && chmod -R 755 /workdir && \
        chown -R paig_user:paig_user /var/lib/nginx && \
        chown -R paig_user:paig_user /var/log/nginx && \
        chown -R paig_user:paig_user /etc/nginx/conf.d
RUN touch /var/run/nginx.pid && \
        chown -R paig_user:paig_user /var/run/nginx.pid

USER paig_user

EXPOSE 3636 3535

ENTRYPOINT ["/workdir/start_securechat.sh"]
CMD ["-m", "start"]
