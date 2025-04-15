FROM python:3.11.9-slim-bullseye

ARG VERSION
ARG USE_LOCAL_WHEEL

ENV APP_NAME=paig
ENV PAIG_HOME=/opt/${APP_NAME}
ENV PAIG_DEPLOYMENT=dev
ENV VERSION=$VERSION

RUN mkdir -p ${PAIG_HOME}

WORKDIR $PAIG_HOME

RUN apt-get update
RUN apt-get install -y vim curl

ENV NVM_DIR /usr/local/nvm
ENV NODE_VERSION v20.18.1
RUN mkdir -p /usr/local/nvm
RUN curl -o- https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
RUN /bin/bash -c "source $NVM_DIR/nvm.sh && nvm install $NODE_VERSION && nvm use --delete-prefix $NODE_VERSION"
ENV NODE_PATH $NVM_DIR/versions/node/$NODE_VERSION/bin
ENV NPM_PATH $NVM_DIR/versions/node/$NODE_VERSION/bin/npm
ENV PATH $NODE_PATH:$NPM_PATH:$PATH
RUN apt-get install -y build-essential gcc g++ make
RUN $NVM_DIR/versions/node/$NODE_VERSION/bin/npm install -g promptfoo

RUN pip install paig-server

# Install spacy model
RUN python -m spacy download en_core_web_lg

# Start the server
CMD ["paig", "run", "--host", "0.0.0.0"]

