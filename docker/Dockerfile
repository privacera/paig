FROM python:3.11.9-slim-bullseye

ARG VERSION
ARG USE_LOCAL_WHEEL=false

ENV APP_NAME=paig \
    PAIG_HOME=/opt/${APP_NAME} \
    PAIG_DEPLOYMENT=dev \
    VERSION=$VERSION \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NVM_DIR=/usr/local/nvm \
    NODE_VERSION=v20.18.1

WORKDIR $PAIG_HOME

# Install dependencies and Node.js in a single layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl build-essential gcc g++ make && \
    mkdir -p ${NVM_DIR} && \
    curl -o- https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash && \
    . ${NVM_DIR}/nvm.sh && \
    nvm install ${NODE_VERSION} && \
    nvm use --delete-prefix ${NODE_VERSION} && \
    ${NVM_DIR}/versions/node/${NODE_VERSION}/bin/npm install -g promptfoo && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Add Node.js to PATH
ENV PATH=${NVM_DIR}/versions/node/${NODE_VERSION}/bin:$PATH

# Copy wheel files if using local wheels
COPY artifacts/ /tmp/artifacts/

# Install packages
RUN if [ "$USE_LOCAL_WHEEL" = "true" ]; then \
        echo "Installing from local wheel files"; \
        pip install /tmp/artifacts/paig_server-*.whl; \
        pip install /tmp/artifacts/paig_common-*.whl --force-reinstall; \
        pip install /tmp/artifacts/paig_authorizer_core-*.whl --force-reinstall; \
        pip install /tmp/artifacts/paig_evaluation-*.whl --force-reinstall; \
        rm -rf /tmp/artifacts; \
    else \
        echo "Installing from PyPI"; \
        pip install paig-server; \
        pip install paig-common --force-reinstall; \
        pip install paig-authorizer-core --force-reinstall; \
        pip install paig-evaluation --force-reinstall; \
    fi

# Install spacy model
RUN python -m spacy download en_core_web_lg

# Clean pip cache
RUN pip cache purge

# Start the server
CMD ["paig", "run", "--host", "0.0.0.0"]

