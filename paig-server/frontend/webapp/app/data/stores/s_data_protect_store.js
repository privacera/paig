import BaseStore from "./base_store";
import MToken from "../models/m_token";

class DataProtectStore extends BaseStore {
  constructor() {
    super({
      type: "data-protect",
      baseUrl: "account-service/api/data-protect"
    });
  }

  generateToken(data, opts = {}) {
    opts.path = 'token/generate';
    opts.recordMapper = (json) => new MToken(json);
    return this.create(data, opts);
  }
}

const dataProtectStore = new DataProtectStore();
export default dataProtectStore;