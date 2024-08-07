import FSBaseModel from "common-ui/data/models/base_model";
import { observable } from "mobx";

class MetaData extends FSBaseModel {
  @observable name = null;
  @observable description = null;
  constructor(props = {}, opts = {}) {
    super(props, opts);
    Object.assign(this, props);
  }
}

export default MetaData;
