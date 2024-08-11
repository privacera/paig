---
title: Self Managed Privacera Shield
---

# Self Managed Privacera Shield

<!-- md:feature_upgrade ../faq/index.md#enterprise_plan_only: Enterprise Plan Only -->

## Overview

The Self-Managed PAIG Shield is an enterprise-level add-on feature designed to provide enhanced security and compliance
for customers using PAIG within their own Virtual Private Cloud (VPC). This feature allows for the local handling and
evaluation of policy checks from the customer's AI applications, ensuring secure and efficient operations. PAIG Shield,
when deployed in the customer's VPC, operates independently while maintaining secure connections with Privacera.AI for
essential functions like policy synchronization and audit uploads.

## Key Features

- **Local Deployment**: PAIG Shield functions entirely within the customer's VPC, ensuring data security and local
  policy evaluation.
- **Secure Communication**: Utilizes public/private key cryptography for secure exchanges between the AI applications
  and PAIG Shield.
- **Local Data Retention**: With Self-Managed PAIG Shield, all customer data remains strictly within the confines of the
  customer's VPC. This setup ensures that sensitive data never leaves the customer's controlled environment, providing
  an extra layer of security and data sovereignty. Keeping data within the VPC significantly reduces the risk of data
  breaches and external threats. This feature supports compliance with stringent data protection regulations, such as
  GDPR, which often require data to be stored and processed within specific geographical boundaries or controlled
  environments.
- **User-Friendly Configurability**: Simplified and intuitive setup process for PAIG Shield in the self-managed mode.
- **Regulatory Compliance Assurance**: Meets all legal and regulatory standards, focusing on data protection and
  privacy.

## Prerequisites

Before proceeding with the installation of Privacera Shield, ensure the following prerequisites are met:

