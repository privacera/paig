function getBaseURL() {
    let baseUrl = "";
    /* Checking for "public" in base url if exists then ignore &
     * make the base url as "/"
     */
    if (window.location.pathname.indexOf("/public") === 0) {
        baseUrl = window.location.origin;
    } else {
        baseUrl = window.location.origin +
            window.location.pathname.substring(window.location.pathname
                .indexOf('/', 2), 0);
    }
    return baseUrl;
}

const STORE_CONFIG = {
    urlRoot: getBaseURL(),
    debug: false,
    pageSize: 25
}

const DATE_TIME_FORMATS = {
    TIME_FORMAT: 'HH:mm:ss.SSS',
    DATEFORMAT: 'YYYY-MM-DD HH:mm:ss.SSS',
    DATE_FORMAT: 'YYYY-MM-DD HH:mm:ss',
    DATE_TIME_FORMAT: 'MM/DD/YYYY HH:mm a',
    DATE_ONLY_FORMAT: 'YYYY-MM-DD',
    DOWNLOAD_REPORT_DATETIME_FORMAT: 'YYYY_MM_DD_HH_mm',
    DATE_FORMAT_UNIFIED_UI: 'YYYY/MM/DD HH:mm:ss',
    POD_REQUEST_DATE_FORMAT: 'MM/DD/YYYY hh:mm:ss A',
    DATE_FORMAT_ISO: "YYYY-MM-DDTHH:mm:ss"
}

const STATUS = {
    disabled: {label: 'Disable', value: 0, booleanValue: false, name:'Disabled'},
    enabled: {label: 'Enable', value: 1, booleanValue: true, name:'Enabled'}
}

const DEFAULTS = {
    DEFAULT_FIELD_MAX_LENGTH: 256,
    DEFAULT_PAGE_SIZE: 15,
    DEFAULT_LOOKUP_PAGE_SIZE: 100,
    MAX_PAGE_SIZE: Number.MAX_SAFE_INTEGER,
    READ_FILESIZE: 10000,
    DOWNLOAD_FILESIZE: 209715200,
    UPLOAD_FILESIZE: 262144000,
    RESOURCE_SPLIT_JOIN_BY: '\\',
    FILESIZE: 10000,
    EXPORT_CSV_DEFAULT_ROWS: 999999999,
    DEFAULT_DATASERVER_REQUEST_CREDIT: 1000000,
    OFFLINE_REPORTS_DEFAULT_THRESHOLD: 5000,
    MAX_PAGINATION_LIMIT: 999999999,
    SEARCH_TXT: 'Type to search',
    AUTO_HIDE_DURATION: 10000,
    SUPPORT_LOG_DOWNLOAD_MAX_DAYS: 120,
    DEFAULT_PAGE_SIZE_MAX: 9999
}

const DEFAULT_FIELD_MAX_LENGTH = 256;
const DEFAULT_PAGE_SIZE = 15;
const DEFAULT_LOOKUP_PAGE_SIZE = 50;
const MAX_PAGE_SIZE = Number.MAX_SAFE_INTEGER;
const READ_FILESIZE = 10000;
const DOWNLOAD_FILESIZE = 209715200;
const UPLOAD_FILESIZE = 262144000;
const RESOURCE_SPLIT_JOIN_BY = '\\';
const FILESIZE = 10000;
const EXPORT_CSV_DEFAULT_ROWS = 999999999;
const DEFAULT_DATASERVER_REQUEST_CREDIT = 1000000;
const OFFLINE_REPORTS_DEFAULT_THRESHOLD = 5000;
const MAX_PAGINATION_LIMIT = 999999999;
const SEARCH_TXT = 'Type to search';
const AUTO_HIDE_DURATION = 10000;
const SUPPORT_LOG_DOWNLOAD_MAX_DAYS = 120;

const SIZE_30 = 30;
const SIZE_50 = 50;
const SIZE_75 = 75;
const SIZE_100 = 100;

