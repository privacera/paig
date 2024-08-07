import generalStore from 'data/stores/s_general_store';
import userStore from 'data/stores/s_user_store';
import groupStore from 'data/stores/s_group_store';
import aiApplicationStore from 'data/stores/s_ai_application_store';
import aiPoliciesStore from 'data/stores/s_ai_policies_store';
import securityAuditsStore from 'data/stores/s_security_audits_store';
import sensitiveDataStore from 'data/stores/s_sensitive_data_store';
import adminAuditsStore from 'data/stores/s_admin_audits_store';
import encryptDecryptStore from 'data/stores/s_encypt_decypt_store';
import jobManagerStore from 'data/stores/s_job_manager_store';
import dashboardStore from 'data/stores/s_dashboard_store';
import publicStore from './s_public_store';
import shieldConfigStore from './s_shield_config_store';
import metaDataStore from './s_metadata_store';
import metaDataValuesStore from './s_metadata_values_store';
import vectorDBStore from './s_vector_db_store';
import vectorDBPolicyStore from './s_vector_db_policy_store';
import dataProtectStore from './s_data_protect_store';
import shieldAuditsReportsStore from './s_shield_audits_reports_store';

const stores = {
	generalStore,
	publicStore,
	shieldConfigStore,
	userStore,
	groupStore,
	aiApplicationStore,
	aiPoliciesStore,
	securityAuditsStore,
	sensitiveDataStore,
	adminAuditsStore,
	encryptDecryptStore,
	jobManagerStore,
	dashboardStore,
	metaDataStore,
	metaDataValuesStore,
	vectorDBStore,
	vectorDBPolicyStore,
	dataProtectStore,
	shieldAuditsReportsStore
}

export default stores;
