import BaseStore from './base_store';
import MVectorDBPolicy from '../models/m_vector_db_policy';

class VectorDBPolicyStore extends BaseStore {
	constructor() {
		super({
			type: 'vector_db_policy',
			baseUrl: 'governance-service/api/ai/vectordb',
		});
	}

	getGlobalPermissionPolicy(appId, opts={}) {
		opts.path = `/${appId}/config`;
		opts.recordMapper = (json) => new MVectorDBPolicy(json);
		return this.fetch('', opts);
	}

	updateGlobalPermissionPolicy(appId, data, opts = {}) {
		opts.path = `/${appId}/config`;
		opts.recordMapper = (json) => new MVectorDBPolicy(json);
		return this.update('', data, opts);
	}

	getAllPolicies(appId, opts = {}) {
		opts.path = `/${appId}/policy`;
		opts.deserialize = (resp) => {
			let {content, ...page} = resp
            this.page = page;
            return content;
        }
		opts.recordMapper = (json) => new MVectorDBPolicy(json);
		return this.fetchAll('', opts);
	}

	getPolicyById(appId, id, opts = {}) {
        opts.path = `/${appId}/policy`;
        opts.recordMapper = (json) => new MVectorDBPolicy(json);
        return this.fetch(id, opts);
    }

	createPolicy(appId, data, opts={}) {
		opts.path = `/${appId}/policy`;
		opts.recordMapper = (json) => new MVectorDBPolicy(json);
		opts.transformPayload = (data) => {
            data.id = undefined;
            return data
        }
        return this.create(data, opts);
	}

	updatePolicy(id, appId, data, opts = {}) {
        opts.path= `/${appId}/policy/${id}`;
        opts.recordMapper = (json) => new MVectorDBPolicy(json);

        return this.update('', data, opts);
    }

	deletePolicy(id, appId, opts = {}) {
        opts.path= `/${appId}/policy`;
        return this.delete(id, opts);
    }

}

const vectorDBPolicyStore = new VectorDBPolicyStore();
export default vectorDBPolicyStore;