const ROWS_PER_PAGE = [{
    rows: DEFAULTS.DEFAULT_PAGE_SIZE
}, {
    rows: SIZE_30
}, {
    rows: SIZE_50
}, {
    rows: SIZE_75
}, {
    rows: SIZE_100
}];

const APPLICATION_TYPE = {
    LDAP: {TYPE: 'ldap', MAX_LIMIT: 1},
    DATASERVER:{TYPE: 'dataserver', MAX_LIMIT: 1},
    POLICYSYNC:{TYPE: 'policysync', MAX_LIMIT: -1},
    POLICYSYNC_V2:{TYPE: 'policysyncv2', MAX_LIMIT: -1},
    USERSYNC:{TYPE: 'usersync', MAX_LIMIT: 1},
    SAML : {TYPE: 'saml', MAX_LIMIT: 1},
    PEG: {TYPE: 'peg', MAX_LIMIT: 1},
    PKAFKA: {TYPE: 'pkafka', MAX_LIMIT: 1},
    //Discovery
    HDFS: {TYPE: 'hdfs', isSentToScan: true, MAX_LIMIT: -1},
    HIVE: {TYPE: 'hive', isSentToScan: false, MAX_LIMIT: -1},
    HBASE: {TYPE: 'hbase', isSentToScan: false, MAX_LIMIT: -1},
    KAFKA: {TYPE: 'kafka', isSentToScan: false, MAX_LIMIT: -1},
    LFS: {TYPE: 'lfs', isSentToScan: true, MAX_LIMIT: -1},
    CASSANDRA: {TYPE: 'cassandra', isSentToScan: false, MAX_LIMIT: -1},
    JDBC: {TYPE: 'jdbc', isSentToScan: false, MAX_LIMIT: -1},
    AWS_S3: {TYPE: 'aws_s3', isSentToScan: false, MAX_LIMIT: -1}, //change isSentToScan: true
    GOOGLE_CLOUD_STORAGE: {LABEL: 'Google Cloud Storage', TYPE: 'google_cloud_storage', uniqueCode: 'gcs', isSentToScan: true, MAX_LIMIT: -1},
    GOOGLE_BIG_QUERY: {LABEL: 'Google Big Query', TYPE: 'google_big_query', uniqueCode: 'gbq', isSentToScan: false, MAX_LIMIT: -1},
    GOOGLE_BIG_TABLE: {LABEL: 'Google Big Table', TYPE: 'google_big_table', uniqueCode: 'gbt', isSentToScan: false, MAX_LIMIT: -1},
    AWS_DYNAMO_DB: {TYPE: 'aws_dynamo_db', isSentToScan: false, MAX_LIMIT: -1},
    AZURE_COSMOS_DB: {TYPE: 'cosmos_db', isSentToScan: false, MAX_LIMIT: -1},
    AZURE_ADLS: {TYPE: 'azure_adls', isSentToScan: false, MAX_LIMIT: -1},
    DATABRICKS_SPARK_SQL: {TYPE: 'databricks_spark_sql', isSentToScan: false, MAX_LIMIT: -1},
    DATABRICKS_UNITY_CATALOG_SQL: {TYPE: 'databricks_unity_catalog_sql', isSentToScan: false, MAX_LIMIT: -1},
    DATABRICKS_SQL: {TYPE: 'databricks_sql', isSentToScan: false, MAX_LIMIT: -1},
    SNOWFLAKE_SQL: {TYPE: 'snowflake_sql', isSentToScan: false, MAX_LIMIT: -1},
    PRESTO_SQL: {TYPE: 'presto_sql', isSentToScan: false, MAX_LIMIT: -1},
    ORACLE_SQL: {TYPE: 'oracle_sql', isSentToScan: false, MAX_LIMIT: -1},
    MYSQL_SQL: {TYPE: 'mysql_sql', isSentToScan: false, MAX_LIMIT: -1},
    CASSANDRA_SQL: {TYPE: 'cassandra_sql', isSentToScan: false, MAX_LIMIT: -1},
    TRINO_SQL: {TYPE: 'trino_sql', isSentToScan: false, MAX_LIMIT: -1},
    MSSQL_SQL: {TYPE: 'mssql_sql', isSentToScan: false, MAX_LIMIT: -1},
    REDSHIFT_SQL: {TYPE: 'redshift_sql', isSentToScan: false, MAX_LIMIT: -1},
    POSTGRES_SQL: {TYPE: 'postgres_sql', isSentToScan: false, MAX_LIMIT: -1},
}

