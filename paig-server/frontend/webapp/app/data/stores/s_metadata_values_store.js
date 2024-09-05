import BaseStore from "./base_store";
import MMetaDataValue from "../models/m_metadata_value";

class MetaDataValuesStore extends BaseStore {
  constructor() {
    super({
      type: "Vector DB Metadata",
      baseUrl: "account-service/api/vectordb/metadata/value"
    });
  }
  fetchMetaDataValues(opts = {}) {
    opts.recordMapper = (json) => new MMetaDataValue(json);
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

  createMetaDataValue(data, opts = {}) {
    opts.recordMapper = (json) => new MMetaDataValue(json);
    return this.create(data, opts);
  }
  updateMetaDataValue(data, opts = {}) {
    opts.recordMapper = (json) => new MMetaDataValue(json);
    return this.update(data.id, data, opts);
  }
  deleteMetaDataValue(id, opts = {}) {
    opts.recordMapper = (json) => new MMetaDataValue(json);
    return this.delete(id, opts);
  }
}

const metaDataValuesStore = new MetaDataValuesStore();
export default metaDataValuesStore;