# Installing Docker and Docker Compose

!!! note "Operating System"
    Docker install varies depending on the OS. Refer to the ==**Table of Contents**== on the right for the specific OS 
    you are using. If your OS is not listed, refer to the official [Docker documentation](https://docs.docker.com/engine/install/).

## On AWS EC2 with AWS Linux 2

### Installing Docker on AWS EC2

Amazon Linux 2 comes with Docker available in its repositories. Install it by running:

```bash
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker $(whoami)
```

Log out and log back in for this to take effect.

Check if Docker is installed correctly by running:

```bash
docker --version
```

### Installing Docker Compose on AWS EC2

```bash
DOCKER_COMPOSE_VERSION="v2.22.0"
sudo  curl -L https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

Check if Docker Compose is installed correctly by running:

```bash
docker-compose --version
```

---