const APPLICATION_KIND_TYPE = {
    FS: [APPLICATION_TYPE.HDFS.TYPE, APPLICATION_TYPE.LFS.TYPE, APPLICATION_TYPE.AWS_S3.TYPE, APPLICATION_TYPE.AZURE_ADLS.TYPE, APPLICATION_TYPE.GOOGLE_CLOUD_STORAGE.TYPE],
    DB_TABLE: [
        APPLICATION_TYPE.HIVE.TYPE, APPLICATION_TYPE.DATABRICKS_SQL.TYPE, APPLICATION_TYPE.SNOWFLAKE_SQL.TYPE, APPLICATION_TYPE.PRESTO_SQL.TYPE, 
        APPLICATION_TYPE.ORACLE_SQL.TYPE, APPLICATION_TYPE.MYSQL_SQL.TYPE, APPLICATION_TYPE.CASSANDRA_SQL.TYPE, APPLICATION_TYPE.TRINO_SQL.TYPE,
        APPLICATION_TYPE.HBASE.TYPE, APPLICATION_TYPE.CASSANDRA.TYPE,
        APPLICATION_TYPE.AWS_DYNAMO_DB.TYPE, APPLICATION_TYPE.AZURE_COSMOS_DB.TYPE, APPLICATION_TYPE.JDBC.TYPE, APPLICATION_TYPE.GOOGLE_BIG_TABLE.TYPE, 
        APPLICATION_TYPE.DATABRICKS_SPARK_SQL.TYPE, APPLICATION_TYPE.DATABRICKS_UNITY_CATALOG_SQL.TYPE, APPLICATION_TYPE.GOOGLE_BIG_QUERY.TYPE, APPLICATION_TYPE.MSSQL_SQL.TYPE, APPLICATION_TYPE.REDSHIFT_SQL.TYPE,
        APPLICATION_TYPE.POSTGRES_SQL.TYPE, APPLICATION_TYPE.GOOGLE_BIG_QUERY.TYPE
    ]
}

const RESOURCE_BY = {
    PATH: {name: 'path'},
    DATABASE: {name: 'database'},
    TABLE: {name: 'table'},
    COLUMN: {name: 'column'},
    TOPIC: {name: 'topic'},
    FIELD: {name: 'field'},
    SERVICE_ID: {name: 'projectId'}
}

