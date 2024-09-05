import BaseStore from "./base_store";
import MSensitiveData from "../models/m_sensitive_data";

class SensitiveDataStore extends BaseStore {
  constructor() {
    super({
      type: "Tags",
      baseUrl: "account-service"
    });
  }
  fetchSensitiveData(opts = {}) {
    opts.path = "api/tags";
    opts.recordMapper = (json) => new MSensitiveData(json);
    opts.deserialize = (resp) => {
      let { content, ...page } = resp;
      content.forEach((item, i) => {
        if (!item.id) {
          item.id = i;
        }
      })
      this.page = page;
      return content;
    };

    return this.fetchAll("", opts);
  }
}

const sensitiveDataStore = new SensitiveDataStore();
export default sensitiveDataStore;
