---
title: Managing Guardrails
---

# Managing Guardrails

To manage your Guardrails (1) you can select the **Guardrails** option from the left navigation pane in the PAIG portal.
On this page, you can view all the guardrails that are created in PAIG. From there you can either select a guardrail to
view and manage or create a new guardrail.
{ .annotate }

1.  :privacera-privacera_p: Read more about Guardrails in the [User Guide](guardrails.md) section.

## Creating a New Guardrail

<!-- md:go_to_paig /#/guardrails:Go To PAIG -->

To configure a new guardrail, go to __Application > Guardrails__ and click the ==**CREATE GUARDRAIL**== button on the
right top. This will open a dialog box where you can enter the details of the guardrail. You need to set up the
[guardrail connection](#creating-a-new-guardrail-connection) and configure the
[response template](#creating-a-new-guardrail-response-template) beforehand.

<figure markdown>
<script src="https://fast.wistia.com/embed/medias/le53t61d0n.jsonp" async></script><script src="https://fast.wistia.com/assets/external/E-v1.js" async></script><span class="wistia_embed wistia_async_le53t61d0n popover=true" style="display:inline-block;height:106px;position:relative;width:150px">&nbsp;</span>
<figcaption>How to add Guardrails</figcaption>
</figure>

{{ read_csv('snippets/create_guardrail_params.csv') }}


## Creating a New Guardrail Connection

<!-- md:go_to_paig /#/guardrails_connection_provider:Go To PAIG -->

To create a new guardrail connection for AWS, go to __Account > Guardrail Connections__ and click on ==**AWS Bedrock**==
from Available Providers. This will open a dialog box where you can enter the details of the guardrail connection.

<figure markdown>
<script src="https://fast.wistia.com/embed/medias/dcmt7pwcny.jsonp" async></script><script src="https://fast.wistia.com/assets/external/E-v1.js" async></script><span class="wistia_embed wistia_async_dcmt7pwcny popover=true" style="display:inline-block;height:106px;position:relative;width:150px">&nbsp;</span>
<figcaption>How to add Guardrail Connection</figcaption>
</figure>

{{ read_csv('snippets/create_guardrail_connection_params.csv') }}


## Creating a New Guardrail Response Template

<!-- md:go_to_paig /#/response_templates:Go To PAIG -->

To create a new response template for Guardrails, go to __Application > Response Template__ and click on the
==**CREATE TEMPLATE**== button at the right top. This will open a dialog box where you can enter the details of the
guardrail response template.

<figure markdown>
<script src="https://fast.wistia.com/embed/medias/7tf1lxzroc.jsonp" async></script><script src="https://fast.wistia.com/assets/external/E-v1.js" async></script><span class="wistia_embed wistia_async_7tf1lxzroc popover=true" style="display:inline-block;height:106px;position:relative;width:150px">&nbsp;</span>
<figcaption>How to add Guardrail Response Template</figcaption>
</figure>

{{ read_csv('snippets/create_guardrail_response_template_params.csv') }}


## Troubleshooting

### AWS Credentials Issues

/// details | Invalid or Expired Security Token
- **Error**: "Unable to verify connection. The security token included in the request is invalid/expired"
- **Solution**: Update the AWS credentials in your Guardrail Connection with valid credentials
///

/// details | Invalid Authentication Credentials
- **Error**: "The provided authentication credentials for the associated connection are invalid"
- **Solution**: Verify and update the AWS credentials in your Guardrail Connection
///

/// details | Access Denied
- **Error**: "Access Denied for the associated connection"
- **Solution**: Ensure you have write access to AWS Bedrock Guardrails
///

### Guardrail Configuration Issues

/// details | Duplicate Guardrail Name
- **Error**: "A guardrail with this name may already exist"
- **Solution**: Choose a different name as another user may have already created a guardrail with the same name in the same AWS account
///

/// details | Duplicate Denied Terms
- **Error**: "Validation error: Custom words cannot have case-insensitive duplicates"
- **Solution**: Review your guardrail configuration and remove any duplicate terms from the denied words list
///

/// details | Topic definition length exceeded
- **Error**: "Validation error: Failed to satisfy constraint: Member must have length less than or equal to 200"
- **Solution**: Reduce the length of the topic definition to meet the character limit

/// details | Guardrails Not Applied
- **Error**: "Guardrails not applied in the AI application"
- **Solution**: Check the guardrail association by either:
    1. Visiting the AI application page
    2. Editing the Guardrail configuration and selecting the AI Application
///