const RESOURCE_SERVICE = {
    HDFS: {name: 'hdfs', resource: {PATH: RESOURCE_BY.PATH}, pattern: /[^A-Za-z0-9-._/\[\]/=*\s:/\\]/g},
    HIVE: {name: 'hive', resource: {DATABASE: RESOURCE_BY.DATABASE, TABLE: RESOURCE_BY.TABLE, COLUMN: RESOURCE_BY.COLUMN}, pattern: /[^A-Za-z0-9-._*]/g},
    AWSS3: {name: 's3', resource: {PATH: RESOURCE_BY.PATH}, pattern: /[^A-Za-z0-9-._/\[\]/=*\s:/\\]/g},
    HBASE: {name: 'hbase', resource: {DATABASE: RESOURCE_BY.DATABASE, TABLE: RESOURCE_BY.TABLE, COLUMN: RESOURCE_BY.COLUMN}, pattern: /[^A-Za-z0-9-._*]/g},
    KAFKA: {name: 'kafka', resource: {TOPIC: RESOURCE_BY.TOPIC, FIELD: RESOURCE_BY.FIELD}, pattern: /[^A-Za-z0-9-._*]/g},
    CASSANDRA: {name: 'cassandra', resource: {DATABASE: RESOURCE_BY.DATABASE, TABLE: RESOURCE_BY.TABLE, COLUMN: RESOURCE_BY.COLUMN}, pattern: /[^A-Za-z0-9-._*]/g},
    AWS_DYNAMO_DB: {name: 'aws_dynamo_db', resource: {DATABASE: RESOURCE_BY.DATABASE, TABLE: RESOURCE_BY.TABLE, COLUMN: RESOURCE_BY.COLUMN}, pattern: /[^A-Za-z0-9-._*]/g},
    JDBC: {name: 'jdbc', resource: {DATABASE: RESOURCE_BY.DATABASE, TABLE: RESOURCE_BY.TABLE, COLUMN: RESOURCE_BY.COLUMN}, pattern: /[^A-Za-z0-9-._*]/g},
    AZURE_ADLS_GEN1: {name: 'adls_gen1', resource: {PATH: RESOURCE_BY.PATH}, pattern: /[^A-Za-z0-9-._/\[\]/=*\s:/\\]/g},
    AZURE_ADLS_GEN2: {name: 'adls_gen2', resource: {PATH: RESOURCE_BY.PATH}, pattern: /[^A-Za-z0-9-._/\[\]/=*\s:/\\]/g},
    AZURE_ADLS_BLOB: {name: 'adls_blob', resource: {PATH: RESOURCE_BY.PATH}, pattern: /[^A-Za-z0-9-._/\[\]/=*\s:/\\]/g},
    AZURE_ADLS: {name: 'azure_adls', resource: {PATH: RESOURCE_BY.PATH}, pattern: /[^A-Za-z0-9-._/\[\]/=*\s:/\\]/g},
    GOOGLE_CLOUD_STORAGE: {name: 'google_cloud_storage', resource: {PATH: RESOURCE_BY.PATH, SERVICE_ID: RESOURCE_BY.SERVICE_ID}, pattern: /[^A-Za-z0-9-._/\[\]/=*\s:/\\]/g},
    GOOGLE_BIG_QUERY: {name: 'google_big_query', resource: {DATABASE: RESOURCE_BY.DATABASE, TABLE: RESOURCE_BY.TABLE, COLUMN: RESOURCE_BY.COLUMN, SERVICE_ID: RESOURCE_BY.SERVICE_ID}, pattern: /[^A-Za-z0-9-._*]/g},
    AZURE_COSMOS_DB: {name: 'azure_cosmos_db', resource: {DATABASE: RESOURCE_BY.DATABASE, TABLE: RESOURCE_BY.TABLE, COLUMN: RESOURCE_BY.COLUMN}, pattern: /[^A-Za-z0-9-._*]/g},
    COSMOS_DB: {name: 'azure_cosmos_db', resource: {DATABASE: RESOURCE_BY.DATABASE, TABLE: RESOURCE_BY.TABLE, COLUMN: RESOURCE_BY.COLUMN}, pattern: /[^A-Za-z0-9-._*]/g},
    DATABRICKS_SPARK_SQL: {name: 'databricks_spark_sql', resource: {DATABASE: RESOURCE_BY.DATABASE, TABLE: RESOURCE_BY.TABLE, COLUMN: RESOURCE_BY.COLUMN}, pattern: /[^A-Za-z0-9-._*]/g},
    DATABRICKS_SQL: {name: 'databricks_sql', resource: {DATABASE: RESOURCE_BY.DATABASE, TABLE: RESOURCE_BY.TABLE, COLUMN: RESOURCE_BY.COLUMN}, pattern: /[^A-Za-z0-9-._*]/g},
    DATABRICKS_UNITY_CATALOG_SQL: {name: 'databricks_unity_catalog_sql', resource: {DATABASE: RESOURCE_BY.DATABASE, TABLE: RESOURCE_BY.TABLE, COLUMN: RESOURCE_BY.COLUMN}, pattern: /[^A-Za-z0-9-._*]/g},
    SNOWFLAKE_SQL: {name: 'snowflake_sql', resource: {DATABASE: RESOURCE_BY.DATABASE, TABLE: RESOURCE_BY.TABLE, COLUMN: RESOURCE_BY.COLUMN}, pattern: /[^A-Za-z0-9-._*]/g},
    PRESTO_SQL: {name: 'presto_sql', resource: {DATABASE: RESOURCE_BY.DATABASE, TABLE: RESOURCE_BY.TABLE, COLUMN: RESOURCE_BY.COLUMN}, pattern: /[^A-Za-z0-9-._*]/g},
    ORACLE_SQL: {name: 'oracle_sql', resource: {DATABASE: RESOURCE_BY.DATABASE, TABLE: RESOURCE_BY.TABLE, COLUMN: RESOURCE_BY.COLUMN}, pattern: /[^A-Za-z0-9-._*]/g},
    MYSQL_SQL: {name: 'mysql_sql', resource: {DATABASE: RESOURCE_BY.DATABASE, TABLE: RESOURCE_BY.TABLE, COLUMN: RESOURCE_BY.COLUMN}, pattern: /[^A-Za-z0-9-._*]/g},
    CASSANDRA_SQL: {name: 'cassandra_sql', resource: {DATABASE: RESOURCE_BY.DATABASE, TABLE: RESOURCE_BY.TABLE, COLUMN: RESOURCE_BY.COLUMN}, pattern: /[^A-Za-z0-9-._*]/g},
    TRINO_SQL: {name: 'trino_sql', resource: {DATABASE: RESOURCE_BY.DATABASE, TABLE: RESOURCE_BY.TABLE, COLUMN: RESOURCE_BY.COLUMN}, pattern: /[^A-Za-z0-9-._*]/g},
    MSSQL_SQL: {name: 'mssql_sql', resource: {DATABASE: RESOURCE_BY.DATABASE, TABLE: RESOURCE_BY.TABLE, COLUMN: RESOURCE_BY.COLUMN}, pattern: /[^A-Za-z0-9-._*]/g},
    REDSHIFT_SQL: {name: 'redshift_sql', resource: {DATABASE: RESOURCE_BY.DATABASE, TABLE: RESOURCE_BY.TABLE, COLUMN: RESOURCE_BY.COLUMN}, pattern: /[^A-Za-z0-9-._*]/g},
    POSTGRES_SQL: {name: 'postgres_sql', resource: {DATABASE: RESOURCE_BY.DATABASE, TABLE: RESOURCE_BY.TABLE, COLUMN: RESOURCE_BY.COLUMN}, pattern: /[^A-Za-z0-9-._*]/g},
    VERTICA_SQL: {name: 'vertica_sql', resource: {DATABASE: RESOURCE_BY.DATABASE, TABLE: RESOURCE_BY.TABLE, COLUMN: RESOURCE_BY.COLUMN}, pattern: /[^A-Za-z0-9-._*]/g}
}

