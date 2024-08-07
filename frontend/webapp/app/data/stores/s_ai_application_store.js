import BaseStore from './base_store';
import VAIApplication from '../models/m_ai_application';

class AIApplicationStore extends BaseStore {
    constructor() {
        let baseUrl = 'governance-service/api/ai/application';
        super({
            type: 'ai_application',
            baseUrl
        });
        this.baseUrl = baseUrl;
    }
    getAIApplicationById(id, opts = {}) {
        opts.recordMapper = (json) => new VAIApplication(json);
        return this.fetch(id, opts);
    }
    getAIApplications(opts = {}) {
        opts.deserialize = (resp) => {
            let {content, ...page} = resp
            this.page = page;
            return content;
        }
        opts.recordMapper = (json) => new VAIApplication(json);
        return this.fetchAll('', opts);
    }
    createAIApplication(data, opts = {}) {
        opts.recordMapper = (json) => new VAIApplication(json);
        return this.create(data, opts);
    }
    updateAIApplication(data, opts = {}) {
        opts.recordMapper = (json) => new VAIApplication(json);
        return this.update(data.id, data, opts);
    }
    deleteAIApplication(id, opts = {}) {
        opts.recordMapper = (json) => new VAIApplication(json);
        return this.delete(id, opts);
    }
    getAIApplicationConfigUrl(id, opts = {}) {
        return this.baseUrl + `/${id}/config/json/download`;
    }
    downloadShieldConfig(opts = {}) {
        return this.baseUrl + `/shield/config/properties/download`;
    }
}

const aiApplicationStore = new AIApplicationStore();
export default aiApplicationStore;