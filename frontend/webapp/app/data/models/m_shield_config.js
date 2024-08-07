import FSBaseModel from "common-ui/data/models/base_model";

class MShieldConfig extends FSBaseModel {
  constructor(props = {}, opts = {}) {
    super(props, opts);
    Object.assign(this, props);
  }
}

export default MShieldConfig;