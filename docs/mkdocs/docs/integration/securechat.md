---
title: Privacera SecureChat 
---
# Privacera SecureChat

Privacera SecureChat, our AI chatbot, offers an accessible way to experience Generative AI (GenAI) in action. It serves as a practical starting point to explore the functionalities and benefits of PAIG. You can easily set up SecureChat and integrate it with PAIG and your preferred Large Language Model (LLM).

While SecureChat is a convenient and effective tool for understanding PAIG's capabilities in a chatbot scenario, it's important to note that using SecureChat is not a prerequisite for leveraging PAIG. Our platform is designed to be flexible and compatible with a wide range of GenAI applications, ensuring that you can integrate PAIG seamlessly with your existing or preferred AI solutions.
## **Prerequisites**

The following are the prerequisites for installing and configuring SecureChat:

<div class="annotate" markdown>
- [ ] [Docker](https://docs.docker.com/engine/install/) (1)
- [ ] [Docker Compose](https://docs.docker.com/compose/install/)
- [ ] Credentials to access LLM
    * [ ] For OpenAI LLM you will need the OpenAI key.
    * [ ] For Bedrock LLM you will need IAM Role which has the permission to access Bedrock. 
</div>

  1. [Check the prerequisites section](prerequisites/docker.md)
    
## **Setting Up Environment**

To install SecureChat, we need to create a folder and add the required configuration files. By default we will
create the folder in the home directory of the user. You can change the location as per your requirement.

```shell
mkdir -p ~/privacera_securechat
cd ~/privacera_securechat
```

Create the custom configuration folder *custom-configs* and copy the Privacera Shield Application configuration file 
and rename it to *privacera-shield-config.json*.

```shell
mkdir -p custom-configs data db index logs
```

## **Connecting SecureChat to PAIG**

### **Adding AI Application in PAIG**

<!-- md:go_to_paig /#/ai_applications:Go To PAIG -->

As a first step, you need to add your AI Application in PAIG and we will use that application to integrate PAIG.
If you already added the Application to the PAIG, then you can skip this step.

--8<-- "docs/integration/snippets/create_application.md"

### **Downloading Privacera Shield Configuration File**

<!-- md:go_to_paig /#/ai_applications:Go To PAIG -->

--8<-- "docs/integration/snippets/download_application_config.md"

Move the Privacera Shield Application configuration file you downloaded to the *custom-configs* folder and rename it to *privacera-shield-config.json*.

!!! info "Rename Application Configuration File"
    The downloaded Privacera Shield Application configuration file is named *privacera-shield-<<APP_NAME>>-config.json*. 
    Rename it to *privacera-shield-config.json*.
    e.g.
    ```shell
    mv ~/Downloads/privacera-shield-Secure-Chat-config.json \
        custom-configs/privacera-shield-config.json
    ```

## **Installing SecureChat**

This section provides the steps to install SecureChat with pre-configured sample data. You can skip this section 
if you want to customize the SecureChat with your own data. 



/// details |  Are you using your own data for VectorDB?
    type: question

If you are using your own data, then you can skip rest and follow the instructions to customize the SecureChat.
However, if you are trying out for the first time, then first try with the sample data and then customize it with 
your own data.

1. [For ChromaDB and OpenAI using custome data](securechat-chromadb-openai.md#installing-privacera-securechat-with-chromadb-and-openai)
2. [For OpenSearch and OpenAI](securechat-opensearch-openai.md#installing-privacera-securechat-with-opensearch-and-openai)

///

=== "OpenAI LLM"

    <a id="openai-key"></a>

    For OpenAI, you need to create a file called *openai.key* in the *custom-configs* folder and add the OpenAI key.

     ```shell
     echo "<<YOUR_OPEN_AI_KEY>>" > custom-configs/openai.key
     ```
    Download the  `docker-compose.yaml` file and save it in the `privacera_securechat` folder or where you will be running Privacera's SecureChat.

    [Download docker-compose.yaml for OpenAI](snippets/docker-compose-securechat-openai.yaml){:download="docker-compose.yaml"}

=== "Bedrock LLM"

    !!! warning "IAM Role Requirement"

        You need IAM roles to access the Bedrock LLM. Please make sure that the EC2 instance where you are running the
        Privacera SecureChat has the IAM role with the permission to access Bedrock.

    Download the  `docker-compose.yaml` file and save it in the `privacera_securechat` folder or where you will be running Privacera's SecureChate.

    [Download docker-compose.yaml for Bedrock](snippets/docker-compose-securechat-bedrock.yaml){:download="docker-compose.yaml"}

    Download the `dev_config.yaml` configuration file and save it in the sub-folder `privacera_securechat/custom-configs` 
    or to sub-folder `custom-configs` from where you will be running Privacera's SecureChat. You will need to update the
    `dev_config.yaml` file with the correct model and region information.

    [Download dev_config.yaml for Bedrock](snippets/securechat-bedrock-dev-config.yaml){:download="dev_config.yaml"}

    !!! info "Models and region configuration"
        The default `dev_config.yaml` uses the following values. Please change it accordingly to your account


        ```shell hl_lines="2 3 4"
        bedrock:
          model: "anthropic.claude-v2"
          region: "us-west-2"
          embedding_model: "amazon.titan-embed-text-v1"
        ```

---

## **Running SecureChat**

To run SecureChat, execute the following command:

```shell
docker-compose stop
docker-compose pull
docker-compose up -d
```

To ensure that SecureChat is running, execute the following command to see if the docker containers are running:

```shell
docker-compose ps
```

To check the logs, execute the following command. This will tail the logs and you can press `Ctrl+C` to stop the logs.

```shell
docker-compose logs -f
```

If everything is running fine, you should see the following message in the logs:

```shell
privacera-securechat  | [2023-11-10 12:18:27,653] INFO [274889730944] on.py  - Application startup complete.
```

## **Using SecureChat**

To use SecureChat, open a browser and go to [http://localhost:3636](http://localhost:3636){:target="_blank"}. 
You should see the page which will ask the user name. For testing, enter the name *sally* and click **Login** button.

!!! info "Authentication"
    Please note that SecureChat does not have any authentication mechanism enabled by default.

Here are some use cases you can try

### **Use Case 1: Default Access Policy**

When the AI Application is added to PAIG, by default everyone get access to the application. This can be tested by
following the steps below:

1. Login as *sally*.
2. On the left top, click on the **+ New Conversation** button and select **Sales Intel**.
3. You can click on the `Give me the contact information for Equinox Technologies?` sample question from the box
4. You should see the response from the LLM which will be similar to the below response, but it could be different for each LLM:

    !!! example "Sample Response"
        One of the contact information for Equinox Technologies is the phone number and email address listed in 
        the first piece of context.

6. Now go to [Security Audits](/#/audits_security){:target="_blank"} and check the prompts and response for the conversation.
6. You can also click on the *Eye* icon to see the content that was sent to the LLM and the response to the user
7. The default content restriction policies is to redact PII information. If you check the responses from the RAG, 
   you will see that the PII information is redacted.

### **Use Case 2: Disable redaction of Sensitive Information**

By default PAIG redacts all PII data in the prompt and reply from the VectorDB and LLM. Due to this reason, sometimes
the PII data won't even show in the response. However, if want to show actual values in the response, then you can
disable the redaction restrictions.

1. Go to the SecureChat application [AI Application](/#/ai_applications){:target="_blank"} and select the *Secure Chat* application.
2. At the top menu tabs, select **Permissions**.
3. For the restriction list, disable the Content Restriction policy *Personal Identifier Redaction* by sliding the
   toggle to the left
4. Wait for few seconds and go back to the SecureChat application and ask the following question: `Give me the contact information for Equinox Technologies?`
5. You should now see PII data in the response.

    !!! note "Inconsistent Result"
        In conversation mode, the result might be inconsistent as the LLM might not return the same result every time.


### **Use Case 3: Deny Access Policy**

By default everyone is provided access to the AI Application. We can change it to *Deny* permission and test it.

1. Go to the SecureChat application [AI Application](/#/ai_applications){:target="_blank"} and select the *Secure Chat* application.
2. At the top menu tabs, select **Permissions**.
3. In the **AI Application Access** section, click the edit :material-pencil: icon
4. Remove the **Everyone** group from the list and click on the [**SAVE**] button 
5. Wait for few seconds and ask the same question again. You should see the below message in the response. You can
   also see the denied message in the [Security Audits](/#/audits_security){:target="_blank"}.

!!! note "Response"
    *** Access Denied, message: ERROR: PAIG-400004: Access denied. Server returned error-code=403, error-message=Access is denied


## **Stopping SecureChat**

To stop SecureChat, execute the following command for the folder which contains the `docker-compose.yaml` file

```shell
docker-compose down
```

To ensure all the containers are stopped, execute the following command:

```shell
docker-compose ps
```


## Troubleshooting

/// details | How do I troubleshoot SecureChat?

1. Check if the containers are running using the following command:

    ```shell
    docker-compose ps
    ```
    If you see the following output, then it means the containers are running, otherwise check the logs.

    ```shell
    privacera-securechat  | [2024-01-07 05:52:22,469] INFO [274911635264] on.py  - Application startup complete.
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

/// details | Log Message `Please provide OPENAI key at mentioned path.`
    type: warning
```shell
privacera-securechat  | OPEN AI Key file=/workdir/custom-configs/openai.key doesn't exists.
privacera-securechat  | Please provide OPENAI key at mentioned path.
```

If you see the above output, then it means that the OpenAI key is not provided. Please make sure that you have created 
the `openai.key` file in the `custom-configs` folder and added the OpenAI key in the file. [See the instructions](#openai-key) for more details.

///


/// details | Log Message `PAIG Shield plugin setup failed. Please confirm if the configuration file /workdir/custom-configs/privacera-shield-config.json is correct and exists`
    type: warning

If you see the above output, then it means that SecureChat was not able to find the Privacera Shield configuration file. 
There could be 2 reasons for this:

1. The Privacera Shield configuration file is not present in the `custom-configs` folder. Please make sure that you have
   downloaded the Privacera Shield configuration file and renamed it to `privacera-shield-config.json` and placed it in
   the `custom-configs` folder.
2. The Privacera Shield configuration file name is not correct. Please make sure that you have downloaded the correct
   configuration file from the PAIG portal and renamed it to `privacera-shield-config.json` and placed it in the
   `custom-configs` folder.

///

