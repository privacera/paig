---
title: Quick Start with PAIG
icon: material/run-fast
---

# Quick Start with PAIG

Welcome to the Quick Start Guide for PAIG. Whether you are looking to integrate with a GenAI application quickly or want
to explore the capabilities of PAIG, this guide provides two convenient options: using a Google Colab Notebook for a
cloud-based approach, or a downloadable local sample application for those who prefer a more hands-on experience.

## Configuration Requirements

Before you begin with either the Google Colab Notebook or the local sample application, you need to complete the following setup steps in PAIG:

1. **Create a Privacera Shield Application**: This is necessary to generate the appropriate configuration files for your environment.

2. **Download Configuration Files**: Essential for connecting your chosen environment to PAIG, these files help ensure that your settings are correctly aligned with PAIG's capabilities.

<!-- md:go_to_paig /#/ai_applications:Go To PAIG -->

As a first step, you need to add your AI Application in PAIG and we will use that application to integrate PAIG.
If you already added the Application to the PAIG, then you can skip this step.

--8<-- "docs/integration/snippets/create_application.md"

## **Downloading Privacera Shield Configuration File**

<!-- md:go_to_paig /#/ai_applications:Go To PAIG -->

--8<-- "docs/integration/snippets/download_application_config.md"

## **Quick Starts**

All the Quick Start notebooks and sample applications are available in the GitHub repository https://github.com/privacera/notebooks/tree/main

Here are some of the Quick Starts for trying out the integrations with PAIG.

{{ read_csv('snippets/quick-starts.csv') }}


## **Quick Starts - For AWS**

For AWS, you need IAM roles for many services. You can go to https://github.com/privacera/notebooks/tree/main/aws and 
follow the instructions to set up the AWS services.


