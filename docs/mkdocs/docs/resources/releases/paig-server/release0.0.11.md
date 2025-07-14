---
title: PAIG Server 0.0.11
---

- **New Features**:
    - Configurable concurrent run limit for evaluations.
    - Validation checks to prevent creation of duplicate evaluation configs and reports.
    - Completion time display on the evaluation report detail page.
    - Categories count on the evaluation config page with clickable popup showing category type details.
    - Get Categories API with type support integrated into evaluation config.
    - Evaluation target application connection check.
    - Unique constraints added on eval-config, eval-config-history, and eval-report name columns.
    - Enhanced audit context with detailed guardrail information, including name, tags, and associated policies.

- **Improvements & Updates**:
    - Updated README.md with PowerShell and Git Bash setup instructions.
    - Made the evaluation verbose flag configurable.
    - Updated base versions of paig-authorizer-core and paig-evaluation dependencies.
    - Refactored evaluation service to support tenant ID.
    - Improved validation for evaluation target API schema.
    - Synchronized guardrail details between test input screen API and audit context.

- **Fixes**:
    - Resolved duplication issue in evaluation reports.
    - Corrected evaluation category severity count when running across multiple target applications.
    - Fixed paginated response error when request size is zero.
    - Added keep-alive timeout for Uvicorn to prevent "connection reset by peer" errors.

<div class="grid cards" markdown>
-  :material-page-previous: Prev topic: [Releases](../index.md#paig-server)
</div> 