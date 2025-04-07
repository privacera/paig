---
title: Integrating PAIG with Guardrails
icon: material/vector-combine
---

PAIG Guardrails are built to enforce safeguards and restrict specific topics,
ensuring the secure and responsible use of your generative AI applications. You can configure the following policies in
guardrails to avoid undesirable and harmful content, filter out denied topics and words, and remove sensitive
information for privacy protection.

1. **Content filters**: Adjust filter strengths to block input prompts or model responses containing harmful content.


2. **Off topics**: Define a set of topics that are undesirable in the context of your application. These topics will be
blocked if detected in user queries or model responses.


3. **Word filters**: Configure filters to block undesirable words, phrases, and profanity. Such words can include 
offensive terms, competitor names etc.


4. **Sensitive information filters**: Block or mask sensitive information such as personally identifiable information
(PII) or custom regex in user inputs and model responses.


5. **Prompt safety**: Can help you detect and filter prompt attacks and prompt injections. Helps detect prompts that are
intended to bypass moderation, override instructions, or generate harmful content.

In addition to the above policies, you can also configure the messages to be returned to the user if a user input or
model response is in violation of the policies defined in the guardrail.

## Customizable User Feedback:

In addition to the above policies, you can also configure the messages to be returned to the user if a user input or
model response is in violation of the policies defined in the guardrail.

## AWS Bedrock Integration and Easy Guardrails Setup:

Using PAIG Guardrails, users can seamlessly integrate with AWS, enabling a secure and compliant connection for
AWS Bedrock Guardrails. This integration allows users to leverage AWS’s guardrails for ensuring strict adherence
to content moderation and safety protocols.

PAIG Guardrails offer a straightforward configuration process, making it easy for users to set up AWS guardrails for
content filters, topic restrictions, word filters and prompt safety. With this end-to-end integration, users can
implement robust safeguards effortlessly while maintaining flexibility in their AI interactions.

By integrating PAIG Guardrails with AWS Bedrock and other AI solutions, businesses can ensure responsible AI usage while
enhancing security, compliance, and user experience. For more info on how to setup AWS connection and use it further
for managing guardrails, refer to the [Managing Guardrails](../../user-guide/manage-guardrails/index.md).

The [User Guide](../../user-guide/manage-guardrails/guardrails.md) provides additional details and use cases of the PAIG
Guardrails and integration with AWS bedrock guardrails.

---
:octicons-tasklist-16: **What Next?**

<div class="grid cards" markdown>

-   :material-book-open-page-variant-outline: __Read More__

    [User Guide](../../user-guide/manage-guardrails/guardrails.md)

-   :material-lightning-bolt-outline: __How To__

    [Manage Guardrails](../../user-guide/manage-guardrails/index.md)