<div class="annotate" markdown>
- [ ] [Docker](https://docs.docker.com/engine/install/) (1) 
- [ ] Docker Compose (v2.22.0 or higher)
- [ ] Must have ADMIN role login credentials in [PAIG](/)
- [ ] The Self-Managed Shield feature should be enabled in your account. Contact Privacera Support for activation.
- [ ] The VM Instance where the Shield Service will be installed must have access from your GenAI application.
- [ ] The hostname or IP address of the VM Instance where the Shield Service will be installed.
</div>

  1. [Check the prerequisites section](prerequisites/docker.md)

## Installation

!!! info "Enabling Self-Managed Shield"
The Self-Managed Shield feature must be enabled in your account.
If the **Shield Configuration** menu is visible in the **Account** menu, this feature is already enabled for you.
If it's not visible and you want to use it, Contact Privacera Support for activation.

1. **Portal Configuration**:
    - Login to your [PAIG Portal](/)
    - Navigate to the **Account** menu, and select **Shield Configuration**
    - Enter the VM Instance Hostname or IP address in the *Privacera Shield Service Endpoint URL* textbox.
        - Example URL format: `http://<shield-ip-address>:8181` or `http://<shield-hostname>:8181`

      !!! info "Enabling Self-Managed Shield"
      This URL is utilized by AI Applications to connect to the Shield Service. It typically runs on the HTTP protocol on port 8181.

        - In the next box, enter the same VM Instance Hostname or IP address in the *Audit Service Endpoint URL* textbox and click **[Apply]** button.
            - Example URL format: `http://<shield-audit-ip-address>:8282` or `http://<shield-audit-hostname>:8282`

          !!! info "Enabling Self-Managed Shield"
          This URL is utilized by PAIG Portal to connect to the Shield Audit Service for displaying Audits in Browser. It typically runs on the HTTP protocol on port 8282.

2. **Download Configuration File**:
    - Click on “Download Shield Configuration” to obtain the `self_managed_privacera_shield_configs.properties` file.

3. **Prepare the VM Instance**:
    - SSH into the VM where Privacera Shield Service will be installed.
    - Make sure Docker and Docker Compose are installed.
    - Set your work directory and prepare the configuration directory:
      ```
      cd ~
      export PAIG_HOME=`pwd`/privacera/paig
      mkdir -p ${PAIG_HOME}/configs
      ```
    - Upload the downloaded `self_managed_privacera_shield_configs.properties` file to the VM and move it to `${PAIG_HOME}/configs`.

4. **Docker Repository Login**:
    - Navigate to `$PAIG_HOME`.
        - The credentials for Docker repository is available in the `self_managed_privacera_shield_configs.properties`
          and needs to be extracted using the below commands and used for login.
          ```shell
          docker_host=$(grep "paig_authz_base_url" configs/self_managed_privacera_shield_configs.properties | awk -F'=' '{print $2}' |  awk -F'//' '{print $2}')
          docker_pass=$(grep "paig_api_key" configs/self_managed_privacera_shield_configs.properties | awk -F'=' '{print $2}')
          docker login $docker_host -u user-name -p $docker_pass
          ```

5. **Docker Compose File**:

   Download [docker-compose.yaml](snippets/docker-compose-self-managed-privacera-shield.yaml){:download="docker-compose.yaml"} file and save it folder where you will be running Privacera's Shield.

   !!! info "Default port for Privacera Shield"
   The default port for Privacera Shield is `8181`. If you want to change the port, update the `docker-compose.yaml` file.

   !!! info "Default port for the Shield Audit"
   The default port for the Shield Audit is `8282`. If you want to change the port update the `docker-compose.yaml` file.

6. **Run the Shield Service**:
    - Start the Shield Service to run in the background using the following command. This will stop the existing service, pull the latest image and start the service.
      ```shell
      docker-compose stop
      docker-compose pull
      docker-compose up -d
      ```

## Validation

- **Check Docker Containers**:
    - Validate that the Shield Service is running:
      ```shell
      docker-compose ps
      ```
- **Check Service Health**:
    - Validate the status of the Shield Service:
      ```shell
      curl --location 'http://<shield-ip-address>:8181/health'
      ```

- **Connect AI Applications**:
    - You can now link your Privacera-enabled AI Applications to this local shield service by downloading the
      “Self-Managed” App configs from the PAIG Portal → AI Applications Section.

## Message Audits Storage Configurations

- By default, the Prompt and Response messages for your AI Application are encrypted and stored in your local storage system at the path -
  ```${PAIG_HOME}/audit_logs```

- To change the storage path or to store the messages in an external storage system like "s3", you can update the `self_managed_privacera_shield_configs.properties` file available at ```${PAIG_HOME}/configs``` and restart the Shield Service.

- To restart the Shield Service, you can use the following command:
  ```shell
  docker-compose restart
  ```

## Troubleshooting

/// details | How do I troubleshoot SecureChat?

1. Check if the containers are running using the following command:

    ```shell
    docker-compose ps
    ```
   If you see the following output, then it means the containers are running, otherwise check the logs.

```shell
   NAME                       IMAGE                                             COMMAND                  SERVICE        CREATED         STATUS        PORTS
   privacera-paig-shield-1    api.na.privacera.ai/paig/paig-shield:latest       "uwsgi uwsgi.ini"        paig-shield    2 minutes ago   Up 2 minutes  0.0.0.0:8181->8181/tcp
   privacera-shield-audit-1   api.na.privacera.ai/paig/shield-audit:latest      "/entrypoint/entrypo…"   shield-audit   2 minutes ago   Up 2 minutes  0.0.0.0:8282->8080/tcp
```

2. Check the logs by using the following command:

    ```shell
    docker-compose logs -f
    ```

   Review the logs and see if there are any errors and remediate them accordingly.

///

/// details | Docker containers are not starting
type: warning
```shell
docker-compose ps     

NAME      IMAGE     COMMAND   SERVICE   CREATED   STATUS    PORTS
```

If you see the above output, then it means that the containers are not running. You can check the logs using the following command:

```shell
docker-compose logs -f
```
Review the logs and see if there are any errors and remediate them accordingly.

///

