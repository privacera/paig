import BaseStore from './base_store';
import MGuardrail from '../models/m_guardrail';

class GuardrailStore extends BaseStore {
    constructor() {
        super({
            type: 'user',
            baseUrl: 'guardrail-service/api/guardrail',
        });
    }

    searchGuardrail(opts = {}) {
        opts.deserialize = (resp) => {
            let {content, ...page} = resp
            this.page = page;
            return content;
        }
        opts.recordMapper = (json) => new MGuardrail(json);
        return this.fetchAll(null, opts);
    }

    getGuardrail(id, opts = {}) {
        opts.recordMapper = (json) => new MGuardrail(json);
        return this.fetch(id, opts);
    }

    createGuardrail(data , opts = {}) {
        opts.recordMapper = (json) => new MGuardrail(json);
        opts.transformPayload = (data) => {
            return data
        }
        return this.create(data, opts);
    }

    updateGuardrail(id, data, opts = {}) {
        opts.recordMapper = (json) => new MGuardrail(json);
        return this.update(id, data, opts);
    }

    deleteGuardrail(id, opts = {}) {
        return this.delete(id, opts);
    }
}

const guardrailStore = new GuardrailStore();
export default guardrailStore;