const FILE_EXPLORER_APPS = [
    RESOURCE_SERVICE.AWSS3.name,
    RESOURCE_SERVICE.GOOGLE_CLOUD_STORAGE.name,
    RESOURCE_SERVICE.AZURE_ADLS.name,
    RESOURCE_SERVICE.AZURE_ADLS_GEN1.name,
    RESOURCE_SERVICE.AZURE_ADLS_GEN2.name,
    RESOURCE_SERVICE.AZURE_ADLS_BLOB.name
]

const BULK_DELETE_STATUS = {
    PARTIAL_DELETED: {label: 'Partial Deleted'},
    ALL_DELETED: {label: 'All Deleted'},
    ACCESS_DENIED: {label: 'Access Denied'}
}

const UNIX_SYMBOLIC_PERMISSION = {
    NONE: "---",
    EXECUTE: "--x",
    WRITE: "-w-",
    WRITE_EXECUTE: "-wx",
    READ: "r--",
    READ_EXECUTE: "r-x",
    READ_WRITE: "rw-",
    ALL: "rwx"
}

const PERMISSIONS = {
    READ: 'read',
    UPDATE: 'update',
    DELETE: 'delete',
    EXPORT: 'export'
}

const COLORPALETTE = ['#5FC8FF', '#75A9F9', '#FF6E6E', '#63AABC', '#60204B',
    '#F3A953', '#FF82C3', '#cc7a00', '#009975', '#FF6337',
    '#002F35', '#4592AF', '#FF8246', '#A34A28', '#6C5CE7',
    '#40A798', '#33313B', '#D25959', '#F18C8E', '#DAA592',
    '#6B8C42', '#8D309B', '#A2A8D3', '#38598B', '#8186D5',
    '#007880', '#AAAAAA', '#1F3C88', '#5D3A3A', '#F67280',
    '#738598', '#1CB3C8', '#913535', '#5D5D5A', '#5C8D89',
    '#9873B9', '#B55400', '#3161A3', '#C7004C', '#27AA80',
    '#AFA939', '#B96B9F','#2f7ed8', '#0d233a', '#8bbc21',
    '#910000', '#1aadce','#492970', '#f28f43', '#77a1e5',
    '#c42525', '#a6c96a','#7D91BC','#DDA11D', '#897B51',
    '#FF7F60' , '#96AFB8', '#7C58A4' , '#a7ecdf' , '#388883',
    '#AD7C7E' , '#005C81','#1f77b4','#aec7e8','#ff7f0e',
    '#ffbb78',' #2ca02c','#98df8a','#d62728','#ff9896',
    '#9467bd',' #c5b0d5','#8c564b','#c49c94','#e377c2',
    '#f7b6d2',' #7f7f7f','#c7c7c7','#bcbd22','#dbdb8d',
    '#17becf',' #9edae5','#E9005B','#434271','#9EF8B3',
    '#85A2CF',' #2F4858', '#fbb4ae' , '#b3cde3', '#ccebc5',
    '#decbe4', '#fed9a6', '#ffffcc', '#e5d8bd', '#fddaec',
    '#f2f2f2'
];

