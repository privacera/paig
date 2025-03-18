import BaseStore from './base_store';
import MGuardrailResponseTemplate from '../models/m_guardrail_response_template';

class GuardrailResponseTemplateStore extends BaseStore {
    constructor() {
        super({
            type: 'user',
            baseUrl: 'guardrail-service/api/response_templates',
        });
    }

    searchResponseTemplate(opts = {}) {
        opts.deserialize = (resp) => {
            let {content, ...page} = resp
            this.page = page;
            return content;
        }
        opts.recordMapper = (json) => new MGuardrailResponseTemplate(json);
        return this.fetchAll(null, opts);
    }

    createResponseTemplate(data , opts = {}) {
        opts.recordMapper = (json) => new MGuardrailResponseTemplate(json);
        opts.transformPayload = (data) => {
            return data
        }
        return this.create(data, opts);
    }

    updateResponseTemplate(id, data, opts = {}) {
        opts.recordMapper = (json) => new MGuardrailResponseTemplate(json);
        return this.update(id, data, opts);
    }

    deleteResponseTemplate(id, opts = {}) {
        return this.delete(id, opts);
    }
}

const guardrailResponseTemplateStore = new GuardrailResponseTemplateStore();
export default guardrailResponseTemplateStore;