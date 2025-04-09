import AWS_BEDROCK from 'common-ui/images/aws-bedrock.svg';
import PAIG from 'common-ui/images/monogram-lp-logo.svg';

const UI_CONSTANTS = {
    PAIG_LENS: 'PAIG_LENS',
    PAIG_NAVIGATOR: 'PAIG_NAVIGATOR',
    PAIG_GUARD: 'PAIG_GUARD',
    SETTINGS: 'SETTINGS',
    DASHBOARD: 'DASHBOARD',
    AI_APPLICATIONS: 'AI_APPLICATIONS',
    USER_MANAGEMENT: 'USER_MANAGEMENT',
    PORTAL_USERS: 'PORTAL_USERS',
    PORTAL_GROUPS: 'PORTAL_GROUPS',
    SHIELD_CONFIGURATION: 'SHIELD_CONFIGURATION',
    AI_POLICIES: 'AI_POLICIES',
    SECURITY: 'SECURITY',
    AUDITS: 'AUDITS',
    COMPLIANCE: 'COMPLIANCE',
    SENSITIVE_DATA: 'SENSITIVE_DATA',
    META_DATA: 'META_DATA',
    META_DATA_VALUES: 'META_DATA_VALUES',
    ADMIN_AUDITS: 'ADMIN_AUDITS',
    DOCS: 'DOCS',
    ACCOUNT: 'ACCOUNT',
    VECTOR_DB: 'VECTOR_DB',
    REPORTING: 'REPORTING',
    REPORTS: 'REPORTS',
    BUILT_IN_REPORTS: 'BUILT_IN_REPORTS',
    SAVED_REPORTS: 'SAVED_REPORTS',
    AI_APPLICATIONS_PERMISSIONS: 'AI_APPLICATIONS_PERMISSIONS',
    VECTOR_DB_PERMISSIONS: 'VECTOR_DB_PERMISSIONS',
    EVALUATION: 'EVALUATION',
    EVALUATION_CONFIG: 'EVALUATION_CONFIG',
    EVALUATION_ENDPOINT: 'EVALUATION_ENDPOINT',
    EVALUATION_SECURITY: 'EVALUATION_SECURITY',
    EVALUATION_REPORTS: 'EVALUATION_REPORTS',
    EVALUATION_REPORT_OVERVIEW: 'EVALUATION_REPORT_OVERVIEW',
    EVALUATION_REPORT_DETAILS: 'EVALUATION_REPORT_DETAILS',
    USERS: 'USERS',
    GUARDRAILS: 'GUARDRAILS',
    RESPONSE_TEMPLATES: 'RESPONSE_TEMPLATES',
    GUARDRAIL_CONNECTION_PROVIDER: 'GUARDRAIL_CONNECTION_PROVIDER'
}

const PERMISSIONS = {
    READ: 'read',
    UPDATE: 'update',
    DELETE: 'delete',
    EXPORT: 'export',
}

const FEATURE_PERMISSIONS = {
    PORTAL: {
        DASHBOARD: {PROPERTY: 'portal.dashboard'},
        DOCS: {PROPERTY: 'portal.docs'},
        REPORTS: {PROPERTY: 'portal.reports'}
    },
    GOVERNANCE: {
        AI_APPLICATIONS: {PROPERTY: 'governance.ai_applications'},
        AI_POLICIES: {PROPERTY: 'governance.ai_policies'},
        VECTOR_DB: {PROPERTY: 'governance.vector_db'},
        VECTOR_DB_POLICIES: {PROPERTY: 'governance.vector_db_policies'},
        EVALUATION_CONFIG: {PROPERTY: 'governance.evaluation_config'},
        EVALUATION_REPORTS: {PROPERTY: 'governance.evaluation_reports'},
        GUARDRAILS: {PROPERTY: 'governance.guardrails'}
    },
    AUDITS: {
        SECURITY: {PROPERTY: 'audits.security'}
    },
    COMPLIANCE: {
        ADMIN_AUDITS: {PROPERTY: 'compliance.admin_audits'}
    },
    ACCOUNT: {
        SHIELD_CONFIGURATION: {PROPERTY: 'account.shield_configuration'},
        USER: {PROPERTY: 'account.user'},
        GROUP: {PROPERTY: 'account.group'},
        SENSITIVE_DATA: {PROPERTY: 'account.sensitive_data'},
        META_DATA: {PROPERTY: 'account.meta_data'},
        META_DATA_VALUES: {PROPERTY: 'account.meta_data_values'}
    }
}

