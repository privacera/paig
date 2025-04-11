import BaseStore from './base_store';
import VAiApplicationApiKey from '../models/m_ai_application_api_key';

class AIApplicationApiKeyStore extends BaseStore {
  constructor() {
    let baseUrl = 'account-service/api/apikey';
    super({
      type: 'ai_application_api_key',
      baseUrl
    });
    this.baseUrl = baseUrl;
  }
  generateApiKey(data, opts = {}) {
    opts.path = `v2/generate`;
    opts.recordMapper = (json) => new VAiApplicationApiKey(json);
    return this.create(data, opts);
  }
  getApiKey(opts = {}) {
    opts.path = `/application/getKeys`;
    opts.deserialize = (resp) => {
      let {content, ...page} = resp
      this.page = page;
      return content;
    }
    opts.recordMapper = (json) => new VAiApplicationApiKey(json);
    return this.fetchAll("", opts);
  }
  deleteApiKey(id, opts = {}) {
    return this.delete(id, opts);
  }
  revokeApiKey(id, opts = {}) {
    opts.path = `/disableKey`;
    return this.update(id, {}, opts);
  }
}

const aiApplicationApiKeyStore = new AIApplicationApiKeyStore();
export default aiApplicationApiKeyStore;