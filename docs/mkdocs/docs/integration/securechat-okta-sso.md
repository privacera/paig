---
title: Privacera SecureChat With Okta SSO
---
# Privacera SecureChat With Okta SSO

This document provides the steps to integrate Privacera SecureChat with Okta SSO.

## Okta Profile

1. Create a application on Okta dashboard. On Okta dashboard traverse to ==**Application > application > Create App Integration**==
2. Select Sign in method as OIDC -Open Id Connect and Application type as Single-Page Application
3. Add ==**${ServerURL}/login/callback**== in Sign-in redirect URIs and Save

Please take a note of **Client ID** and other details after creation of application in Okta Dashboard

## Setup Secure Chat Configuration
Once you have done setup for your application Okta dashboard , Please provide update Secure Chat Configuration with 
details of your application. 

```yaml title="dev_openai_opensearch_config.yaml"
security:
  okta:
    enabled: "true"
    issuer: "${OKTA_ISSUER}"
    audience: "${api://default}"
    client_id: "${OKTA_CLIENT_ID}"
  username_login_enabled: "true"
  expire_minutes: 1440
```