const REGEX = {
    VALID_URL: /^(https?):\/\/[^\s/$.?#].[^\s]*$/,
    EMAIL: /^[\w]([\-\.\w\+])+@[\w]+[\w\-]+[\w]*\.([\w]+[\w\-]+[\w]*(\.[a-z][a-z|0-9]*){0,4}?)$/,
    ACCOUNT_NAME: /^[a-z0-9\d-_]+$/i,
    FIRSTNAME : /^([A-Za-z0-9_]|[\u00C0-\u017F])([a-zA-Z0-9\s_. -@]|[\u00C0-\u017F])+$/i,
    LASTNAME : /^([A-Za-z0-9_]|[\u00C0-\u017F])([a-zA-Z0-9\s_. -@]|[\u00C0-\u017F])+$/i,
    PASSWORD : /^$|^(?=.*[A-Za-z])(?=.*\d).{8,255}$/i
}

const SUBSCRIPTION_TYPE = {}

const ERROR_MESSAGE = {}

const PROMPT_REPLY_TYPE = {
    PROMPT: "prompt",
    REPLY: "reply",
    ENRICH_PROMPT: "enriched_prompt",
    RAG: "rag"
}
  
const PROMPT_REPLY_ACTION_TYPE = {
    ALLOW: {VALUE: "ALLOW", LABEL: "Allow"},
    DENY: {VALUE: "DENY", LABEL: "Deny"},
    REDACT: {VALUE: "REDACT", LABEL: "Redact"},
}
const CATOGORIES_KEY_LABEL = {
    user_name: { key: 'user_name', label: 'user_name' },
    application: {key: 'application', label: 'application'},
    datazone_name: {key: 'datazone_name', label: 'datazone_name'},
    group_name: {key: 'group_name_split', label: 'group_name'},
    tags: {key: 'tags_split', label: 'tags'}
}
const CONDITIONS_CATEGORIES = {
    ALERTS_CATEGORY: [{ category: CATOGORIES_KEY_LABEL.user_name.label, type: "textoptions"}, { category: CATOGORIES_KEY_LABEL.application.label, type: "textoptions" }]
}

const MESSAGE_RESULT_TYPE = {
    ALLOWED: {NAME: 'allowed', LABEL: 'Allowed', COLOR: '#6FF17C'},
    DENIED: {NAME: 'denied', LABEL: 'Denied', COLOR: '#FD8A5B'},
    MASKED: {NAME: 'masked', LABEL: 'Masked', COLOR: '#69C9F9'}
}

const DEPLOYMENT_TYPE = {
    CLOUD: {NAME: 'CLOUD', VALUE: 'CLOUD', LABEL: 'Cloud'},
    SELF_MANAGED: {NAME: 'SELF_MANAGED', VALUE: 'SELF_MANAGED', LABEL: 'Self Managed'},
}

const METADATA_DATA_TYPE = {
    SINGLE_VALUE: {TYPE: 'single_value', LABEL: 'Single Value'},
    MULTI_VALUE: {TYPE: 'multi_value', LABEL: 'Multi Value'}
}

const FEATURE_PROPERTIES_MAPPING = {
    'Self-Managed Shield': 'SHIELD_CONFIGURATION',
    'Vector DB': 'VECTOR_DB'
}

const VECTOR_DB_TYPES = {
    OPENSEARCH: {TYPE: 'OPENSEARCH', LABEL: 'OpenSearch'},
    MILVUS: {TYPE: 'MILVUS', LABEL: 'Milvus'},
    SNOWFLAKE_CORTEX: {TYPE: 'SNOWFLAKE_CORTEX', LABEL: 'Snowflake Cortex'}
}

const REPORT_DETAILS = {
    USER_GEN_AI_APPLICATION_SUMMARY: {
        NAME: 'user_gen_ai_application_summary',
        LABEL: 'Summary of Users who accessed the GenAI Application',
        DESCRIPTION: 'This report provides users, who have accessed for GenAI application.',
        DOWNLOAD_FILE_NAME: 'privacera_users_application_gen_ai_summary_report'
    },
    SENSITIVE_DATA_GEN_AI_SUMMARY: {
        NAME: 'sensitive_data_gen_ai_summary',
        LABEL: 'Sensitive Data Access Overview',
        DESCRIPTION: 'Track and analyze access patterns to sensitive data across applications, users, and interactions within your GenAI applications, ensuring comprehensive oversight and robust data security management.',
        DOWNLOAD_FILE_NAME: 'privacera_sensitive_data_gen_ai_summary_report'
    },
    USERS_WHO_VIEWED_USER_CONTENT_SUMMARY: {
        NAME: 'users_who_viewed_user_content_summary', 
        LABEL: 'Content Viewing Compliance Report',
        DESCRIPTION: 'Gain critical compliance insights with a focus on the viewing of potentially sensitive user-generated content. This report outlines admin interactions, message views, and user content engagement, all while adhering to strict data privacy and security standards.',
        DOWNLOAD_FILE_NAME: 'privacera_users_who_viewed_user_content_summary_report'
    }
}

const ENUMS = {
    CLASS_TYPE_REPORT_CONFIG: 39
}

const SCAN_SUMMARY_SOLR_FIELDS = {};

const SCHEDULE_FOR = {
    DASHBOARD_REPORT: {label: 'DASHBOARD_REPORT', value: 'DASHBOARD_REPORT'}
}

const DATE_UNITS_GAP = {
    QUARTER: {VALUE: "quarter", format: "MMM YYYY"},
    MONTH: {VALUE: "month", format: "MMM YYYY"},
    WEEK:  {VALUE: "week", format: "MMMM D"},
    DAY: {VALUE: "day", format: "MMM DD"},
    HOUR: {VALUE: "hour", format: "HH:mm"}
}

const GRAPH_COLOR_PALLET = [
  "#2CA02C",
  "#FF9335",
  "#41546F",
  "#54236B",
  "#F59E0B",
  "#8085E8",
  "#FFD500",
  "#EC5B2A",
  "#DE2C82",
  "#E4D354",
  "#AA38E0",
  "#314ED3",
  "#31ACD3",
  "#4CE249",
  "#91E8E1",
  "#001A6E",
  "#A36557",
  "#B4D2E1",
  "#D62728",
  "#42B19D",
  "#999999",
  "#91E8E1",
  "#FFC0A5",
  "#746637",
  "#89D8FF",
  "#D0D0D0",
  "#DA8BFF",
  "#999999",
];

const ACTION_TYPE = {
    CREATE: { VALUE: 'CREATE', LABEL: 'created', COLOR: "#dff0d8" },
    UPDATE: { VALUE: 'UPDATE', LABEL: 'updated', COLOR: "#fef7cd" },
    DELETE: { VALUE: 'DELETE', LABEL: 'deleted', COLOR: "#ffefe4" },
    REVIEW: { VALUE: 'REVIEW', LABEL: 'viewed', COLOR: "#e0f7fa" },
    DOWNLOAD: { VALUE: 'DOWNLOAD', LABEL: 'downloaded', COLOR: "#e0f7fa" }
};

const OBJECT_TYPE_MAPPING = {
    USER: { VALUE: 'USER', LABEL: 'User' },
    GROUP: { VALUE: 'GROUP', LABEL: 'Group' },
    GROUP_USER: { VALUE: 'GROUP_USER', LABEL: 'Group' },
    AI_APPLICATION: { VALUE: 'AI_APPLICATION', LABEL: 'AI Application' },
    AI_APPLICATION_POLICY: { VALUE: 'AI_APPLICATION_POLICY', LABEL: 'Policy' },
    AI_APPLICATION_CONFIG: { VALUE: 'AI_APPLICATION_CONFIG', LABEL: 'Config' },
    VECTOR_DB: { VALUE: 'VECTOR_DB', LABEL: 'VectorDb' },
    VECTOR_DB_POLICY: { VALUE: 'VECTOR_DB_POLICY', LABEL: 'VectorDb Policy' },
    META_DATA: { VALUE: 'META_DATA', LABEL: 'Meta Data' },
    META_DATA_ATTR_VALUE: { VALUE: 'META_DATA_ATTR_VALUE', LABEL: 'Meta Data Value' },
    SHIELD_AUDIT: { VALUE: 'SHIELD_AUDIT', LABEL: 'Security Audit' },
    SHIELD_AUDIT_REPORT: { VALUE: 'SHIELD_AUDIT_REPORT', LABEL: 'Shield Audit Report' },
    SELF_MANAGED_SHIELD_CONFIG: { VALUE: 'SELF_MANAGED_SHIELD_CONFIG', LABEL: 'Self Managed Shield Config' },
    PRIVACERA_SHIELD_CONFIG: { VALUE: 'PRIVACERA_SHIELD_CONFIG', LABEL: 'Privacera Shield Config' },
    SENSITIVE_DATA: { VALUE: 'SENSITIVE_DATA', LABEL: 'Sensitive Data' },
    TENANT_FEATURE: { VALUE: 'TENANT_FEATURE', LABEL: 'Tenant Feature' },
    ADMIN_AUDIT_REPORT: { VALUE: 'ADMIN_AUDIT_REPORT', LABEL: 'Admin Audit Report' }
};

const ADMIN_AUDITS_FIELDS_TO_HIDE_MAPPING = {
    CREATE: ['updateTime', 'createTime', 'tenantId', 'rangerPolicyIds', 'defaultRangerPolicyId'],
    UPDATE: ['updateTime', 'createTime', 'tenantId', 'tntId', 'pcloudUserId', 'pCloudGroupId'],
    DELETE: ['updateTime', 'createTime', 'tenantId', 'rangerPolicyIds', 'defaultRangerPolicyId', 'tntId'],
    DOWNLOAD: ['updateTime', 'createTime', 'tenantId', 'shieldApiKeyId', 'shieldRSASelfManagedKeyId', 'shieldRSAAuditSvcKeyId', 'shieldServerKeyId', 'shieldPluginKeyId', 'dateOfDownload'],
    REVIEW: ['eventTime', 'logTime', 'rangerAuditIds', 'rangerPolicyIds', 'paigPolicyIds', 'tenantId', 'clientApplicationKey', 'clientApplicationName', 'clientHostname', 'clientIp', 'eventId', 'numberOfTokens', 'encryptionKeyId', 'transactionSequenceNumber']
}

const REPORT_GRID_LABELS = {
    ADMIN_CONTENT_COMPLIANCE: {LABEL: "Admin Content Compliance Views", TOOLTIP: "Tracks the number of administrators reviewing user content for compliance, indicating diligence in monitoring sensitive user-generated messages."},
    REVIEWED_MESSAGE: {LABEL: "Reviewed Messages Count", TOOLTIP: "Total count of user messages reviewed, a key metric in compliance and content monitoring within the network."},
    UNIQ_USERS: {LABEL: "Unique User Content Reviews", TOOLTIP: "The number of distinct users whose content was subject to review, signifying the extent of compliance-driven content monitoring."},
    COMPLIANCE_REVIEW_TRENDS: {LABEL: "Compliance Review Trend Over Time", TOOLTIP: "Visualizes the frequency of user content reviewed by admins over time, aiding in identifying patterns and ensuring consistent content compliance checks."},
    TOP_REVIEWER_CONTENT_COMPLIANCE: {LABEL: "Top 20 Reviewers In Content Compliance", TOOLTIP: "Identifies the top 20 administrators active in content compliance reviews, crucial for understanding who is most engaged in monitoring sensitive user content."}
}

const GUARDRAIL_PROVIDER = {
    PAIG: {
        NAME: 'PAIG',
        LABEL: 'PAIG Guardrails',
        STATUS: 1,
        DEFAULT: true,
        EDITABLE: false,
        IMG_URL: PAIG,
        DESCRIPTION: 'This default guardrail provides moderate coverage in all key areas, offering a balanced solution for organizations looking for flexible, medium-level protections without heavy customization.'
    },
    AWS: {
        NAME: 'AWS',
        LABEL: 'AWS Bedrock',
        STATUS: 0,
        DEFAULT: false,
        EDITABLE: true,
        IMG_URL: AWS_BEDROCK,
        DESCRIPTION: 'AWS offers strong security and scalability, making it ideal for businesses needing flexible yet powerful solutions. It supports highly regulated industries with global coverage.'
    }/*,
    OPEN_AI: {
        NAME: 'OPEN_AI',
        LABEL: 'Open AI',
        STATUS: 0,
        DEFAULT: false,
        EDITABLE: true,
        DESCRIPTION: 'This guardrail offers robust yet flexible protection across critical areas, providing organizations with moderate, out-of-the-box safeguards that balance comprehensive coverage and adaptability without requiring extensive customization.'
    },
    LLAMA: {
        NAME: 'LLAMA',
        LABEL: 'LLAMA',
        STATUS: 0,
        DEFAULT: false,
        EDITABLE: true,
        DESCRIPTION: 'This guardrail offers robust yet flexible protection across critical areas, providing organizations with moderate, out-of-the-box safeguards that balance comprehensive coverage and adaptability without requiring extensive customization.'
    }*/
}

const GUARDRAIL_CONFIG_TYPE = {
    CONTENT_MODERATION: {NAME: 'CONTENT_MODERATION', LABEL: 'Content Moderation'},
    SENSITIVE_DATA: {NAME: 'SENSITIVE_DATA', LABEL: 'Sensitive Data'},
    OFF_TOPIC: {NAME: 'OFF_TOPIC', LABEL: 'Off-topic'},
    DENIED_TERMS: {NAME: 'DENIED_TERMS', LABEL: 'Denied Terms'},
    PROMPT_SAFETY: {NAME: 'PROMPT_SAFETY', LABEL: 'Prompt Safety'}
}

const AWS_PROVIDER_CONNECTION_CONFIG_TYPE = {
    IAM_ROLE: {TYPE: 'IAM_ROLE', LABEL: 'IAM Role'},
    ACCESS_SECRET_KEY: {TYPE: 'ACCESS_SECRET_KEY', LABEL: 'Access Key & Secret Key'},
    INSTANCE_ROLE: {TYPE: 'INSTANCE_ROLE', LABEL: 'Instance Role'}
}

const EVAL_REPORT_CATEGORIES = {
    TYPE: { multi: false, category: "Type", type: "text", key: 'category_type' },
    PROMPT: { multi: false, category: "Prompt", type: "text", key: 'prompt' },
    RESPONSE: { multi: false, category: "Response", type: "text", key: 'response' },
    SEVERITY: { multi: false, category: "Severity", type: "text", key: 'category_severity' },
}


const SEVERITY_MAP = {
    CRITICAL: {LABEL: 'Severe Failure', COLOR: '#ee8b8b', DONUTCOLOR: 'E10101'},
    HIGH: {LABEL: 'High Concern', COLOR: '#E101014D', DONUTCOLOR: 'FF6B35'},
    MEDIUM: {LABEL: 'Moderate Concern', COLOR: '#FFEDB2', DONUTCOLOR: 'FFC233'},
    LOW: {LABEL: 'Low Concern', COLOR: '#B2F0D6', DONUTCOLOR: '2CA02C'}
}

const CATEGORY_DESCRIPTIONS = {
    "Brand": "Tests focused on brand protection, including competitor mentions, misinformation, hallucinations, and model behavior that could impact brand reputation.",
    "Compliance & Legal": "Tests for LLM behavior that may encourage illegal activity, breach contractual commitments, or violate intellectual property rights.",
    "Security & Access Control": "Technical security risk tests mapped to OWASP Top 10 for LLMs, APIs, and web applications, covering SQL injection, SSRF, broken access control, and cross-session leaks.",
    "Trust & Safety": "Tests that attempt to produce illicit, graphic, or inappropriate responses from the LLM.",
    "Custom": "Configurable tests for specific policies or generating custom probes for your use case."
};

export {
    UI_CONSTANTS,
    PERMISSIONS,
    FEATURE_PERMISSIONS,
    REGEX,
    SUBSCRIPTION_TYPE,
    ERROR_MESSAGE,
    PROMPT_REPLY_TYPE,
    PROMPT_REPLY_ACTION_TYPE,
    CONDITIONS_CATEGORIES,
    CATOGORIES_KEY_LABEL,
    MESSAGE_RESULT_TYPE,
    DEPLOYMENT_TYPE,
    METADATA_DATA_TYPE,
    FEATURE_PROPERTIES_MAPPING,
    VECTOR_DB_TYPES,
    REPORT_DETAILS,
    ENUMS,
    SCAN_SUMMARY_SOLR_FIELDS,
    SCHEDULE_FOR,
    DATE_UNITS_GAP,
    GRAPH_COLOR_PALLET,
    ACTION_TYPE,
    OBJECT_TYPE_MAPPING,
    ADMIN_AUDITS_FIELDS_TO_HIDE_MAPPING,
    REPORT_GRID_LABELS,
    EVAL_REPORT_CATEGORIES,
    GUARDRAIL_PROVIDER,
    GUARDRAIL_CONFIG_TYPE,
    AWS_PROVIDER_CONNECTION_CONFIG_TYPE,
    SEVERITY_MAP,
    CATEGORY_DESCRIPTIONS
}
