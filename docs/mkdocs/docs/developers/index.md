---
title: Developers Guide to PAIG
icon: material/vector-combine
---

#  Developers Guide to PAIG
!!! tip "This section is for the AI Application developers and PAIG contributors"

    You need to have some familarity of Large Language Models (LLMs) and  need to have understanding of programming language like python.

PAIG is an open source project. We welcome contributions from the community. This section provides a guide to developers on how to contribute to the project.
This guide is intended for developers who want to contribute to the PAIG project. It provides an overview of the project, the architecture, and the development process.


PAIG has two main components:


1. **PAIG Server**: The PAIG server handles AI governance, authorization, generate audits, provides access management, analytics, and other services. It is implemented in Python using the FASTAPI framework.
2. **PAIG Client**: The PAIG client is a python library that provides an interface to the PAIG server. PAIG AI governance can be integrated into AI applications using the PAIG client.