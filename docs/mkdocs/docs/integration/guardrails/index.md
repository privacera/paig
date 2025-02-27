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


3. **Word filters**: Configure filters to block undesirable words, phrases, and profanity. Such words can include offensive
terms, competitor names etc.


4. **Sensitive information filters**: Block or mask sensitive information such as personally identifiable information (PII)
or custom regex in user inputs and model responses.


5. **Prompt safety**: Can help you detect and filter prompt attacks and prompt injections. Helps detect prompts that are
intended to bypass moderation, override instructions, or generate harmful content.

In addition to the above policies, you can also configure the messages to be returned to the user if a user input or
model response is in violation of the policies defined in the guardrail.

The [User Guide](../../user-guide/manage-guardrails/guardails.md) provides additional details and use cases of the integration.

---
:octicons-tasklist-16: **What Next?**

<div class="grid cards" markdown>

-   :material-book-open-page-variant-outline: __Read More__

    [User Guide](../../user-guide/securing-ai-applications-with-guardails.md)

-   :material-lightning-bolt-outline: __How To__

    [Manage Guardrails](../../user-guide/manage-guardrails/guardrails.md)
