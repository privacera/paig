import BaseStore from './base_store';
import MGuardrailConnection from '../models/m_guardrail_connection';

class GuardrailConnectionProviderStore extends BaseStore {
    constructor() {
        super({
            type: 'guardrailConnection',
            baseUrl: 'guardrail-service/api',
        });
    }

    getConnectedGuardrailProvider(opts = {}) {
        opts.path = 'connection_providers';
        opts.recordMapper = (json) => new Object(json);
        return this.fetchAll(null, opts);
    }

    guardrailProviderConnectionTest(data, opts = {}) {
        opts.path = 'connection/test';
        opts.recordMapper = (json) => new MGuardrailConnection(json);
        return this.create(data, opts);
    }

    searchGuardrailConnectionProvider(opts = {}) {
        opts.path = 'connection';
        opts.deserialize = (resp) => {
            let {content, ...page} = resp
            this.page = page;
            return content;
        }
        opts.recordMapper = (json) => new MGuardrailConnection(json);
        return this.fetchAll(null, opts);
    }

    createGuardrailConnectionProvider(data, opts = {}) {
        opts.path = 'connection';
        opts.recordMapper = (json) => new MGuardrailConnection(json);
        opts.transformPayload = (data) => {
            return data
        }
        return this.create(data, opts);
    }

    updateGuardrailConnectionProvider(id, data, opts = {}) {
        opts.path = 'connection';
        opts.recordMapper = (json) => new MGuardrailConnection(json);
        return this.update(id, data, opts);
    }

    deleteGuardrailConnectionProvider(id, opts = {}) {
        opts.path = 'connection';
        return this.delete(id, opts);
    }
}

const guardrailConnectionProviderStore = new GuardrailConnectionProviderStore();
export default guardrailConnectionProviderStore;