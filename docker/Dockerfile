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

COPY ./paig_server-${VERSION}-py3-none-any.whl ${PAIG_HOME}/

# Install paig server
RUN if [ "$USE_LOCAL_WHEEL" = "true" ] && [ -f "${PAIG_HOME}/paig_server-${VERSION}-py3-none-any.whl" ]; then \
        pip install "${PAIG_HOME}/paig_server-${VERSION}-py3-none-any.whl"; \
    else \
        pip install "paig-server==${VERSION}"; \
    fi

# TODO Remove below line once the guardrails are enabled by default
RUN sed -i "s/^enable = false/enable = true/" /usr/local/lib/python3.11/site-packages/paig/api/shield/conf/shield_scanner.properties
RUN sed -i "s/^guardrail_.*//" /usr/local/lib/python3.11/site-packages/paig/api/shield/conf/shield_scanner.properties
RUN sed -i "s/^region.*//" /usr/local/lib/python3.11/site-packages/paig/api/shield/conf/shield_scanner.properties

# Install spacy model
RUN python -m spacy download en_core_web_lg

# Start the server
CMD ["paig", "run", "--host", "0.0.0.0"]

