# Configure GenAI Application

This section provides detailed guidance on configuring a GenAI application for security evaluation in PAIG.

## Configuring GenAI Application


Before running the evaluation your GenAI application must be configured in PAIG Security Evaluation.
PAIG Evaluation will use the configuration details to connect to your GenAI application and send prompts for evaluation.
Application should be configured with valid HTTP endpoint URL, method, headers and other details of your GenAI application which should respond to a prompt.

To configure a GenAI application for security evaluation in PAIG, follow these steps:

1. **Navigate to the Security Evaluation Module**: Log in to the PAIG platform and access the Security Evaluation module from  `Paig Lens` > `Security Evaluation`.
2. **Add New**: Click on the `Add New` button to create a new security evaluation.
3. **Applications Configurations Listing**: 
    - The applications configurations listing page displays all the GenAI applications available for evaluation.
    - Click on the `edit` button next to the application you want to configure.
    - If you want to add a new application, click on the `New Configuration` button.
4. **Configure Application Form**:
    - Fill in the details in the configuration form:
        - **Name**: Enter the name of the GenAI application.Incase application exists in PAIG AI applications list ,name cannot be changed
        - **Connection type**: Evaluation will use default connection type as `HTTP/HTTPS Endpoint`
        - **Endpoint URL**: Enter request URL of your GenAI application using which prompts will be sent for evaluation.
           e.g.  `http://127.0.0.1:3535/securechat/api/v1/conversations/prompt`
        - **Method**: Select HTTP method of your request endpoint url from the available options.
        - **Headers**: Add headers to the request. Click on the `Add Header` button to add headers.
           e.g. `Authorization: Bearer <token>`
        - **Request Body**: Add request body to the request. Request body should be in JSON format.Prompts wil be injected on the fly by PAIG evaluation.
           e.g. `{"ai_application_name": "sales_model", "prompt": "{{prompt}}"}`
        - **Transform Response**: Enter valid JSONPath expression to extract the response from the GenAI application response.
           e.g. 
           
            `json.messages && json.messages.length > 0 ? (json.messages.find(message => message.type === 'reply') || {}).content || "No reply found.: "No response from the server."`


:octicons-tasklist-16: **What Next?**

<div class="grid cards" markdown>

-   :material-book-open-page-variant-outline: __Read More__

    [Create Security Evaluation](create-security-evaluation.md)

</div>