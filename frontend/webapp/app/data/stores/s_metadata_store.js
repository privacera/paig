import BaseStore from "./base_store";
import MMetaData from "../models/m_metadata";

class MetaDataStore extends BaseStore {
  constructor() {
    super({
      type: "Vector DB Metadata",
      baseUrl: "account-service/api/vectordb/metadata/key"
    });
  }
  fetchMetaData(opts = {}) {
    opts.recordMapper = (json) => new MMetaData(json);
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

  createMetaData(data, opts = {}) {
    opts.recordMapper = (json) => new MMetaData(json);
    return this.create(data, opts);
  }
  updateMetaData(data, opts = {}) {
    opts.recordMapper = (json) => new MMetaData(json);
    return this.update(data.id, data, opts);
  }
  deleteMetaData(id, opts = {}) {
    opts.recordMapper = (json) => new MMetaData(json);
    return this.delete(id, opts);
  }
}

const metaDataStore = new MetaDataStore();
export default metaDataStore;
