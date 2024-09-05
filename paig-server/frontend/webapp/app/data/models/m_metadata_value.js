import { observable } from 'mobx';

import FSBaseModel from 'common-ui/data/models/base_model';

class MetaDataValue extends FSBaseModel {
  @observable metadataValue;
  constructor(props = {}, opts = {}) {
    super(props, opts);
    Object.assign(this, props);
  }
}

export default MetaDataValue;