
---
This is to save content which can be used later
---

**2. Cutting-Edge Data Protection Mechanisms**:

- **Encryption and Secure Data Storage**: Data reservoirs, including LLM and VectorDB, are encrypted both in transit and
  at rest, ensuring optimal protection from breaches or unauthorized access.
- **Regular Data Backups**: Regularly scheduled backups ensure that data remains safe and retrievable in unforeseen
  situations.

**3. Ethical AI Frameworks**:

- **Bias Detection & Elimination**: By continuously scanning for biases, PAIG ensures AI models are fair and devoid of
  prejudices.

- **Ethics-First Design**: Every feature and model in PAIG is designed with ethical considerations at the forefront,
  ensuring responsible AI utilization.

- **User-Based Pricing**:
  - Each user is priced at $10/month.
  - Every user gets up to 100 checks daily (with one check comprising a prompt and a reply).

- **Non-User Prompts (Public-Facing AI Service)**:
  - Priced at $0.01/request.
  - Billed based on the actual number of monthly requests.

---
1. **Transparent Integration with LangChain:**
   Achieve automated policy enforcement with LangChain via a straightforward integration mechanism. Initialize the PAIG
   plugin by supplying the requisite configuration parameters, allowing the PAIG library to interoperate with LangChain
   inconspicuously, ensuring policy adherence and enforcement are executed without requiring additional manual
   interventions.

2. **Python Library for Native AI Applications:**
   Opt for our Python library to facilitate integration with AI applications developed natively. Here, the PAIG library
   should be initialized with the requisite configuration, and the AI application must be modified to invoke PAIG’s
   Python APIs, ensuring a smooth enforcement of policies.

3. **REST API for Universal Integration:**
   Leverage our REST API for an integration applicable to any AI application. This option doesn't require the inclusion
   of the PAIG plugin within the AI Application. Instead, it requires the AI application to call upon PAIG's REST APIs,
   thereby enforcing the policies.

---

---
-   __REST API for Universal Integration__

    ---

    Perfectly suited for AI applications developed in any programming language,
    this method enables easy integration with the PAIG REST API, allowing for streamlined policy enforcement. Similar to
    the Python library option, developers maintain significant flexibility in API invocation, ensuring PAIG's
    applicability and efficacy across varied development contexts.

    [:octicons-arrow-right-24: REST API](rest-api.md)

---

-   :material-clock-fast:{ .lg .middle } __Just Registered for PAIG?__

    ---

    Explore the capabilities of PAIG with our Open Source Privacera SecureChat AI chatbot. Begin your journey by
    installing SecureChat and configuring it to interface with PAIG and your LLM. Detailed setup instructions are
    available at:

    [:octicons-arrow-right-24: Privacera SecureChat](https://gitlab.com/privacera/chat/privacera_securechat/-/tree/main)


---

<div class="grid cards" markdown>

-   :material-lightning-bolt-outline:{ .lg .middle } __Want to Dive In?__

    ---

    [:octicons-arrow-right-24: Privacera SecureChat](https://gitlab.com/privacera/chat/privacera_securechat/-/tree/main)

    Don't have the patience? :smile: Jump right in and start exploring PAIG's capabilities.

    [:octicons-arrow-right-24: How To](how-to/index.md)

</div>

---

=== "OpenAI LLM"

     For OpenAI, you need to create a file called *openai.key* in the *custom-configs* folder and add the OpenAI key.
    
     ```shell
     echo "<<YOUR_OPEN_AI_KEY>>" > custom-configs/openai.key
     ```
    
     ## **Creating Docker Compose File**
    
     Create a file called *docker-compose.yml* and copy the following code snippet into it.
    
     ```shell title="docker-compose.yml"
     version: '3'
     services:
       privacera_secure_chat:
         image: privacera/privacera-securechat:latest
         container_name: privacera-securechat
         # nginx listener is on 3636. Map it per your need.
         ports:
           - "3636:3636"
         environment:
           PRIVACERA_SHIELD_CONF_FILE: /WORKDIR/custom-configs/privacera-shield-config.json
         volumes:
           - ${PWD}/custom-configs:/WORKDIR/custom-configs
           - ${PWD}/logs:/WORKDIR/securechat/logs
           - ${PWD}/index:/WORKDIR/securechat/index
           - ${PWD}/db:/WORKDIR/securechat/db
     ```

## **Creating Docker Compose File**

Create a file called *docker-compose.yml* and copy the following code snippet into it.

```shell title="docker-compose.yml"
version: '3'
services:
  privacera_secure_chat:
    image: privacera/privacera-securechat:latest
    container_name: privacera-securechat
    # nginx listener is on 3636. Map it per your need.
    ports:
      - "3636:3636"
    environment:
      PRIVACERA_SHIELD_CONF_FILE: /WORKDIR/custom-configs/privacera-shield-config.json
    volumes:
      - ${PWD}/custom-configs:/WORKDIR/custom-configs
      - ${PWD}/logs:/WORKDIR/securechat/logs
      - ${PWD}/index:/WORKDIR/securechat/index
      - ${PWD}/db:/WORKDIR/securechat/db
```

---