---
title: Manage GenAI Application Policies
#icon: material/checkbox-multiple-outline
---

# Manage Guardrail Policies(Guardrail configurations)

Once you added basic information, navigate to the next screen for adding guardrail configurations for content filtering,
sensitive data filtering, prompt safety, denied topics, and denied terms by clicking on the continue button.

Each configuration page includes a ==**Select Response**== option, allowing you to define the default response triggered when
the guardrail is activated. While a predefined response is set by default, you have the flexibility to select an
alternative response or create a custom one on the [Template](/#/response_templates) page.


## Content Filters
Here you can enable the detection and blocking of harmful user inputs and model responses. Increase filter strength to
enhance the likelihood of filtering harmful content in specific categories. This applies to both prompts and responses.

- **Purpose**: Content filtering helps detect and block harmful user inputs and AI-generated responses, ensuring a safer
interaction with generative AI applications. By filtering inappropriate content, this feature enhances security,
compliance, and responsible AI usage.
- **Functionality**: You can enable content filtering to automatically identify and restrict harmful prompts and
responses. The filter strength can be adjusted to increase the likelihood of detecting and blocking undesirable content
within specific categories. These filters apply to both user inputs and AI outputs.
- **Management**: Content filtering settings allow you to fine-tune detection levels based on your application’s needs. Administrators can enable or disable this content filter and can also modify the individual filter strength to balance strictness and flexibility, ensuring that your AI application effectively screens harmful content without unnecessary restrictions.

<figure markdown>
<script src="https://fast.wistia.com/embed/medias/psvjflzmmw.jsonp" async></script><script src="https://fast.wistia.com/assets/external/E-v1.js" async></script><span class="wistia_embed wistia_async_psvjflzmmw popover=true" style="display:inline-block;height:106px;position:relative;width:150px">&nbsp;</span>
<figcaption>How to add Guardrails</figcaption>
</figure>

### Filter strength
The filter strength can be set to Low, Medium, or High, and you have the flexibility to apply the same setting for both
user prompts and model responses or configure them separately.

Every input and output statement is evaluated and classified into one of four confidence levels (`NONE, LOW, MEDIUM,
HIGH`) for each harmful content category.

- **For example**, If a statement is categorized as **Hate** with `HIGH` confidence, it strongly indicates hateful content.
A single statement can fall under multiple categories with different confidence levels.

- For instance, a statement might be classified as:
  - **Hate** – HIGH confidence
  - **Insults** – LOW confidence
  - **Sexual** – NONE confidence
  - **Violence** – MEDIUM confidence

This multi-category classification ensures a nuanced assessment, allowing for more precise content filtering.


## Sensitive Data Filtering
This enables the detection and blocking of sensitive data. Configure actions such as masking or redacting detected data
to suit your needs. This functionality consists of two components: elements and regex, working together to ensure
comprehensive coverage. This applies to both prompts and responses.

- **Purpose**: Sensitive Data Filtering ensures the detection and management of sensitive information within user
prompts and AI-generated responses. This helps protect confidential data, enforce privacy policies, and maintain
compliance with security regulations.
- **Functionality**: This feature enables the identification and handling of sensitive data through configurable actions
such as redacting or masking detected information. It operates using two key components: **elements** (predefined sensitive
data types) and **regex** (custom patterns), working together to provide comprehensive protection. Sensitive data filtering
applies to both inputs and outputs, ensuring privacy and security across interactions.
- **Management**: In the Sensitive Data Filtering settings, administrators can enable or disable filters and create
custom rules based on their specific requirements. Each filter element can be configured with different actions such
as `allowing, blocking, or redacting` detected sensitive data. Admins can also define specific data types to monitor and
manage, selecting from a list of predefined sensitive elements or adding custom regex patterns for enhanced flexibility.

<figure markdown>
<script src="https://fast.wistia.com/embed/medias/c02mx4eyyn.jsonp" async></script><script src="https://fast.wistia.com/assets/external/E-v1.js" async></script><span class="wistia_embed wistia_async_c02mx4eyyn popover=true" style="display:inline-block;height:106px;position:relative;width:150px">&nbsp;</span>
<figcaption>How to add Guardrails</figcaption>
</figure>

### Adding New Elements
Click on the ==**ADD ELEMENT**== button located at the top right of the section to introduce new restriction elements
for sensitive data filtering. Fill in the necessary details including Sensitive data (selected from a list available in
the __Account -> Sensitive Data__ page), and the restriction actions `ALLOW, DENY, or REDACT`.

### Adding New REGEX Elements
Click on the **REGEX** TAB right to the **ELEMENTS** on sensitive data filtering page. Then click the
==**ADD REGEX**== button located at the top right of the section to introduce new restriction elements to block content
matching with the provided regex. 
Fill in the necessary details including Name, Description, Regex Pattern, and the restriction actions
`ALLOW, DENY, or REDACT`


## Off-topic Filters
Utilize customizable filters with off-topics with sample phrases to enforce guardrails. Add unwanted topics to a deny
list to automatically block associated keywords. This applies to both prompts and responses.

- **Purpose**: Off-topic filtering allows you to enforce guardrails by blocking specific topics from user prompts and
AI-generated responses. By defining restricted topics and associated keywords, you can ensure that conversations stay
relevant and aligned with your application’s intended use.
- **Functionality**: Off-topic restrictions work by detecting predefined topics and their associated phrases within user
interactions. You can add unwanted topics to a deny list, automatically preventing discussions related to them.
Each denied topic consists of a name, a definition (up to 200 characters), and sample phrases (up to five) that
illustrate the type of content to be filtered.
  - **For example**:
    - **Topic Name**: Political Discussions
    - **Definition**: Covers conversations about political events, figures, ideologies, or government policies.
      - **Sample Phrases**:
        1. What are your thoughts on the upcoming elections?
        2. Should I vote for a particular party?
        3. Explain the impact of recent government policies.
- **Management**: In the Off-Topic Filtering section, administrators can enable or disable predefined restrictions
or create new ones tailored to their needs. Admins can refine filtering rules by adjusting sample phrases and
keywords, ensuring accurate detection and enforcement of content restrictions across user interactions.

<figure markdown>
<script src="https://fast.wistia.com/embed/medias/7xal6pacrh.jsonp" async></script><script src="https://fast.wistia.com/assets/external/E-v1.js" async></script><span class="wistia_embed wistia_async_7xal6pacrh popover=true" style="display:inline-block;height:106px;position:relative;width:150px">&nbsp;</span>
<figcaption>How to add Guardrails</figcaption>
</figure>

### Adding New Off-Topic
Click on the ==**ADD OFF TOPIC**== button located at the top right of the section to introduce new restrictions for denied topics. 
Fill in the necessary details including **Topic name**, **Definition**, and **Sample phrases**.


## Denied Terms
Use customizable filters with specified terms or keywords and phrases to enforce restrictions. Add unwanted terms to a
deny list to automatically block related keywords or phrases. This applies to both prompts and responses.

- **Purpose**: Denied Terms filtering helps enforce guardrails by restricting specific words, and phrases in both user
prompts and AI-generated responses. This feature ensures that conversations remain appropriate, compliant, and aligned
with your application’s guidelines by automatically blocking undesirable content.
- **Functionality**: You can define customizable filters using specific terms to detect and block unwanted words or
phrases. By adding terms to a deny list, the system automatically prevents interactions that contain restricted content.
This applies to both inputs and outputs, helping to maintain content integrity and prevent the spread of inappropriate
or sensitive topics.
- **Management**: In the Denied Terms section, administrators can enable or disable the denied term filter or create
custom restrictions by adding specific keywords or phrases. Each denied term can be configured with different actions
such as `blocking`, `redacting`, or `allowing` detected content. Admins can continuously update the deny list to refine
filtering rules, ensuring that the application enforces content restrictions effectively and adapts to evolving
requirements.

<figure markdown>
<script src="https://fast.wistia.com/embed/medias/w4rpm06baf.jsonp" async></script><script src="https://fast.wistia.com/assets/external/E-v1.js" async></script><span class="wistia_embed wistia_async_w4rpm06baf popover=true" style="display:inline-block;height:106px;position:relative;width:150px">&nbsp;</span>
<figcaption>How to add Guardrails</figcaption>
</figure>

### Adding New Term
Click on the ADD TERMS button located at the top right of the section of the Terms to introduce new restrictions for
denied terms. Fill in the necessary details including **Term names**, **Phrases**, and **keywords**. You can add phrases
of up to three words per entry, with a maximum of 10,000 entries in the custom word filter.


## Profanity Filter
Detects and filters offensive language to prevent unsuitable content from being displayed. 

- **Purpose**: The Profanity Filter helps maintain a respectful and appropriate user experience by detecting and
blocking offensive language in both user inputs and AI-generated responses. This ensures that interactions remain
professional, inclusive, and free from inappropriate content.
- **Functionality**: This filter automatically identifies and restricts the use of offensive words and phrases based on
a continuously updated list that aligns with widely accepted definitions of profanity. When enabled, any detected
profane language is blocked.
- **Management**: In the Profanity Filter settings, administrators can enable or disable the filter as needed.
The profanity list is regularly updated, but admins can also customize restrictions by adding specific terms to enhance
filtering. Based on application needs, admins can configure the denied term filter to `block` content entirely.


## Prompt Safety
Guardrails prevent prompt injections by validating inputs, filtering harmful patterns, and analyzing context to block
malicious instructions. They ensure user input cannot manipulate or mislead the model into unsafe behavior.

- **Purpose**: Guardrails defend against prompt injection attacks by validating user inputs, identifying harmful
patterns, and analyzing contextual cues to prevent malicious instructions from manipulating AI behavior.
This ensures that the model remains secure and resistant to unauthorized influence.
- **Functionality**: These safeguards detect and block attempts to override system instructions, preventing AI-generated
responses from being misled into unsafe or unintended behavior. By filtering manipulative prompts, guardrails help
maintain model integrity and ensure adherence to security policies.
- **Management**: The Prompt Attack Sensitivity slider allows administrators to fine-tune the system’s defense
mechanisms against prompt injection attempts. Increasing sensitivity applies stricter validation and filtering,
enhancing security against advanced attacks. Lower sensitivity provides more flexibility in user interactions but may
reduce protection against sophisticated manipulation tactics. Admins can adjust this setting based on the specific
security needs of their application.


<figure markdown>
<script src="https://fast.wistia.com/embed/medias/721rgfag3h.jsonp" async></script><script src="https://fast.wistia.com/assets/external/E-v1.js" async></script><span class="wistia_embed wistia_async_721rgfag3h popover=true" style="display:inline-block;height:106px;position:relative;width:150px">&nbsp;</span>
<figcaption>How to add Guardrails</figcaption>
</figure>

---
:octicons-tasklist-16: **What Next?**

<div class="grid cards" markdown>

-   :material-book-open-page-variant-outline: __Read More__

    [Reporting](../reporting/)

</div>