const REGEX = {
    EMAIL: /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/,
    ACCOUNT_NAME: /^[a-z0-9\d-_]+$/i,
    RANGER_USERNAME: /^([A-Za-z0-9_]|[\u00C0-\u017F])([a-z0-9,._\-+/@= ]|[\u00C0-\u017F])+$/i,
    FIRSTNAME : /^([A-Za-z0-9_]|[\u00C0-\u017F])([a-zA-Z0-9\s_. -@]|[\u00C0-\u017F])+$/i,
    LASTNAME : /^([A-Za-z0-9_]|[\u00C0-\u017F])([a-zA-Z0-9\s_. -@]|[\u00C0-\u017F])+$/i,
    // PHONE_NUMBER: /^\(?([0-9]{3})\)?[]?([0-9]{3})[]?([0-9]{4}|[0-9]{3})$/,
    PHONE_NUMBER: /^[0-9]+$/,
    COUNTRY_CODE: /^(\+?\d{1,3}|\d{1,4})$/,
    PASSWORD: /^(?=.*?[A-Z])(?=.*?[0-9]).{8,20}$/,
    COMPANY_NAME : /^(?!\s)(?!.*\s$)(?=.*[a-zA-Z0-9])[a-zA-Z0-9 '~?!._&,()\-]{2,}$/,
    NAME : /^[a-zA-Z][a-zA-Z0-9\s\-\' ]*$/,
    IP_ADDRESS: /((^\s*((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))\s*$)|(^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$))/,
    IPV4_ADDRESS: /^(((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))(\/[0-9]{1,3})?$/,
    IPV6_ADDRESS: /^(((([0-9a-fA-F]){0,4})\:){1,7}([0-9a-fA-F]){0,4})(\/[0-9]{1,3})?$/,
    //Discovery Regex
    HDFS_APP_NAME: /hdfs/gi,
    HBASE_APP_NAME: /hbase/gi,
    S3_APP_NAME: /s3/gi,
    HIVE_APP_NAME: /hive/gi,
    KAFKA_APP_NAME: /kafka/gi,
    CASSANDRA_APP_NAME: /cassandra/gi,
    AWS_DYNAMO_DB_APP_NAME: /aws_dynamo_db/gi,
    AZURE_COSMOS_DB_APP_NAME: /azure_cosmos_db/gi,
    JDBC_APP_NAME: /jdbc/gi,
    DATABRICKS_APP_NAME: /databricks_sql/gi,
    SNOWFLAKE_APP_NAME: /snowflake_sql/gi,
    PRESTO_APP_NAME: /presto_sql/gi,
    MYSQL_APP_NAME: /mysql_sql/gi,
    MSSQL_APP_NAME: /mssql_sql/gi,
    ORACLE_APP_NAME: /oracle_sql/gi,
    TRINO_APP_NAME: /trino/gi,
    GOOGLE_BIG_QUERY: /google_big_query/gi,
    ADLS_APP_NAME: /adls/gi,
    HIVE_RESOURCE_NAME: /^[A-Za-z0-9-._*]/g,
    TAG_DEF: /^[A-Z]+[A-Z0-9._\s]*$/,
    SEARCH_BY_LOCATION: /[^A-Za-z0-9-._/\[\]/=\s:/\\]/g,
    ONLY_NUMBERS: /^\d+$/,
    REDSHIFT_APP_NAME: /redshift_sql/gi,
    POSTGRES_APP_NAME: /postgres_sql/gi,
    ONLY_ASCII_CHARACTERS: /^[\x00-\x7F]*$/,
    DOT_INDEX_DOT: /\.[0-9]+\./g,
    UNDERSCORE_INDEX_DOT: /\_[0-9]+\./g,
    ESCAPE_SPECIAL_CHAR: /\\|]|[*]|[(]|[)]|[+]|[{]|[}]|[[]|[?]/g,
    DATABRICKS_UNITY_CATALOG_APP_NAME: /databricks_unity_catalog_sql/gi,
    GROUP_NAME_REGEX : /^([A-Za-z0-9_]|[\u00C0-\u017F])([a-z0-9,:._\-+/@= ]|[\u00C0-\u017F])+$/i,
    ROLE_NAME_REGEX :  /^([A-Za-z0-9_]|[\u00C0-\u017F])([a-z0-9,._\-+/@= ]|[\u00C0-\u017F])+$/i,
    PORTAL_EMAIL_REGEX: /^[\w]([\-\.\w\+])+@[\w]+[\w\-]+[\w]*\.([\w]{1,6}(\.[a-z][a-z|0-9]*){0,4}?)$/
}

const CLOUD_SERVICE = {
    AWS: {NAME: 'aws', LABEL: 'AWS'},
    AZURE: {NAME: 'azure', LABEL: 'AZURE'},
    GCP: {NAME: 'gcp', LABEL: 'GCP'},
    NONE: {NAME: 'none', LABEL: 'NONE'}
}

const TOKEN_STATUS = {
    ENABLED: {VALUE: 'ENABLED', LABEL: 'Enable', bsStyle: 'warning'},
    DISABLED: {VALUE: 'DISABLED', LABEL: 'Inactive', bsStyle: 'default'},
    REVOKED: {VALUE: 'REVOKED', LABEL: 'Revoked', bsStyle: 'default'},
    DELETED: {VALUE: 'DELETED', LABEL: 'Deleted', bsStyle: 'danger'},
    EXPIRED: {VALUE: 'EXPIRED', LABEL: 'Expired', bsStyle: 'danger'},
    ACTIVATED: {VALUE: 'ACTIVATED', LABEL: 'Active', bsStyle: 'success'}
}

const NETWORK_ERROR = 'Network Error';
const NETWORK_ERROR_MESSAGE = "A network error occurred. This could be a CORS issue or a dropped internet connection. It is not possible for us to know";

const SEARCH_OPERATORS = {
    INCLUDE_LIST: ['==', 'is'],
    EXCLUDE_LIST: ['!=', 'is not']
}

const USER_ACCOUNT_PERMISSIONS = {
    READ: {NAME: 'READ'},
    READ_WRITE: {NAME: 'READ_WRITE'}
}

const FIELDS_STR = {
    DATAZONE_STR: 'datazones_str',
    APP_NAME: 'app_name',
    APP_CODE: 'app_code',
    ALL_TAGS_STR: 'all_tags_str',
    TAGGED_TAGS_STR: 'tagged_tags_str'
}

const SCHEDULE_TYPE = {
    MINUTES: {name: 'Minutes', value: 'MINUTES'},
    HOURLY: {name: 'Hourly', value: 'HOURLY'},
    ONCE: {name: 'Once', value: 'ONCE'},
    DAILY: {name: 'Daily', value: 'DAILY'},
    WEEKLY: {name: 'Weekly', value: 'WEEKLY'},
    MONTHLY: {name: 'Monthly', value: 'MONTHLY'}
}

const SEARCH_TYPE = {
    PARTIAL_MATCH: {value: 'partial_match', label: 'Partial Match'},
    EXACT_MATCH: {value: 'exact_match', label: 'Exact Match'}
};

const STRING_OPERATORS = {
    EQUALS: { label: 'Equals', value: 'eq' },
    STARTS_WITH: { label: 'Starts with', value: 'sw' }
}

const DISABLED_TXT = ' (Disabled)';

export {
    STORE_CONFIG,
    DATE_TIME_FORMATS,
    STATUS,
    DEFAULTS,
    ROWS_PER_PAGE,
    APPLICATION_TYPE,
    APPLICATION_KIND_TYPE,
    RESOURCE_BY,
    RESOURCE_SERVICE,
    BULK_DELETE_STATUS,
    UNIX_SYMBOLIC_PERMISSION,
    PERMISSIONS,
    COLORPALETTE,
    REGEX,
    CLOUD_SERVICE,
    TOKEN_STATUS,
    DEFAULT_FIELD_MAX_LENGTH,
    DEFAULT_PAGE_SIZE,
    DEFAULT_LOOKUP_PAGE_SIZE,
    MAX_PAGE_SIZE,
    READ_FILESIZE,
    DOWNLOAD_FILESIZE,
    UPLOAD_FILESIZE,
    RESOURCE_SPLIT_JOIN_BY,
    FILESIZE,
    EXPORT_CSV_DEFAULT_ROWS,
    DEFAULT_DATASERVER_REQUEST_CREDIT,
    OFFLINE_REPORTS_DEFAULT_THRESHOLD,
    MAX_PAGINATION_LIMIT,
    SEARCH_TXT,
    AUTO_HIDE_DURATION,
    SUPPORT_LOG_DOWNLOAD_MAX_DAYS,
    NETWORK_ERROR,
    NETWORK_ERROR_MESSAGE,
    FILE_EXPLORER_APPS,
    SEARCH_OPERATORS,
    USER_ACCOUNT_PERMISSIONS,
    FIELDS_STR,
    SCHEDULE_TYPE,
    SEARCH_TYPE,
    STRING_OPERATORS,
    DISABLED_TXT
}