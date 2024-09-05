import BaseStore from './base_store';
import MAiPolices from '../models/m_ai_policies';

class AiPoliciesStore extends BaseStore {
	constructor() {
		super({
				type: 'ai_policies',
				baseUrl: 'governance-service/api/ai/application',
		});
	}

	getGlobalPermissionPolicy(appId, opts={}) {
		opts.path = `/${appId}/config`;
		opts.recordMapper = (json) => new MAiPolices(json);
		return this.fetch('', opts);
	}

	updateGlobalPermissionPolicy(appId, data, opts = {}) {
		opts.path = `/${appId}/config`;
		opts.recordMapper = (json) => new MAiPolices(json);
		return this.update('', data, opts);
	}

	getAllPolicies(appId, opts = {}) {
		opts.path = `/${appId}/policy`;
		opts.deserialize = (resp) => {
			let {content, ...page} = resp
            this.page = page;
            return content;
        }
		opts.recordMapper = (json) => new MAiPolices(json);
		return this.fetchAll('', opts);
	}

	getPolicyById(appId, id, opts = {}) {
        opts.path = `/${appId}/policy`;
        opts.recordMapper = (json) => new MAiPolices(json);
        return this.fetch(id, opts);
    }

	createPolicy(appId, data, opts={}) {
		opts.path = `/${appId}/policy`;
		opts.recordMapper = (json) => new MAiPolices(json);
		opts.transformPayload = (data) => {
            data.id = undefined;
            return data
        }
        return this.create(data, opts);
	}

	updatePolicy(id, appId, data, opts = {}) {
        opts.path= `/${appId}/policy/${id}`;
        opts.recordMapper = (json) => new MAiPolices(json);

        return this.update('', data, opts);
    }

	deletePolicy(id, appId, opts = {}) {
        opts.path= `/${appId}/policy`;
        return this.delete(id, opts);
    }

}

const aiPoliciesStore = new AiPoliciesStore();
export default aiPoliciesStore;